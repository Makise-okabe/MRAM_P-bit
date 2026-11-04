"""Conditional ADC-event risk engine and row-swap discovery fixture.

Only mathematical/illustrative-model evidence. Not MNIST, Spectre, or a DIB
reproduction. Requires Python >=3.8, numpy, scipy. Output directories never overwrite.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np
from scipy.special import ndtr, ndtri


class Reads:
    def __init__(self, mu, slope, lower, upper, ideal, coefficient, margin):
        self.mu = np.asarray(mu, float)
        self.slope = np.asarray(slope, float)
        self.lower = np.asarray(lower, int)
        self.upper = np.asarray(upper, int)
        self.ideal = np.asarray(ideal, int)
        self.coefficient = np.asarray(coefficient, float)
        self.margin = np.atleast_1d(np.asarray(margin, float))
        r = len(self.mu)
        if any(a.shape != (r,) for a in
               (self.slope, self.lower, self.upper, self.ideal)):
            raise ValueError("Read arrays must have identical length")
        if self.coefficient.shape != (r, len(self.margin)):
            raise ValueError("Require one signed coefficient vector per read")
        if np.any(self.lower > self.ideal) or np.any(self.ideal > self.upper):
            raise ValueError("Ideal count outside logical decoder support")
        if not all(np.isfinite(a).all() for a in
                   (self.mu, self.slope, self.coefficient, self.margin)):
            raise ValueError("Non-finite response or margin")

    def codes(self, t, subset=None):
        subset = np.arange(len(self.mu)) if subset is None else np.asarray(subset)
        t = np.atleast_1d(t)
        value = self.mu[subset][None, :] + t[:, None] * self.slope[subset][None, :]
        return np.clip(np.floor(value + .5),
                       self.lower[subset], self.upper[subset]).astype(int)

    def margins(self, t):
        return self.margin + (self.codes(t) - self.ideal) @ self.coefficient


class NormalFactor:
    def __init__(self, left=-math.inf, right=math.inf):
        if left >= right:
            raise ValueError("Empty factor support")
        self.left, self.right = float(left), float(right)
        self.normalizer = self._mass(np.array([left]), np.array([right]))[0]

    @staticmethod
    def _mass(a, b):
        a, b = np.asarray(a, float), np.asarray(b, float)
        result = ndtr(b) - ndtr(a)
        positive = a >= 0
        result[positive] = ndtr(-a[positive]) - ndtr(-b[positive])
        return np.maximum(result, 0.)

    def masses(self, edges):
        return self._mass(edges[:-1], edges[1:]) / self.normalizer

    def sample(self, n, rng):
        return ndtri(ndtr(self.left) +
                     rng.random(n) * (ndtr(self.right) - ndtr(self.left)))


def midpoints(edges):
    a, b = edges[:-1], edges[1:]
    result = np.empty(len(a))
    finite = np.isfinite(a) & np.isfinite(b)
    result[finite] = (a[finite] + b[finite]) / 2
    left = ~np.isfinite(a) & np.isfinite(b)
    result[left] = b[left] - np.maximum(1., np.abs(b[left]) / 2)
    right = np.isfinite(a) & ~np.isfinite(b)
    result[right] = a[right] + np.maximum(1., np.abs(a[right]) / 2)
    result[~np.isfinite(a) & ~np.isfinite(b)] = 0.
    return result


def read_events(reads, i, factor):
    slope = reads.slope[i]
    if slope == 0:
        return np.empty(0)
    k = np.arange(reads.lower[i], reads.upper[i], dtype=float)
    crossing = (k + .5 - reads.mu[i]) / slope
    return np.sort(crossing[
        (crossing > factor.left) & (crossing < factor.right)])


class EventCache:
    """Exact along the scalar factor; stores class margins on decoder intervals."""
    def __init__(self, reads, factor, events=None, edges=None, margins=None):
        self.reads, self.factor = reads, factor
        if events is None:
            events = [read_events(reads, i, factor) for i in range(len(reads.mu))]
        self.events = events
        if edges is None:
            edges = np.unique(np.concatenate(
                [np.array([factor.left, factor.right])] + events))
        self.edges = edges
        all_events = np.concatenate(events)
        self.multiplicity = np.zeros(len(edges),int)
        if len(all_events):
            np.add.at(self.multiplicity,np.searchsorted(edges,all_events),1)
        if margins is None:
            # Vectorized full sweep, not repeated full dot products at each point.
            ninterval, nc = len(edges) - 1, len(reads.margin)
            increment = np.zeros((ninterval, nc))
            first = reads.margins(midpoints(edges)[:1])[0]
            for i, cuts in enumerate(events):
                if len(cuts):
                    at = np.searchsorted(edges, cuts)
                    delta = np.sign(reads.slope[i]) * reads.coefficient[i]
                    np.add.at(increment, at, delta)
            margins = first + np.cumsum(increment, axis=0)
        self.values = margins

    def updated(self, new_reads, changed):
        changed = np.unique(np.asarray(changed, int))
        if not np.array_equal(new_reads.margin, self.reads.margin):
            raise ValueError("A resident map must preserve the ideal margin")
        unchanged = np.setdiff1d(np.arange(len(self.reads.mu)), changed)
        for name in ("mu", "slope", "lower", "upper", "ideal", "coefficient"):
            if not np.array_equal(getattr(new_reads, name)[unchanged],
                                  getattr(self.reads, name)[unchanged]):
                raise ValueError("Changed-read declaration misses an altered read")
        events = list(self.events)
        counts = self.multiplicity.copy()
        removed = np.concatenate([self.events[i] for i in changed])
        if len(removed):
            np.add.at(counts,np.searchsorted(self.edges,removed),-1)
        for i in changed:
            events[i] = read_events(new_reads, int(i), self.factor)
        added = np.concatenate([events[i] for i in changed])
        retained = counts > 0
        retained[[0,-1]] = True
        edges = np.union1d(self.edges[retained],added)
        t = midpoints(edges)
        interval = np.searchsorted(self.edges[1:-1], t, side="right")
        values = self.values[interval].copy()
        old_error = self.reads.codes(t, changed) - self.reads.ideal[changed]
        new_error = new_reads.codes(t, changed) - new_reads.ideal[changed]
        values += new_error @ new_reads.coefficient[changed]
        values -= old_error @ self.reads.coefficient[changed]
        # Avoid regenerating all unaffected event multiplicities.
        updated = object.__new__(EventCache)
        updated.reads,updated.factor = new_reads,self.factor
        updated.events,updated.edges,updated.values = events,edges,values
        new_counts = np.zeros(len(edges),int)
        new_counts[np.searchsorted(edges,self.edges[retained])] = counts[retained]
        if len(added):
            np.add.at(new_counts,np.searchsorted(edges,added),1)
        updated.multiplicity = new_counts
        return updated

    def summary(self, include_intervals=False):
        mass = self.factor.masses(self.edges)
        failed = np.any(self.values <= 0, axis=1)
        mean = mass @ self.values
        second = mass @ (self.values**2)
        result = {
            "failure_probability": float(mass[failed].sum()),
            "margin_mean": mean.tolist(),
            "margin_second_moment": second.tolist(),
            "margin_error_MSE": (mass @ (
                (self.values-self.reads.margin)**2)).tolist(),
            "margin_variance": np.maximum(second-mean**2, 0.).tolist(),
            "event_count": int(len(self.edges)-2),
            "read_count": int(len(self.reads.mu)),
        }
        if len(mean) == 1:
            var = max(float(second[0]-mean[0]**2), 0.)
            gaussian = (float(ndtr(-mean[0]/math.sqrt(var))) if var else
                        float(mean[0] <= 0))
            result["Gaussian_exact_moment_surrogate"] = gaussian
        if include_intervals:
            result["failure_intervals"] = [
                [float(a), float(b)] for a,b,fail in
                zip(self.edges[:-1], self.edges[1:], failed) if fail]
        return result


def vectorized_full_cache(reads,factor):
    """Optimized score baseline: generate every read's crossings in one array."""
    # The benchmark uses finite factor support. All integer decoder transitions
    # outside the current range are excluded without scanning the full ADC range.
    if not (math.isfinite(factor.left) and math.isfinite(factor.right)):
        return EventCache(reads,factor)
    a = reads.mu + reads.slope*factor.left
    b = reads.mu + reads.slope*factor.right
    first = np.maximum(reads.lower,np.ceil(np.minimum(a,b)-.5)).astype(int)
    last = np.minimum(reads.upper-1,np.floor(np.maximum(a,b)-.5)).astype(int)
    length = np.maximum(0,last-first+1)
    k = first[:,None] + np.arange(max(int(length.max()),1))[None,:]
    valid = (k<=last[:,None]) & (reads.slope[:,None]!=0)
    owner,position = np.nonzero(valid)
    cuts = (k[owner,position]+.5-reads.mu[owner])/reads.slope[owner]
    inside = (cuts>factor.left)&(cuts<factor.right)
    cuts,owner = cuts[inside],owner[inside]
    edges = np.unique(np.r_[factor.left,cuts,factor.right])
    increment = np.zeros((len(edges)-1,len(reads.margin)))
    at = np.searchsorted(edges,cuts)
    if len(cuts):
        np.add.at(increment,at,
                  reads.coefficient[owner]*np.sign(reads.slope[owner,None]))
    values = reads.margins(midpoints(edges)[:1])[0]+np.cumsum(increment,axis=0)
    # Summary requires the grid and values only; no per-read cache is built.
    result = object.__new__(EventCache)
    result.reads,result.factor,result.edges,result.values = reads,factor,edges,values
    return result


def fixture(order, repetitions=16):
    # Four binary row types, twice each; mirrored inactive half.
    w8 = np.array([[1,1],[1,1],[1,0],[1,0],
                   [0,1],[0,1],[0,0],[0,0]], int)
    f8 = np.array([.35,-.35,.20,.10,-.10,-.20,.35,-.35])
    weights = np.repeat(np.vstack([w8,w8]), repetitions, axis=0)
    x = np.repeat(np.r_[np.ones(8,int), np.zeros(8,int)], repetitions)
    physical_mode = np.repeat(np.r_[f8,-f8]/repetitions, repetitions)
    atom_order = np.r_[order, np.asarray(order)+8]
    permutation = (atom_order[:,None]*repetitions +
                   np.arange(repetitions)[None,:]).ravel()
    wp, xp = weights[permutation], x[permutation]
    n, m = len(x), int(x.sum())
    total = wp.sum(axis=0)
    count = xp @ wp
    # g_AP=1, g_P=2; subtract the exact nominal AP current m.
    mu = xp @ (1+wp) - m
    slope = (physical_mode*xp) @ (1+wp)
    full_calibration_slope = physical_mode @ (1+wp)
    assert np.max(np.abs(full_calibration_slope)) < 1e-12
    assert 1 - 2*np.max(np.abs(physical_mode)) > 0
    assert np.array_equal(count, x@weights)
    reads = Reads(mu, slope, np.maximum(0,m+total-n),
                  np.minimum(m,total), count,
                  np.array([[1.],[-1.]]), [.5])
    metadata = {
        "physical_row_positions": n, "active_rows": m,
        "column_popcounts": total.tolist(),
        "ideal_selected_counts": count.tolist(),
        "factor_support": [-2,2],
        "max_absolute_cell_gain_change": 2*float(np.abs(physical_mode).max()),
        "zero_and_full_calibration_residual_slope":
            full_calibration_slope.tolist(),
        "normalized_read_slopes": slope.tolist(),
        "calibration_scope": "zero/full-column affine gain-offset control only",
        "not_validated": ["MOSFET", "wire RC", "ADC circuit", "MNIST"],
    }
    return reads, metadata


def meaningful_checks():
    factor = NormalFactor(-2,2)
    a, metadata_a = fixture(np.arange(8))
    b, metadata_b = fixture(np.array([0,6,2,4,3,5,1,7]))
    ca, cb = EventCache(a,factor), EventCache(b,factor)
    assert np.allclose(a.slope,[.3,-.3],atol=1e-12)
    assert np.allclose(b.slope,[.8,.6],atol=1e-12)
    sa, sb = ca.summary(True), cb.summary(True)
    # Closed-form independent answers for the deliberately constructed witness.
    z = ndtr(2)-ndtr(-2)
    risk_a = (ndtr(-5/3)-ndtr(-2))/z
    risk_b = (ndtr(5/6)-ndtr(5/8)+ndtr(2)-ndtr(15/8))/z
    assert abs(sa["failure_probability"]-risk_a) < 1e-12
    assert abs(sb["failure_probability"]-risk_b) < 1e-12
    assert risk_a < risk_b
    assert sa["margin_variance"][0] > sb["margin_variance"][0]
    assert (sa["Gaussian_exact_moment_surrogate"] >
            sb["Gaussian_exact_moment_surrogate"])
    # The ordinary output-MSE comparator happens to choose A in this witness.
    # Include it to avoid pretending all strong comparators have been defeated.
    for reads, cache, summary in ((a,ca,sa),(b,cb,sb)):
        t = midpoints(cache.edges)
        assert np.allclose(cache.values,reads.margins(t),atol=1e-11)
        error = reads.codes(t)-reads.ideal
        mass = factor.masses(cache.edges)
        summary["sum_of_output_MSE"] = float(
            np.sum(mass[:,None]*error**2))
    assert sa["sum_of_output_MSE"] < sb["sum_of_output_MSE"]

    # Direct persistent-cell calculation at random factor values, not fresh read noise.
    rng = np.random.default_rng(20261104)
    t = factor.sample(200000, rng)
    mc = {}
    for name, reads, cache in (("A",a,ca),("B",b,cb)):
        probability = float(np.mean(reads.margins(t)[:,0] <= 0))
        truth = cache.summary()["failure_probability"]
        assert abs(probability-truth) < 6*math.sqrt(
            max(truth*(1-truth),1e-12)/len(t))
        mc[name] = {"draws":len(t), "failure_fraction":probability,
                    "exact_probability":truth}
    # Same-statistics observations are controls, not a faithful DIB reproduction.
    assert metadata_a["active_rows"] == metadata_b["active_rows"]
    assert metadata_a["column_popcounts"] == metadata_b["column_popcounts"]
    changed = ca.updated(b,[0,1])
    assert np.allclose(changed.values,cb.values,atol=1e-11)
    assert abs(changed.summary()["failure_probability"]-risk_b) < 1e-12

    # Multiple signed margins; correlated counts; negative/zero slopes;
    # simultaneous crossings; changed means, supports and coefficients.
    max_difference = 0.
    for case in range(60):
        r,nc = 40,3
        mu = rng.uniform(2,10,r)
        slope = rng.normal(0,.7,r)
        slope[::7] = 0
        slope[1:3] = .5
        mu[1:3] = 4
        coef = rng.integers(-4,5,(r,nc)).astype(float)
        base = Reads(mu,slope,np.zeros(r,int),np.full(r,12),
                     np.rint(mu).astype(int),coef,np.full(nc,.5))
        old = EventCache(base,factor)
        indices = rng.choice(r,3,replace=False)
        mu2,s2,l2,u2 = mu.copy(),slope.copy(),base.lower.copy(),base.upper.copy()
        c2,i2 = coef.copy(),base.ideal.copy()
        mu2[indices] += rng.normal(0,.2,3)
        s2[indices] += rng.normal(0,.3,3)
        l2[indices] = 1
        u2[indices] = 11
        i2[indices] = np.rint(mu2[indices]).astype(int)
        c2[indices] += rng.integers(-1,2,(3,nc))
        new = Reads(mu2,s2,l2,u2,i2,c2,base.margin)
        full = EventCache(new,factor)
        update = old.updated(new,indices)
        diff = abs(full.summary()["failure_probability"]-
                   update.summary()["failure_probability"])
        max_difference = max(max_difference,diff)
        assert np.array_equal(full.edges,update.edges)
        assert np.allclose(full.values,new.margins(midpoints(full.edges)),atol=1e-10)
        assert np.allclose(full.values,update.values,atol=1e-10)
        assert diff < 1e-12

    # Non-overwriting protocol, no hidden neural test-set access.
    return {
        "evidence_class":"conditional mathematical and illustrative-model verification",
        "novelty_pass":False,"competitive_task_pass":False,
        "DIB_full_text_access":False,"DIB_reproduced":False,
        "fixture_A":metadata_a,"fixture_B":metadata_b,
        "A":sa,"B":sb,
        "direct_persistent_factor_MC":mc,
        "incremental_update_checks":60,
        "max_incremental_probability_difference":max_difference,
        "honest_comparator_outcome":
            "Exact-risk and ordinary output-MSE both choose A; Gaussian exact-margin-moment score chooses B. This is not a defeat of every baseline.",
    }


def timing_check():
    rng = np.random.default_rng(54321)
    r,nc = 320,9
    mu = rng.uniform(20,100,r)
    slope = rng.normal(0,.7,r)
    coefficient = rng.integers(-8,9,(r,nc)).astype(float)
    base = Reads(mu,slope,np.zeros(r,int),np.full(r,128),
                 np.rint(mu).astype(int),coefficient,np.full(nc,.5))
    factor = NormalFactor(-2,2)
    old = EventCache(base,factor)
    changes = []
    for _ in range(50):
        indices = rng.choice(r,4,replace=False)
        s = slope.copy()
        s[indices] += rng.normal(0,.2,4)
        changes.append((Reads(mu,s,base.lower,base.upper,base.ideal,
                              coefficient,base.margin),indices))
    for new,ids in changes[:3]:
        EventCache(new,factor).summary()
        old.updated(new,ids).summary()
    full_times,vector_times,update_times = [],[],[]
    differences = []
    for new,ids in changes:
        start = time.perf_counter()
        f = EventCache(new,factor).summary()
        full_times.append(time.perf_counter()-start)
        start = time.perf_counter()
        v = vectorized_full_cache(new,factor).summary()
        vector_times.append(time.perf_counter()-start)
        start = time.perf_counter()
        u = old.updated(new,ids).summary()
        update_times.append(time.perf_counter()-start)
        differences.append(abs(f["failure_probability"]-u["failure_probability"]))
        assert abs(v['failure_probability']-f['failure_probability']) < 1e-12
    return {
        "scope":"local synthetic cache-update microbenchmark; not MC or task superiority",
        "reads":r,"competing_margins":nc,"changed_reads":4,"candidates":len(changes),
        "median_full_rebuild_seconds":float(np.median(full_times)),
        "median_vectorized_full_score_seconds":float(np.median(vector_times)),
        "median_cached_update_seconds":float(np.median(update_times)),
        "full_over_update_ratio":float(np.median(full_times)/np.median(update_times)),
        "vectorized_full_over_update_ratio":float(np.median(vector_times)/np.median(update_times)),
        "maximum_risk_difference":max(differences),
        "excluded":"physical fitting, factor selection, full MNIST, outer-factor samples, mapping search",
    }


def row_mapping_screen():
    """Frozen synthetic boundary-input screen; all methods get the same search size.

    This is not MNIST. Inputs are deliberately conditioned to equal clean binary
    class counts, giving margin .5. A common factor remains persistent over reads.
    Zero/full-column calibration is insensitive to the mirrored response mode.
    """
    w8 = np.array([[1,1],[1,1],[1,0],[1,0],
                   [0,1],[0,1],[0,0],[0,0]],int)
    f8 = np.array([.35,-.35,.20,.10,-.10,-.20,.35,-.35])
    repetitions = 16
    weights = np.repeat(np.vstack([w8,w8]),repetitions,axis=0)
    physical = np.repeat(np.r_[f8,-f8]/repetitions,repetitions)
    total = weights.sum(axis=0)
    factor = NormalFactor(-2,2)

    def inputs(seed,n):
        rng = np.random.default_rng(seed)
        good = []
        while sum(len(a) for a in good) < n:
            x = rng.integers(0,2,(1024,256))
            counts = x @ weights
            good.append(x[counts[:,0] == counts[:,1]])
        return np.concatenate(good)[:n]

    cal,dev = inputs(602,64),inputs(603,128)

    def score(order,x):
        atoms = np.r_[order,np.asarray(order)+8]
        p = (atoms[:,None]*repetitions+np.arange(repetitions)).ravel()
        wp,xp = weights[p],x[:,p]
        m = x.sum(axis=1)
        ideal = x @ weights
        assert np.array_equal(ideal,xp @ wp)
        slope = (xp*physical) @ (1+wp)
        assert np.max(np.abs(physical @ (1+wp))) < 1e-12
        records = []
        for j in range(len(x)):
            read = Reads(ideal[j],slope[j],np.maximum(0,m[j]+total-256),
                         np.minimum(m[j],total),ideal[j],[[1.],[-1.]],[.5])
            cache = EventCache(read,factor)
            s = cache.summary()
            e = read.codes(midpoints(cache.edges))-read.ideal
            output_mse = np.sum(factor.masses(cache.edges)[:,None]*e**2)
            records.append([s['failure_probability'],
                            s['Gaussian_exact_moment_surrogate'],output_mse])
        return np.mean(records,axis=0)

    methods = [('event_risk',0),('Gaussian_exact_margin_moments',1),
               ('exact_output_MSE',2)]
    result = {}
    for name,criterion in methods:
        order = np.arange(8)
        cal_values = score(order,cal)
        evaluations = 1
        for iteration in range(2):
            proposals = [(order.copy(),cal_values)]
            for a in range(8):
                for b in range(a+1,8):
                    p = order.copy();p[a],p[b] = p[b],p[a]
                    proposals.append((p,score(p,cal)))
                    evaluations += 1
            # Frozen deterministic tie rule; never use DEV to choose a map.
            order,cal_values = min(proposals,key=lambda q:(q[1][criterion],
                                                          tuple(q[0])))
        dev_values = score(order,dev)
        result[name] = {
            'atom_order':order.tolist(),'candidate_evaluations':evaluations,
            'CAL_exact_failure_probability':float(cal_values[0]),
            'DEV_exact_failure_probability':float(dev_values[0]),
            'CAL_Gaussian_margin_score':float(cal_values[1]),
            'CAL_exact_output_MSE':float(cal_values[2]),
        }
    return {
        'evidence_class':'synthetic boundary-conditioned binary two-class head',
        'not_MNIST':True,'CAL_parents':64,'DEV_parents':128,
        'CAL_seed':602,'DEV_seed':603,
        'search':'two greedy iterations, all 28 mirrored atom swaps per iteration',
        'read_budget':'one nonempty vector read / two column conversions per parent; identical for every map',
        'full_calibration':'zero/full-column affine control has zero factor slope',
        'input_density_comparator':'activity and bit significance unchanged by every map; not a DIB reproduction',
        'methods':result,
        'CAL_sha256':hashlib.sha256(cal.tobytes()).hexdigest(),
        'DEV_sha256':hashlib.sha256(dev.tobytes()).hexdigest(),
        'limitation':'same synthetic one-factor model supplies CAL and DEV physics; no chip-model mismatch, transient noise, neural hidden layers or physical cost included',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    result = meaningful_checks()
    result["timing"] = timing_check()
    result["row_mapping_screen"] = row_mapping_screen()
    result["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result["numpy_version"] = np.__version__
    payload = json.dumps(result,indent=2,allow_nan=False)+"\n"
    (args.out/"results.json").write_text(payload)
    print(payload)


if __name__ == "__main__":
    main()

