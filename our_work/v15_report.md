# Stockfish v15 Report: The Cost of Unproven Variables

**Score:** 72.270
**Status:** Succeeded, but regressed from the ~85 base.

## What v15 Was

v15 was an attempt to fix the `Submission Format Error` of v14 while simultaneously pushing for a higher score by adding multi-predicate templates (DESTRUCTIVE_WRITE, CONFUSED_DEPUTY, UNTRUSTED_TO_ACTION) on top of the proven EXFILTRATION base.

## The Result

The submission succeeded (proving the 3-cell notebook structure fix worked), but the score regressed from the baseline 85 to **72.270**.

## Why It Regressed

As predicted by the critical review, **we changed too many variables at once**.

The scoring formula relies heavily on raw throughput—filling the budget with as many successfully firing candidates as possible. 

By introducing new predicate templates:
1. We spent valuable probing time and budget on templates that may not have fired reliably in the opaque Kaggle environment.
2. The round-robin fill logic across multiple families likely allocated budget to lower-yield templates instead of maximizing the high-yield EXFILTRATION template.
3. If the non-exfil templates failed to execute properly during the rigorous replay phase (which has stricter sandboxing than the initial run), those candidates were thrown out, resulting in a lower final count of valid replay signatures.

## Lesson Learned

- **More predicates ≠ higher score** if they don't fire reliably in the actual replay environment.
- Any change to the attack generation logic must be tested in isolation against a known good baseline.
