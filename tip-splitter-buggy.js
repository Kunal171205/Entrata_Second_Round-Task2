// tip-splitter-buggy.js

function calculateTotal(bill, tipPercent) {
  const tip = bill * (tipPercent / 100);
  return bill + tip; // total already includes tip
}

function splitEvenly(total, numPeople, tipPercent) {
  // BUG 1: tip is re-applied here even though `total` already includes it
  const totalWithExtraTip = total + total * (tipPercent / 100);
  const perPersonRaw = totalWithExtraTip / numPeople;
  const rounded = Math.round(perPersonRaw * 100) / 100;
  // BUG 2: every person gets the same rounded value — remainder cents silently dropped
  return Array(numPeople).fill(rounded);
}

function splitBill(bill, tipPercent, numPeople) {
  const total = calculateTotal(bill, tipPercent);
  return splitEvenly(total, numPeople, tipPercent);
}

console.log(splitBill(10.03, 15, 3));
// => [4.42, 4.42, 4.42]
// sum = 13.26  ← WRONG: real bill+tip total is only 11.53
