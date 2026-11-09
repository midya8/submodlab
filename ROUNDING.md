# Exact multilinear expectation and cardinality rounding

The original discrete inspector, its native API/CLI, 24 controls and all algorithmic source files remain unchanged. A separate `submodlab.rounding.rounding_audit` API, module CLI and browser page add exact product-distribution and deterministic rounding witnesses. No continuous optimization or new algorithm is claimed.

## Input and expectation

Exactly `objective` and `probabilities` keys. `objective` uses the original exact kind/data/k schema. There is one exact nonnegative integer/fraction string per item, in [0,1], at most 12 characters and reduced numerator/denominator <=10,000. An original objective may be an arbitrary signed/non-normalized table. No floats, Booleans, whitespace, exponents or leading-zero strings are accepted for probabilities. Equivalent fractions reduce exactly. Inputs are not mutated.

For each S subset of V,

```
p_x(S) = product(i in S) x_i * product(i not in S) (1-x_i)
F(x) = sum_S p_x(S) f(S)
```

Every subset mass, value and contribution is retained in integer bitmask order, as are all count probabilities, their sum, expected count and probability of exceeding k. This is the independent product distribution, not the law of the final deterministic set. Expected count sum(x)=k is not an almost-sure cardinality constraint.

The default duplicate-coverage input has x=[1/2,1/2], k=1 and f(S)=1 for any nonempty S. E[count]=1, P(count>1)=1/4 and F(x)=3/4. Both rounded singletons have value 1. The final deterministic tie rule chooses the left endpoint [0,1], so initial inclusion marginals are not preserved.

## Derivatives without dividing by a probability

The gradient for i sums product probabilities over T subset V minus {i}, multiplying f(T+i)-f(T). The mixed derivative for distinct i,j sums probabilities over T subset V minus {i,j}, multiplying f(T+i+j)-f(T+i)-f(T+j)+f(T). Every excluded-context mass, finite difference and weighted contribution is retained. Diagonal Hessian terms are zero. A one-item ground set has no pair, explicitly shown as null in the UI. The derivatives remain defined when any x_i is zero or one.

This uses explicitly excluded context sets. The full-ground-set expectation notation in Dughmi's displayed derivative shorthand can obscure this conditioning; Singer's course notes state the exclusion directly. The correct four-term second difference is used rather than the damaged/reordered PDF extraction of its next display. Pouget-Abadie's notes also have a repeated singleton term in the four-outcome display; the defining expectation and independent derivation, not that typo, govern this implementation.

## Deterministic cardinality pipage rounding

Rounding is allowed iff the complete finite objective is submodular and sum(x)=k exactly, with integer k from the original schema. Unlike the original monotone approximation theorem, this swap proof does not need monotonicity, normalization or nonnegative table values. The nonmonotone cut [0,1,1,0] and a negative modular baseline remain supported controls. For non-submodular objectives or incorrect sums, expectation/derivatives remain diagnostic but every final rounding field is null and history empty. Even an integral non-submodular input is conservatively refused.

At each step, choose the lowest two fractional indices i,j. All other coordinates stay fixed. Along x+t(e_i-e_j),

```
lo = max(-x_i, x_j-1)
hi = min(1-x_i, x_j)
F(t) = F(0) + (partial_i F - partial_j F)t - partial_ij F * t^2
F''(t) = -2 partial_ij F >= 0
```

The mixed partial is constant along this two-coordinate path. Both endpoints are evaluated by complete exact product enumeration. Choose the endpoint with larger F, left on ties. Since 0 lies inside [lo,hi], convexity makes at least one endpoint no worse than the current value. Each endpoint fixes at least one fractional coordinate. Sum stays integer k; exactly one remaining fractional coordinate would contradict that integer sum. Thus the process terminates at exactly k selected items with value at least the supplied F(x).

Every step retains before/after probability vectors and values; both endpoints and values; exact linear/quadratic/curvature coefficients; lo/hi; tie/chosen side; gain and fractional counts. Integral inputs need zero steps. No claim that the resulting set is optimal, that the supplied starting point was optimized, or that a new approximation factor follows. This is deterministic rounding, not randomized pipage or swap rounding with marginal preservation, negative-correlation or concentration guarantees. General matroid/knapsack constraints are not implemented.

The synergy table [0,0,0,1] at [1/2,1/2] has expectation 1/4 but both fixed-size singleton endpoints have value zero. It fails submodularity, so the UI refuses rounding rather than using a false convexity guarantee. Wrong/nonintegral probability sums also refuse rounding. Fractional seeded rectangular controls, endpoint asymmetry, modular ties, all/zero budget and one-item behavior remain explicit.

## Verification

33 Python tests pass on 3.10-3.13: the original 24 tests are retained unchanged, plus nine new tests. New independent controls include 120 full product-distribution oracles; 100 signed-table exact derivative/cross-difference controls; 120 full facility rounding-path oracles with independent endpoint enumeration and several interior quadratic checks; all vertices on small retained objectives; complete context sums, strict schemas, input nonmutation and CLI invalid-output preservation.

21 complete new native/BigInt reports agree on 10,682 exact leaves. Actual Chrome verifies 302 product rows, 1,769 complete selected records (302 subsets, 705 gradient contexts, 727 pair contexts and 35 rounding steps), all gradient/pair summary selections, final fields, all 85 count bars with exact fraction labels, over-budget colors and CSS-height rounding tolerance, export, malformed/stale states and 320/390/1280 containment. The original 24 complete reports / 16,426 leaves and original browser controls still pass. Installed-wheel reproduction outside checkout verifies all 45 reports, both CLIs and six installed module origins.

Native JSON bounds UTF-8 bytes to 32KiB, refuses duplicate keys/nonfinite tokens, and leaves saved output intact on malformed input. Browser JSON.parse keeps the last duplicate key and bounds input to 32,768 characters. Valid diagnostic assumption/sum failures exit CLI 0; malformed inputs exit 2. BigInt/Fraction outputs are exact; count-chart geometry alone uses Number/CSS, checked to a 1e-5 relative tolerance for CSS serialization. Complete enumeration is exponential, bounded to six items and the original eight facility rows. No sampling, learned similarity, benchmark speed, calibrated uncertainty, downstream selection result or private data.

## Sources, read November 9, 2026

1. Shaddin Dughmi, [Submodular Functions: Extensions, Distributions, and Algorithms, A Survey](https://arxiv.org/html/0912.0322v4), scholarly survey based on a December 2009 qualifying report. Definitions 3.12-3.13 and propositions 3.15/3.17: product expectation, derivative structure, cross-convexity. High confidence; explicit excluded contexts corroborated below.
2. Jean Pouget-Abadie, March 3, 2015, [Pipage Rounding, Matroid Constraints](https://thibaut.horel.org/submodularity/notes/02-24.pdf), course notes hosted by Thibaut Horel. Endpoint convexity, finite exchange directions and broader matroid framework. The displayed repeated singleton typo is not imported. This implementation uses only uniform cardinality, not the general tight-set procedure. High confidence after independent derivation.
3. Yaron Singer, Spring 2016 AM221 Lecture 24, [course notes hosted by Thibaut Horel](https://thibaut.horel.org/ao/lecture_notes/AM221_lecture24.pdf). Product expectation and explicitly excluded-set first/second derivatives; continuous optimization is a separate stage. High confidence for definitions; damaged/reordered extraction checked against the four-term finite difference.
4. Krause and Golovin, [Submodular Function Maximization](https://las.inf.ethz.ch/files/krause12survey.pdf), scholarly survey, section 3.2. Multilinear relaxation and distinction between optimizing a fractional point and rounding it. High confidence. No continuous-greedy approximation imported for arbitrary supplied x.
5. Chekuri, Vondrák and Zenklusen, STOC 2011, [Submodular Function Maximization via the Multilinear Relaxation and Contention Resolution Schemes](https://chekuri.cs.illinois.edu/papers/nonmonotone_submod_max.pdf), primary paper, abstract/introduction. Relaxation, optimization and constraint-specific rounding are separate components, including nonmonotone settings. Used for scope, not a claim to implement its algorithms. High confidence.
6. Chekuri and Vondrák, September 23, 2009, [Randomized Pipage Rounding for Matroid Polytopes and Applications](https://theory.stanford.edu/~jvondrak/data/pipage-chernoff.pdf), primary technical paper, introduction and theorem 1.2. Explicit distinction between deterministic objective-valued pipage and randomized oblivious rounding with marginal/negative-correlation guarantees. The latter is not implemented or claimed here. High confidence.

Implementation, independent checks and original synthetic controls by Midya Rahmani. No external implementation code, figures, datasets or weights copied.
