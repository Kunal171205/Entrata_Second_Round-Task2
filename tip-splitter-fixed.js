// tip-splitter-fixed.js
// ✅ Corrected version — two bugs fixed

// ─── FIX SUMMARY ──────────────────────────────────────────────────────────────
//
// Bug 1 (double-tip): splitEvenly was re-applying tipPercent to a total that
//   already included the tip from calculateTotal. Removed the tipPercent param
//   from splitEvenly entirely — the tip is now applied ONCE and ONLY in calculateTotal.
//
// Bug 2 (dropped remainder): Array(n).fill(rounded) gives every person the same
//   rounded value, silently losing leftover cents. Fixed by converting the grand
//   total to INTEGER CENTS first, using floor-division for the base share, and
//   distributing the modulo remainder one cent at a time to the first N people.
//
// Commit message:
//   fix: apply tip once and distribute remainder cents explicitly instead of
//        double-charging tip and dropping the leftover cent
// ──────────────────────────────────────────────────────────────────────────────

function calculateTotal(bill, tipPercent) {
  const tip = bill * (tipPercent / 100);
  return bill + tip; // tip is applied HERE and NOWHERE ELSE
}

// tipPercent param removed — total already includes the tip
function splitEvenly(total, numPeople) {
  // Work in integer cents to avoid IEEE-754 floating-point drift
  const totalCents = Math.round(total * 100);

  // Floor-division: every person's guaranteed minimum share
  const baseShare = Math.floor(totalCents / numPeople);

  // Remainder cents that can't be divided further (0 ≤ remainder < numPeople)
  const remainder = totalCents % numPeople;

  // Give 1 extra cent to the first `remainder` people — fair and deterministic
  const shares = Array.from({ length: numPeople }, (_, i) =>
    (baseShare + (i < remainder ? 1 : 0)) / 100
  );

  return {
    shares,
    remainderCents: remainder,
    // 1-based indices of people who pay 1 cent more
    remainderAssignedTo: Array.from({ length: remainder }, (_, i) => i + 1),
  };
}

function splitBill(bill, tipPercent, numPeople) {
  const total = calculateTotal(bill, tipPercent); // tip applied exactly once
  return splitEvenly(total, numPeople);
}

// ─── VERIFICATION ─────────────────────────────────────────────────────────────

const result = splitBill(10.03, 15, 3);

console.log("Grand total :", (10.03 * 1.15).toFixed(2));   // 11.53
console.log("Shares      :", result.shares);                // [3.85, 3.84, 3.84]
console.log("Sum of shares:", result.shares.reduce((a,b) => +(a+b).toFixed(2), 0)); // 11.53 ✅
console.log("Remainder ¢ :", result.remainderCents);        // 1
console.log("Assigned to :", result.remainderAssignedTo);   // [1]

// Edge case: perfectly divisible
const even = splitBill(30.00, 0, 3);
console.log("\nEven split  :", even.shares);                 // [10, 10, 10]
console.log("Remainder ¢ :", even.remainderCents);          // 0
