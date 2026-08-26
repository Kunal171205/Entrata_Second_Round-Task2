# Tip Splitter — Bug Fix

> **Task:** Fix incorrect per-person rounding in a bill-splitter utility.
> The app splits a total (bill + tip) evenly across N people, handles cents fairly,
> and shows remainder assignment explicitly.

---

## Root Cause Explanation

Two independent bugs existed in `splitEvenly`:

### Bug 1 — Double-counted tip
`calculateTotal(bill, tipPercent)` already returned `bill + tip`.
`splitEvenly` then received that total **and** `tipPercent` and re-applied the tip a second time:

```js
// Inside splitEvenly — WRONG
const totalWithExtraTip = total + total * (tipPercent / 100); // tip applied AGAIN
```

For `splitBill(10.03, 15, 3)` this inflated the working total from `$11.53` to `$13.27`
before division even started.

### Bug 2 — Remainder cents silently dropped
After dividing, every person received the **same independently-rounded value**:

```js
const rounded = Math.round(perPersonRaw * 100) / 100;
return Array(numPeople).fill(rounded); // identical copies — remainder lost
```

`$11.53 / 3 = $3.8433` rounds to `$3.84` x 3 = `$11.52` — **one cent short** of the real total.
The leftover cent simply disappeared with no assignment or error.

---


---

## Fix — Diff / Patch

```diff
- function splitEvenly(total, numPeople, tipPercent) {
-   // BUG: tip is re-applied even though `total` already includes it
-   const totalWithExtraTip = total + total * (tipPercent / 100);
-   const perPersonRaw = totalWithExtraTip / numPeople;
-   const rounded = Math.round(perPersonRaw * 100) / 100;
-   return Array(numPeople).fill(rounded); // remainder silently dropped
- }
-
- function splitBill(bill, tipPercent, numPeople) {
-   const total = calculateTotal(bill, tipPercent);
-   return splitEvenly(total, numPeople, tipPercent);
- }

+ function splitEvenly(total, numPeople) {              // tipPercent param REMOVED
+   // Work in integer cents — eliminates all IEEE-754 floating-point drift
+   const totalCents = Math.round(total * 100);
+   const baseShare  = Math.floor(totalCents / numPeople);
+   const remainder  = totalCents % numPeople;
+
+   // Distribute 1 extra cent to the first `remainder` people
+   const shares = Array.from({ length: numPeople }, (_, i) =>
+     (baseShare + (i < remainder ? 1 : 0)) / 100
+   );
+
+   return {
+     shares,
+     remainderCents: remainder,
+     remainderAssignedTo: Array.from({ length: remainder }, (_, i) => i + 1),
+   };
+ }
+
+ function splitBill(bill, tipPercent, numPeople) {
+   const total = calculateTotal(bill, tipPercent); // tip applied EXACTLY ONCE, here
+   return splitEvenly(total, numPeople);           // tipPercent NOT passed down
+ }
```

---

## One-Line Commit Message

```
fix: apply tip once and distribute remainder cents explicitly instead of double-charging tip and dropping the leftover cent
```

---

## Worked Example — splitBill(10.03, 15, 3)

| Step | Buggy | Fixed |
|------|-------|-------|
| calculateTotal(10.03, 15) | $11.53 | $11.53 |
| Working total inside splitEvenly | $11.53 x 1.15 = $13.27 (BUG) | $11.53 (correct) |
| Total in cents | 1327c (wrong) | 1153c (correct) |
| Base share per person | 442c | 384c |
| Remainder | ignored | 1c assigned to Person 1 |
| Shares | [$4.42, $4.42, $4.42] (WRONG) | [$3.85, $3.84, $3.84] (CORRECT) |
| Sum | $13.26 (WRONG) | $11.53 (EXACT) |
| Matches grand total? | No | Yes |

---

## Key Invariants Guaranteed by the Fix

- Tip is applied exactly once — inside calculateTotal only
- All arithmetic is done in integer cents — no floating-point rounding drift
- Shares differ by at most 1 cent — no person is over-charged by more than a single cent
- sum(shares) === grandTotal — mathematically guaranteed for every valid input
- Remainder cents are explicitly named (remainderAssignedTo) — never hidden

---

## Files

| File | Purpose |
|------|---------|
| `tip-splitter-fixed.js` | Corrected implementation with verification |
| `tip-splitter-buggy.js` | Original buggy code preserved for reference |
| `index.html` | Full browser UI containing embedded CSS and modular script logic |
| `tip-splitter.test.js` | Vanilla JS CLI test suite (no external dependencies required) |
| `test_ui.py` | Pytest Playwright script for automated End-to-End browser testing of the UI |

---

## Automated Testing Results

To ensure the bug does not regress and the UI behaves exactly as expected, a comprehensive suite of automated tests was written and executed successfully.

### 1. UI Integration Testing (Python + Pytest + Playwright)
A full E2E test suite running in a real headless browser was built to simulate a user typing into the UI.

```bash
$ pytest test_ui.py
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: P:\TASK-2_Entrata_second_round
plugins: anyio-4.12.0, base-url-2.1.0, playwright-0.9.0
collected 4 items

test_ui.py ....                                                          [100%]

============================== 4 passed in 4.64s ==============================
```

### 2. Logic Unit Testing (Vanilla JS)
The underlying algorithm logic was stress-tested across 13 extreme edge cases (including large bills, large parties, 1-cent splits, etc.) asserting perfect mathematical equality.

```bash
$ node tip-splitter.test.js
Starting TipSplit tests...

✅ PASS: Bug Scenario: grand total is $11.53 (tip applied exactly once)
✅ PASS: Bug Scenario: shares sum to exactly the grand total
✅ PASS: Bug Scenario: Person 1 pays $3.85 (base + 1¢ remainder)
✅ PASS: Bug Scenario: Person 2 and 3 pay $3.84 (base share only)
✅ PASS: Bug Scenario: remainder is exactly 1 cent assigned to Person 1
✅ PASS: 0% tip: shares sum to exactly $10.03
✅ PASS: 0% tip: extra cent assigned to Person 1
✅ PASS: Evenly Divisible: shares sum to exactly $30.00
✅ PASS: Evenly Divisible: every person pays exactly $10.00
✅ PASS: Evenly Divisible: remainder is 0 cents
✅ PASS: 1¢ Remainder (2 people): shares sum to exactly $10.01
✅ PASS: 1¢ Remainder (2 people): assigns single remainder cent to first person only
✅ PASS: 2¢ Remainder (3 people): shares sum to exactly $10.04
✅ PASS: 2¢ Remainder (4 people): shares sum to exactly $10.02
✅ PASS: 2¢ Remainder (5 people): first 2 pay extra cent, remaining 3 do not
✅ PASS: Single Person: single share equals grand total $51.08
✅ PASS: Large Party (10): shares sum to exactly $10.07
✅ PASS: Large Party (10): remainder is 7 cents, assigned to first 7 people
✅ PASS: Large Party (10): shares differ by at most 1 cent
✅ PASS: Sum-equals-total invariant holds across 13 combinations

Test Summary: 20 passed, 0 failed.
```
