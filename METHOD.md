# SubmodLab mathematical and input contract

## Set functions, not a quality benchmark

Let V={0,...,n-1}. For a set S, facility value is f(S)=sum over represented rows u of max over j in S of a[u,j], where the empty maximum is zero and every a[u,j] is nonnegative. This is normalized, nonnegative, monotone and submodular. Matrix rows need not be selectable items: represented targets and selectable columns can differ. Weighted coverage is the special case a[u,j]=w[u] if item j covers target u, otherwise zero, with w[u]>=0. No learned semantics is inferred from supplied values.

A complete table gives f(S) in integer bitmask order. For example n=3 has masks 0..7, where bit j indicates membership. Reports order subsets by size then lexicographic member list, not mask order. Table values may be signed or nonnormalized, enabling honest invalid-assumption controls. No value is repaired or rescaled automatically.

## Exact finite checks

- Normalized iff f(empty)=0.
- Nonnegative iff every f(S)>=0.
- Monotone iff every absent-item edge delta(j|S)=f(S+j)-f(S)>=0.
- Submodular iff every local pair slack f(S+i)+f(S+j)-f(S)-f(S+i+j)>=0 for distinct absent i,j. Only unordered pairs are needed because the slack is symmetric. Chaining these inequalities gives diminishing returns for all nested sets, equivalent to the usual f(A)+f(B)>=f(A union B)+f(A intersection B) lattice condition.

All edge/pair witnesses and complete violation lists are retained. Independent arbitrary-table tests compare the local checks against every full lattice/nested-set inequality. A one-item ground set has no pair witness; its submodularity check is vacuously true, explicitly displayed as a null selected witness.

## Uniform-cardinality greedy

The optimization target is max f(S) over |S|<=k, including empty output. Exact enumeration retains every maximizer, including smaller-cardinality ties. Greedy starts empty and performs exactly k additions, each maximizing delta(j|S); ties choose the lowest item index. Every candidate value/gain and all maximizers at the visited prefix are recorded. Other possible tie paths are not enumerated. Singleton top-k ranks delta(j|empty) once, then chooses k items with the same tie rule; it does not update overlap.

For invalid nonmonotone tables, exactly-k greedy is a deterministic diagnostic and may lose even to an earlier prefix. The exhaustive comparator still optimizes at most k. We do not claim a greedy approximation in this case. General set functions, costs, knapsack or matroid constraints have different theory and are not supported here.

## Finite-k theorem and proof-derived upper bounds

Only normalized, nonnegative, monotone submodular inputs are eligible. For k>0 the classical cardinality theorem gives

```
f(G_k) >= [1-(1-1/k)^k] OPT_k >= (1-1/e) OPT_k.
```

The displayed factor is exact rational; no decimal 0.63 threshold is substituted. It is a lower-bound guarantee, not an actual performance ratio or optimality claim. k=0 has exact optimum f(empty)=0 for eligible functions but no reciprocal-k theorem factor; factor, guaranteed-value and guarantee-holds fields are null.

For any prefix A and any feasible S*, monotonicity and diminishing returns give

```
f(S*) <= f(A union S*)
       <= f(A) + sum over j in S* minus A of delta(j|A)
       <= f(A) + sum of the k largest nonnegative remaining gains.
```

A separate monotone cap is f(V). Each prefix bound is the smaller of this cap and the marginal bound. The final certificate takes the minimum over all k+1 visited prefixes. Use k, not k-|A|: S* is not required to contain A. This upper bound is valid for all A, not only greedy sets; tests exhaust every A for 60 independent facility controls. Prefix fields retain the full ranked remaining list and all top-k gains. When all assumptions pass, gains are already nonnegative. The max with zero in the formula makes the at-most-k logic explicit.

The greedy/upper-bound ratio is an a posteriori lower bound on greedy/OPT when the upper bound is positive. The actual ratio uses the separately enumerated optimum and is not a certificate available without enumeration. The displayed guaranteed value multiplies the finite-k factor by the exhaustive optimum only as an educational check. None of the certificate computation depends on a claim that this tiny full-enumeration tool scales.

Any failed assumption withholds all theorem and upper-bound fields, even where a weaker theorem might apply. Zero optimum or zero upper bound yields null corresponding ratios. Valid assumption failures exit CLI 0; malformed input exits 2.

## Retained counterexamples

1. Six-row coverage, three items: item 0 covers four rows, items 1/2 each cover three. Greedy chooses 0 then lowest-index tied item 1, value 5; {1,2} covers all six, exact optimum 6. Ratio 5/6, theorem factor 3/4. The terminal k-|A| formula would give incorrect upper bound 5, below true optimum 6; the correct formula retains an upper bound >=6.
2. Two rows [[5,5,0],[0,0,4]]: singleton top-k chooses duplicate representatives {0,1}, value 5; updated greedy selects {0,2}, value 9. This does not isolate a learned mechanism: all supplied values are synthetic.
3. Synergy table [0,2,1,3,1,3,10,12] with k=2: monotone but not submodular; greedy gets 3, optimum 10, ratio 3/10. The monotone-submodular factor is withheld rather than falsely claiming >=3/4.
4. Table [0,2,1,0], k=2: submodular but nonmonotone. Forced greedy ends at value 0; at-most-k optimum is {0}, value 2. Again no monotone guarantee.
5. Nonzero empty baseline, negative tables, all-zero ties, zero budget, all-items budget, fractional values, weighted coverage, modular additivity and seeded rectangular facility controls remain explicit.

## Input and arithmetic boundary

Exactly kind/data/k keys. kind is facility or table. Facility matrices: 1..8 rows, 1..6 columns, rectangular, nonnegative rational strings. Table length is 2^n for n=1..6. Rational strings match an integer or numerator/positive denominator, <=12 characters, reduced numerator magnitude/denominator <=10,000. No numeric/Boolean cells, decimal strings, whitespace, exponents or leading-zero forms. Equivalent fractions reduce exactly. k is a finite integer-valued number 0..n; Python bool is refused, JSON 1.0 is accepted like JavaScript's Number integer. No input mutation.

Native CLI bounds UTF-8 input to 32KiB, rejects duplicate keys/nonfinite tokens and never overwrites an output file on invalid input. Browser bounds characters to 32,768 and JSON.parse retains the last duplicate value. This is an explicit parser difference, not a byte-identical parser claim. Exact Fraction and normalized BigInt arithmetic preserve all output fractions. SVG widths alone convert to Number. Invalid/stale browser input clears the current report, hides results and disables export.

## Independent verification

24 Python tests pass on 3.10-3.13: 120 direct facility set-enumeration references and greedy histories; 100 arbitrary signed tables checked against all full lattice and nested-set inequalities; 40 positive-scale controls; 30 facility/table full-report equivalence checks; 60 facility controls checking marginal upper bounds from every subset, plus exact counterexamples, strict schemas, all ties, zero/all budget and CLI invalid-output preservation. Counts refer to controls within tests, not separate test methods.

24 retained reports compare 16,426 exact native/BigInt leaves. Python uses Fraction, direct bitmask maxima and sorted subsets. Independent JavaScript uses normalized BigInt arithmetic and separate finite-set construction. Actual Chrome verifies 360 subset rows/bars and 2,056 complete displayed records: 360 subset records, 33 greedy steps and all their candidate tables, 57 prefixes, 812 edges and 794 pair witnesses. Summary selections, assumptions, certificate, complete violation lists, export, invalid/stale behavior and 320/390/1280 viewport containment are checked. Isolated installed-wheel reproduction checks all 24 reports, console CLI and four installed module origins outside the checkout.

## Sources, read November 9, 2026

1. Nemhauser, Wolsey and Fisher (1978), [An analysis of approximations for maximizing submodular set functions I](https://www.cs.cmu.edu/~aarti/Class/10704_Spring15/submod-max.pdf), primary Mathematical Programming paper, sections 4 and 7. Classical finite-k greedy approximation and solution-dependent marginal upper bounds, especially (7.2). High confidence; PDF extraction damages symbols, so the independently readable survey proof and formal theorem corroborate the algebra. No source code or figures copied.
2. Krause and Golovin, [Submodular Function Maximization](https://las.inf.ethz.ch/files/krause12survey.pdf), scholarly survey, definitions 1.1-1.3, weighted coverage/facility examples and theorem 1.5 proof. Nonnegative facility entries, normalization, monotonicity, cardinality and the recurrence delta_(t+1) <= (1-1/k) delta_t support the exact finite-k factor. High confidence; no claim about other constraint systems is imported.
3. [Submodlib facility location](https://submodlib.readthedocs.io/en/latest/functions/facilityLocation.html), official implementation documentation, rectangular represented/ground-set formula. High confidence for the stated objective; no library used. Its method docs call a greedy output an optimal set as API shorthand; this project distinguishes greedy and exact optimum explicitly.
4. [Submodlib set cover](https://submodlib.readthedocs.io/en/latest/functions/setCover.html), official documentation, weighted union/min-count definition. High confidence with nonnegative weights, matching the survey. Coverage in this project is encoded by nonnegative weighted binary rows, not a separate algorithm.
5. [Submodlib naive greedy](https://submodlib.readthedocs.io/en/latest/optimizers/naiveGreedy.html), official optimizer documentation, updating marginal gains and tie ambiguity. Its final approximate-guarantee note abbreviates the assumptions to submodularity; primary theory also requires monotonicity/nonnegativity/cardinality. This project never applies the theorem based on that shorthand. We use deterministic lowest-index ties, not unspecified unordered-set iteration. No empirical 90%-of-optimum claim is used.
6. [Greedy Algorithms for Cardinality-Constrained Submodular Maximization](https://isa-afp.org/browser_info/current/AFP/Submodular_Greedy/document.pdf), Isabelle Archive of Formal Proofs, abstract and normalized-monotone setup: explicitly states the finite-k factor 1-(1-1/k)^k and scope limited to cardinality. Independent formal corroboration; this Python/JavaScript implementation is not itself formally verified and does not implement the document's lazy-greedy algorithm.

Implementation, independent checks and original synthetic controls by Midya Rahmani. Established theory, not a novel algorithm, learned representation or downstream result.
