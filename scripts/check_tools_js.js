// Node unit check that tools.js mirrors calculator.py on the fixture scenario.
const fs = require('fs'); const vm = require('vm');
const src = fs.readFileSync(require('path').join(__dirname, '../worker/campus_worker/render/static/tools.js'), 'utf8');
const ctx = { window: {}, document: { querySelectorAll: () => [] } };
vm.createContext(ctx); vm.runInContext(src, ctx);
const calc = ctx.window.CampusCalc.calculate;
const items = [{ label: 'Room', amount: 1204200, period: 'per_academic_year', mandatory: true }, { label: 'Meal', amount: 295000, period: 'per_semester', mandatory: true },
  { label: 'Deposit', amount: 25000, period: 'one_time', refundable: true, mandatory: true }, { label: 'Parking', amount: null, period: 'per_academic_year', mandatory: false },
  { label: 'Apt', amount: 1860000, period: 'per_academic_year', basis: 'per_unit', mandatory: true }];
const r = calc(items, 'per_academic_year', {});
const assert = require('assert');
assert.strictEqual(r.mandatory, 1794200); assert.strictEqual(r.deposits, 25000); assert.strictEqual(r.unknown.join(','), 'Parking,Apt');
const r2 = calc(items, 'per_semester', { occupants_per_unit: 2 });
assert.strictEqual(r2.mandatory, 602100 + 295000 + 465000);
console.log('tools.js ok: mirrors calculator.py');
