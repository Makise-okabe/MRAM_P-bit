"""An illustrative probability calculation, not a target MRAM circuit simulator.

Run from the repository root with numpy and scipy installed. The complete binary
weight matrix has 256x256 positions. Analytic checks cover every column; Monte
Carlo checks one predeclared column with frozen per-cell variation across reads.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import scipy
from scipy.integrate import quad
from scipy.stats import norm


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(seed: int):
    rng = np.random.default_rng(seed)
    # Each 128-row half has A=11 (16 rows), B=01 (16), C=10 (16),
    # and D=00 (80). Every 8-row chunk has four P/four AP bits per column.
    x = np.tile(np.repeat([3, 1, 2, 0], [16, 16, 16, 80]), 2)
    w = np.empty((256, 256), dtype=np.int64)
    for start in range(0, 256, 8):
        for column in range(256):
            w[start:start + 8, column] = rng.permutation([0] * 4 + [1] * 4)
    concentrated, balanced = [], []
    for base in (0, 128):
        a = list(range(base, base + 16))
        b = list(range(base + 16, base + 32))
        c = list(range(base + 32, base + 48))
        d = list(range(base + 48, base + 128))
        concentrated += a + d[:48] + b + c + d[48:]
        balanced += a[:8] + b[:8] + c[:8] + d[:40]
        balanced += a[8:] + b[8:] + c[8:] + d[40:]
    return x, w, {"concentrated_overlap": np.array(concentrated),
                  "balanced_overlap": np.array(balanced)}


def tail2(a: float, b: float, rho: float) -> float:
    if rho >= 1 - 1e-12:
        return float(norm.sf(max(a, b)))
    if rho <= -1 + 1e-12:
        return float(max(0.0, norm.cdf(-b) - norm.cdf(a)))
    scale = np.sqrt(1 - rho * rho)
    return quad(lambda z: norm.pdf(z) * norm.sf((b - rho * z) / scale),
                a, np.inf, epsabs=1e-14, epsrel=1e-10)[0]


def decoded_moments(sigma: float, limit: int):
    # f(Z)=clip(round(sigma*Z), -limit, limit), an odd function.
    # Layer-cake sums are finite and include all feasible count errors.
    thresholds = (np.arange(1, limit + 1) - 0.5) / sigma
    tails = 2 * norm.sf(thresholds)
    variance = float(np.dot(2 * np.arange(1, limit + 1) - 1, tails))

    @lru_cache(None)
    def covariance(rho: float) -> float:
        if abs(rho) < 1e-12:
            return 0.0
        if abs(abs(rho) - 1) < 1e-12:
            return float(np.sign(rho) * variance)
        return float(sum(2 * (tail2(float(a), float(b), rho)
                             - tail2(float(a), float(b), -rho))
                         for a in thresholds for b in thresholds))

    return {"count_error_probability": float(tails[0]),
            "count_error_second_moment": variance}, covariance


def analytic(config, x, w, orders):
    cv = config["assumed_cell_current_cv"]
    g = 1.0 + w
    coefficients = np.tile([1.0, 2.0], 4)
    records = {}
    sigma = np.sqrt(cv * cv * 30)
    marginal, count_cov = decoded_moments(sigma, 8)
    for name, order in orders.items():
        assert np.array_equal(np.sort(order), np.arange(256))
        assert np.array_equal(x[order] @ w[order], x @ w)
        column_scores, linear_scores, correlations = [], [], []
        for j in range(256):
            sensitivity = np.zeros((8, 256))
            for group in range(4):
                ids = order[group * 64:(group + 1) * 64]
                for bit in (0, 1):
                    mask = (x[ids] >> bit) & 1
                    assert int(mask.sum()) == 16
                    assert int(mask @ w[ids, j]) == 8
                    assert int(w[ids, j].sum()) == 32
                    # Conditional-mean correction using the full-group deviation.
                    sensitivity[2 * group + bit, ids] = cv * g[ids, j] * (mask - 0.25)
            analog_cov = sensitivity @ sensitivity.T
            assert np.allclose(np.diag(analog_cov), sigma * sigma)
            rho = analog_cov / (sigma * sigma)
            decoded_cov = np.array([[count_cov(float(round(v, 12))) for v in row]
                                    for row in rho])
            column_scores.append(float(coefficients @ decoded_cov @ coefficients))
            linear_scores.append(float(coefficients @ analog_cov @ coefficients))
            correlations.append([float(rho[2*k, 2*k + 1]) for k in range(4)])
        assert np.ptp(column_scores) < 1e-12
        records[name] = {"vector_reads": 8, "active_rows_every_read": 16,
                         "ideal_count_every_read_every_column": 8,
                         "within_group_bit_cycle_correlations": correlations[0],
                         "reconstructed_mse_all_columns": column_scores[0],
                         "continuous_readout_mse_all_columns": linear_scores[0]}
    hi, lo = [records[n]["continuous_readout_mse_all_columns"] for n in orders]
    assert abs(hi - lo) < 1e-12
    assert records["balanced_overlap"]["reconstructed_mse_all_columns"] < records["concentrated_overlap"]["reconstructed_mse_all_columns"]
    return {"marginal_for_both_mappings": marginal,
            "independent_error_mse_prediction_for_both": 20 * marginal["count_error_second_moment"],
            "policies": records,
            "checks": {"all_256_columns": True, "exact_ideal_arithmetic": True,
                       "equal_read_counts_and_marginals": True,
                       "equal_continuous_readout_mse": True}}


def summary(values):
    values = np.asarray(values)
    mean = float(values.mean())
    se = float(values.std(ddof=1) / np.sqrt(values.size))
    return {"mean": mean, "independent_sample_se": se,
            "normal_approx_95pct_ci": [mean - 1.96 * se, mean + 1.96 * se]}


def sample(config, x, w, orders, seed):
    rng = np.random.default_rng(seed)
    n = config["samples_per_seed"]
    g = 1.0 + w[:, config["monte_carlo_column"]]
    cv = config["assumed_cell_current_cv"]
    results = {cal: {name: [] for name in orders} for cal in ("conditional_mean", "full_group_gain")}
    marginal = {name: [] for name in orders}
    for offset in range(0, n, config["batch_samples"]):
        size = min(config["batch_samples"], n - offset)
        # Same per-position mismatch samples for both mappings and both input cycles.
        theta = rng.standard_normal((size, 256))
        for name, order in orders.items():
            delta = cv * theta * g[order]
            outputs = {cal: np.zeros(size) for cal in results}
            count_events = np.zeros(size)
            for group in range(4):
                sl = slice(group * 64, (group + 1) * 64)
                ids = order[sl]
                full_delta = delta[:, sl].sum(axis=1)
                assert np.all(96 + full_delta > 0)
                for bit in (0, 1):
                    mask = (x[ids] >> bit) & 1
                    active_delta = delta[:, sl] @ mask
                    corrected = {"conditional_mean": active_delta - 0.25 * full_delta,
                                 "full_group_gain": (24 + active_delta) * 96 / (96 + full_delta) - 24}
                    for cal, current_error in corrected.items():
                        e = np.clip(np.rint(8 + current_error), 0, 16) - 8
                        outputs[cal] += (1 << bit) * e
                        if cal == "conditional_mean":
                            count_events += (e != 0)
            for cal in results:
                results[cal][name].append(outputs[cal] ** 2)
            marginal[name].append(count_events / 8)
    out = {"seed": seed, "independent_variation_samples": n, "calibrations": {}}
    for cal, policies in results.items():
        high = np.concatenate(policies["concentrated_overlap"])
        low = np.concatenate(policies["balanced_overlap"])
        out["calibrations"][cal] = {"concentrated_overlap_mse": summary(high),
                                   "balanced_overlap_mse": summary(low),
                                   "paired_mse_reduction": summary(high - low)}
    out["marginal_count_error_probability"] = {name: summary(np.concatenate(a)) for name, a in marginal.items()}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists():
        raise SystemExit("Refusing to overwrite an existing result")
    if "archive" in args.out.resolve().parts:
        raise SystemExit("Refusing to write into archive")
    config = json.loads(args.config.read_text())
    assert config["rows"] == config["columns"] == 256
    assert config["group_rows"] == 64
    assert config["normalized_cell_current_low"] == 1.0
    assert config["normalized_cell_current_high"] == 2.0
    assert config["target_circuit_validated"] is False
    x, w, orders = fixture(config["weight_seed"])
    record = {"evidence_class": config["evidence_class"], "target_circuit_validated": False,
              "started_utc": datetime.now(timezone.utc).isoformat(),
              "argv": sys.argv, "config_sha256": sha256(args.config),
              "implementation_sha256": sha256(Path(__file__)),
              "weight_matrix_sha256": hashlib.sha256(w.tobytes()).hexdigest(),
              "python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
              "config": config, "analytic": analytic(config, x, w, orders)}
    record["monte_carlo"] = [sample(config, x, w, orders, seed) for seed in config["sampling_seeds"]]
    record["finished_utc"] = datetime.now(timezone.utc).isoformat()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as f:
        json.dump(record, f, indent=2)
        f.write("\n")
    print(json.dumps({"out": str(args.out), "analytic": record["analytic"],
                      "sampling_seeds": len(record["monte_carlo"]),
                      "target_circuit_validated": False}, indent=2))


if __name__ == "__main__":
    main()
