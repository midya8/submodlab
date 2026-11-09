# SubmodLab

An exact finite subset-selection inspector: every greedy marginal, every optimum tie and every assumption behind the bound. Dependency-free Python and independent BigInt JavaScript. No learned model or API call.

[Live inspector](https://midya8.github.io/submodlab/) · [Method and sources](METHOD.md)

## Exact product distributions and cardinality rounding

[New rounding inspector](https://midya8.github.io/submodlab/rounding.html) · [Rounding method](ROUNDING.md)

Independent inclusion probabilities do not enforce a hard budget. The retained [1/2,1/2] duplicate-coverage control has expected count 1, but exceeds k=1 with probability 1/4. Exact deterministic pair rounding raises expected value 3/4 to a fixed-size singleton of value 1. Full product masses, excluded-context gradient/Hessian terms and both endpoints of every swap are retained. Submodularity and probability sum exactly k are required; signed/nonmonotone submodular objectives still work. Synergy and wrong-sum controls refuse rounding. This does not optimize the supplied fractional point or preserve its marginals.

```bash
python -m submodlab.rounding_cli --spec examples/rounding.json --json rounding.json
```

33 Python tests (the original 24 plus nine new tests) pass on 3.10-3.13. The 21 new native/BigInt reports agree on 10,682 exact leaves; actual Chrome checks 302 product rows, 1,769 complete selected records, 705 gradient contexts, 727 pair contexts, 35 steps and 85 count bars, plus summaries, export and invalid/stale states. Original 24 reports and discrete behavior remain unchanged. Installed reproduction covers all 45 reports, both CLIs and six module origins.

## A guarantee is not an optimum

The default six-row coverage control has three selectable items. Greedy chooses item 0, which covers four rows; either next item adds one, for value **5**. Items 1+2 together cover all six rows, so the exact optimum is **6**. The greedy ratio is **5/6**, above the finite-k worst-case factor **3/4**, but not optimal.

A separate duplicate-representative control makes singleton top-k score 5 while updated greedy and the exact optimum score 9. Synergy and nonmonotone controls deliberately break theorem assumptions; their approximation and upper-bound fields are withheld, not repurposed.

## Run

```bash
python -m pip install .
submodlab --spec examples/coverage.json --json report.json
# or: python -m submodlab --spec examples/coverage.json --json report.json
```

```python
from submodlab import audit
r = audit({"kind": "facility", "data": [["5", "5", "0"], ["0", "0", "4"]], "k": 2})
assert r["greedy_value"] == "9"
assert r["singleton_value"] == "5"
```

- `facility`: data rows are represented targets; columns are selectable items. Sum each row's largest selected nonnegative similarity, with an empty maximum of zero. Weighted binary rows encode weighted coverage. This is not a distance-minimization objective or a DPP.
- `table`: data supplies every exact f(S) in integer bitmask order, including f(empty). Arbitrary tables are accepted for diagnostic assumption failures, never silently treated as submodular.
- `k`: integer-valued count 0..n. Uniform cardinality only, not money, costs, knapsack or matroid constraints. Greedy makes exactly k additions; ties go to the lowest index. All maximizers at visited prefixes are retained, not all possible tie paths.

## Complete witnesses

Every subset value, feasibility flag and optimum tie; facility row maxima; all monotonicity edges and local diminishing-return inequalities; complete candidate gains and greedy history; singleton top-k baseline; exact at-most-k optimum; finite-k factor; proof-derived prefix upper bounds and greedy/upper-bound certificates. Null ratios mean zero denominators. Null theorem fields mean failed assumptions or k=0, never a manufactured perfect result.

One to six items, <=64 subsets; facility data has one to eight rows. Exact fraction strings <=12 characters, reduced numerator magnitude/denominator <=10,000. Native input <=32KiB and rejects duplicate keys/nonfinite tokens. Browser input <=32,768 characters and JSON.parse keeps the last duplicate key. Integral numbers like JSON 1.0 are accepted for k, Booleans are not. All report fractions are exact; only SVG geometry uses decimal conversion.

## Verify

```bash
python -m unittest discover -s tests -v
python tools/build_audits.py
npm test
bash tools/wheel_smoke.sh
```

24 Python tests pass on 3.10-3.13, including 120 independently enumerated facility controls, 100 arbitrary-table full lattice comparisons, 40 scaling controls, 30 facility/table equivalence controls and 60 all-subset upper-bound controls. 24 complete native/BigInt reports agree on 16,426 exact leaves. Actual Chrome verifies 360 subset rows/bars and 2,056 complete records, including 33 greedy steps, 57 prefixes, 812 monotonicity edges and 794 diminishing-return witnesses, plus every candidate table, summary, certificate, export, invalid/stale states and 320/390/1280 containment. Isolated installed-wheel reproduction checks all reports, console CLI and four installed module origins outside checkout.

## Limits

This is established monotone-submodular mathematics on tiny synthetic supplied values. Exhaustive enumeration is exponential, not a scalable optimizer or efficient value-oracle implementation. No learned similarity, data-selection quality, corpus diversity, trained embedding, speed, fairness or downstream result. No lazy/stochastic greedy, costs, local search or new theorem. Implementation and original synthetic controls by Midya Rahmani; no external implementation code, figures, datasets or weights copied. See [METHOD.md](METHOD.md) for assumptions, derivation, sources and explicit differences from software-documentation shorthand.
