"""Audited neural-only export helpers. No electrical data or device model is read."""
from __future__ import annotations

import gzip
import hashlib
from pathlib import Path
import struct

import numpy as np

SHAPES = ((128, 784), (64, 128), (10, 64))


def array_hash(a):
    a = np.ascontiguousarray(a)
    return hashlib.sha256(a.dtype.str.encode() + str(a.shape).encode() + a.tobytes()).hexdigest()


def quantized_layers(state, clips, weight_bits=4, activation_bits=8):
    """Port of the inspected Stage4A quantizer; NUS also checks its golden forward."""
    if len(clips) != 3 or not np.isfinite(clips).all() or min(clips) <= 0:
        raise ValueError('Require the three positive frozen activation clips')
    if (weight_bits, activation_bits) != (4, 8):
        raise ValueError('The first-run protocol is frozen to W4A8')
    if set(state) != {f'fc{i}.{k}' for i in range(1, 4) for k in ('weight', 'bias')}:
        raise ValueError('Checkpoint must be exactly the audited three-layer MLP')
    result = []
    for i, shape in enumerate(SHAPES, 1):
        w, bias = np.asarray(state[f'fc{i}.weight']), np.asarray(state[f'fc{i}.bias'])
        if w.shape != shape or bias.shape != (shape[0],):
            raise ValueError(f'FC{i} shape differs from the frozen 784-128-64-10 model')
        if w.dtype != np.float32 or bias.dtype != np.float32:
            raise ValueError('The audited checkpoint stores FP32 weights and biases')
        if not np.isfinite(w).all() or not np.isfinite(bias).all():
            raise ValueError('Non-finite checkpoint parameter')
        ws = max(float(np.abs(w).max()) / 7, 1e-12)
        wi = np.clip(np.rint(w.astype(np.float64) / ws), -7, 7).astype(np.int64)
        result.append({'weight': wi, 'weight_scale': ws, 'bias': bias.astype(np.float64),
                       'clip': float(clips[i-1]), 'activation_scale': float(clips[i-1]) / 255})
    return result


def forward_export(images, layers):
    images = np.asarray(images)
    if images.ndim != 3 or images.shape[1:] != (28, 28) or images.dtype != np.uint8:
        raise ValueError('Require MNIST uint8 images with shape [N,28,28]')
    # torchvision.ToTensor() first divides in float32, then the golden PTQ uses FP64.
    x = (images.reshape(len(images), 784).astype(np.float32) / np.float32(255)).astype(np.float64)
    inputs = []
    for i, layer in enumerate(layers):
        xi = np.clip(np.rint(x / layer['activation_scale']), 0, 255).astype(np.int64)
        inputs.append(xi)
        exact = xi @ layer['weight'].T
        x = exact.astype(np.float64) * (layer['activation_scale'] * layer['weight_scale']) + layer['bias']
        if i < 2:
            x = np.maximum(x, 0)
    return inputs, x


def validate_splits(splits, config):
    required = ('train', 'validation', 'calibration')
    if any(k not in splits for k in required):
        raise ValueError('Missing saved train/validation/calibration membership')
    parts = {}
    for key in required:
        values = np.asarray(splits[key])
        if values.ndim != 1 or values.dtype.kind not in 'iu' or len(np.unique(values)) != len(values):
            raise ValueError(f'Invalid or duplicate {key} IDs')
        if np.any(values < 0) or np.any(values >= 60000):
            raise ValueError('MNIST original-training parent ID outside 0..59999')
        parts[key] = values.astype(np.int64)
    if np.intersect1d(parts['train'], parts['validation']).size:
        raise ValueError('Training and validation parents overlap')
    if not np.isin(parts['calibration'], parts['train']).all():
        raise ValueError('Calibration parents must be in the saved training partition')
    if np.intersect1d(parts['calibration'], parts['validation']).size:
        raise ValueError('Calibration and development-evaluation parents overlap')
    perm = np.random.default_rng(int(config['split_seed'])).permutation(60000)
    nval, ncal = int(config['val_size']), int(config['calibration_size'])
    expected = {'validation': perm[:nval], 'train': perm[nval:], 'calibration': perm[nval:nval+ncal]}
    if any(not np.array_equal(parts[k], expected[k]) for k in required):
        raise ValueError('Saved membership/order differs from the frozen split seed/settings')
    return parts


def read_idx(path, expected_magic):
    path = Path(path)
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rb') as f:
        raw = f.read()
    if len(raw) < 8 or struct.unpack('>I', raw[:4])[0] != expected_magic:
        raise ValueError('Invalid MNIST IDX header')
    if expected_magic == 2051:
        if len(raw) < 16:
            raise ValueError('Truncated image header')
        _, n, rows, cols = struct.unpack('>IIII', raw[:16])
        if (rows, cols) != (28, 28) or len(raw) != 16 + n*rows*cols:
            raise ValueError('MNIST image dimensions/payload mismatch')
        return np.frombuffer(raw, np.uint8, offset=16).reshape(n, rows, cols).copy()
    if expected_magic != 2049:
        raise ValueError('Only MNIST image and label IDX are supported')
    _, n = struct.unpack('>II', raw[:8])
    if len(raw) != 8 + n:
        raise ValueError('MNIST label payload mismatch')
    labels = np.frombuffer(raw, np.uint8, offset=8).copy()
    if np.any(labels > 9):
        raise ValueError('MNIST label outside 0..9')
    return labels


def pack_weights(weight, row_start, weight_bits=4):
    """Pack [output,input] W4 into physical-position bookkeeping, never a circuit."""
    w = np.asarray(weight)
    if w.ndim != 2 or w.dtype.kind not in 'iu' or np.any(w < -8) or np.any(w > 7):
        raise ValueError('Require signed W4 integer weights [output,input]')
    if weight_bits != 4 or row_start < 0 or row_start % 256 or row_start >= w.shape[1]:
        raise ValueError('Invalid W4 row-block selection')
    nout, nin = w.shape
    nrows = min(256, nin-row_start)
    block = w[:, row_start:row_start+nrows].T
    packed = []
    for begin in range(0, nout*4, 256):
        columns = np.arange(begin, min(begin+256, nout*4))
        out = columns % nout
        bits = columns // nout
        matrix = np.zeros((256, 256), dtype=np.uint8)
        matrix[:nrows, :len(columns)] = ((block[:, out] >> bits[None, :]) & 1).astype(np.uint8)
        coeff = np.where(bits == 3, -8, 1 << bits)
        packed.append({'W': matrix, 'output_channels': out, 'weight_bits': bits,
                       'coefficients': coeff, 'used_columns': len(columns), 'used_rows': nrows,
                       'row_start': row_start, 'array_index': begin//256})
    return packed


def trace_planes(integer_inputs, parents, row_start):
    x = np.asarray(integer_inputs)
    ids = np.asarray(parents)
    if x.ndim != 2 or x.dtype.kind not in 'iu' or np.any(x < 0) or np.any(x > 255):
        raise ValueError('Require unsigned A8 integer inputs')
    if ids.shape != (len(x),) or len(np.unique(ids)) != len(ids):
        raise ValueError('Require one unique parent per image')
    if row_start < 0 or row_start % 256 or row_start >= x.shape[1]:
        raise ValueError('Invalid activation row block')
    nrows = min(256, x.shape[1]-row_start)
    padded = np.zeros((len(x), 256), dtype=np.int64)
    padded[:, :nrows] = x[:, row_start:row_start+nrows]
    bit_index = np.tile(np.arange(8, dtype=np.int64), len(x))
    repeated_parents = np.repeat(ids.astype(np.int64), 8)
    planes = ((padded[:, None, :] >> np.arange(8)[None, :, None]) & 1).reshape(-1, 256).astype(np.uint8)
    trace_ids = np.asarray([f'mnist_train:{p}:rows{row_start}:a{b}'
                            for p, b in zip(repeated_parents, bit_index)])
    return planes, trace_ids, repeated_parents, bit_index


def exact_binary_dot(x, w):
    """FP64 binary GEMM is exact: every product/sum is an integer in 0..256."""
    x, w = np.asarray(x), np.asarray(w)
    if x.ndim != 2 or w.ndim != 2 or x.shape[1] != 256 or w.shape[0] != 256:
        raise ValueError('Require a 256-position binary dot product')
    if not np.isin(x, (0, 1)).all() or not np.isin(w, (0, 1)).all():
        raise ValueError('Binary operands required for the exact FP64 bound')
    result = x.astype(np.float64) @ w.astype(np.float64)
    if not np.array_equal(result, result.astype(np.int64)) or np.any(result > 256):
        raise AssertionError('Binary exactness bound failed')
    return result.astype(np.int64)


def verify_packed_reconstruction(integer_inputs, weight, row_start, packed):
    x = np.asarray(integer_inputs, dtype=np.int64)
    nrows = min(256, x.shape[1]-row_start)
    padded = np.zeros((len(x), 256), dtype=np.int64)
    padded[:, :nrows] = x[:, row_start:row_start+nrows]
    decoded = np.zeros((len(x), weight.shape[0]), dtype=np.int64)
    for array in packed:
        for bit in range(8):
            counts = exact_binary_dot((padded >> bit) & 1, array['W'])
            for col, output in enumerate(array['output_channels']):
                decoded[:, output] += (1 << bit) * int(array['coefficients'][col]) * counts[:, col]
    expected = x[:, row_start:row_start+nrows] @ weight[:, row_start:row_start+nrows].T
    if not np.array_equal(decoded, expected):
        raise AssertionError('Packed signed bit-plane reconstruction differs from dense integer dot')
    return decoded
