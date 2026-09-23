// Generator compatibility check. A seed must always build the exact same board, or games in progress
// change under players. Compares the generator in index.html against stored fingerprints of the
// board, its solution and the RNG draws it consumed.
//
//   node tools/check_generator.js           verify, exits 1 on any difference
//   node tools/check_generator.js --update  rewrite the fingerprints (only for a deliberate breaking change)
const fs = require('fs');
const os = require('os');
const path = require('path');
const crypto = require('crypto');
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

const HTML = path.join(__dirname, '..', 'index.html');
const FINGERPRINTS = path.join(__dirname, 'generator_fingerprints.json');
const RNG_HOOK = 'RNG = mulberry32(seedInt);';

function loadGenerator(rng){
  const s = fs.readFileSync(HTML, 'utf8').replace(/\r\n/g, '\n');
  const start = s.indexOf('function PUZZLE_GENERATOR(){');
  const endMark = '\nreturn generate_puzzle;\n}';
  const end = s.indexOf(endMark, start);
  if (start < 0 || end < 0) throw new Error('PUZZLE_GENERATOR not found in index.html');
  let src = s.slice(start, end + endMark.length);
  if (src.split(RNG_HOOK).length !== 2) throw new Error(`expected "${RNG_HOOK}" exactly once in PUZZLE_GENERATOR`);
  // Count draws so a change in how randomness is consumed is caught even when a board happens to match.
  src = src.replace(RNG_HOOK, 'RNG = (function(f){ return function(){ const v=f(); __rng.n++; __rng.last=v; return v } })(mulberry32(seedInt));');
  return new Function('__rng', src + '\nreturn PUZZLE_GENERATOR();')(rng);
}

// Fixed corpus: every size, numeric seeds like fill_slot_data makes, the client's string seed
// formats, parseSeedInput edge cases and every tryout board.
function corpus(){
  const cases = [];
  let st = 0x2545f491;
  const rnd = ()=>{ st = (st + 0x6D2B79F5) >>> 0; let t = st; t = Math.imul(t ^ t>>>15, t|1); t ^= t + Math.imul(t ^ t>>>7, t|61); return ((t ^ t>>>14)>>>0) / 4294967296; };
  for (let pairs = 2; pairs <= 20; pairs++){
    const n = pairs <= 10 ? 25 : pairs <= 14 ? 8 : pairs <= 17 ? 4 : 3;
    for (let i = 0; i < n; i++) cases.push({ pairs, seed: String(100000000 + Math.floor(rnd() * 900000000)) });
    cases.push({ pairs, seed: `Player:Level ${pairs}:0` });
  }
  for (const seed of ['0', '1', '4294967295', '4294967296', '-1', ' 123456789 ', '00042']) cases.push({ pairs: 5, seed });
  for (let L = 1; L <= 20; L++) for (let s = 0; s < 3; s++){
    const pairs = Math.max(3, Math.min(20, Math.round(3 + 17 * ((L - 1) / 19))));
    cases.push({ pairs, seed: `tryout:Level ${L}:${s}` });
  }
  return cases;
}
const keyOf = c => `${c.pairs}|${c.seed}`;

if (!isMainThread){
  const rng = { n: 0, last: 0 };
  const gen = loadGenerator(rng);
  for (const c of workerData){
    rng.n = 0; rng.last = 0;
    const p = gen({ seed: c.seed, pairs: c.pairs });
    const body = JSON.stringify([p.grid, p.start_points, p.rows, p.cols, p.seed, p.solution, rng.n, rng.last]);
    parentPort.postMessage({ key: keyOf(c), hash: crypto.createHash('sha256').update(body).digest('hex').slice(0, 16) });
  }
  return;
}

const update = process.argv.includes('--update');
let expected = {};
if (!update){
  if (!fs.existsSync(FINGERPRINTS)){ console.error('No fingerprints file. Run with --update once to create it.'); process.exit(1); }
  expected = JSON.parse(fs.readFileSync(FINGERPRINTS, 'utf8'));
}
const cases = update ? corpus() : Object.keys(expected).map(k => { const i = k.indexOf('|'); return { pairs: Number(k.slice(0, i)), seed: k.slice(i + 1) }; });
cases.sort((a, b) => b.pairs - a.pairs); // big boards first so the workers finish together

const threads = Math.max(1, Math.min(cases.length, os.cpus().length - 1));
const shares = Array.from({ length: threads }, () => []);
cases.forEach((c, i) => shares[i % threads].push(c));

const t0 = Date.now();
const got = {};
let live = 0, failed = false;
for (const share of shares){
  live++;
  const w = new Worker(__filename, { workerData: share });
  w.on('message', r => { got[r.key] = r.hash; });
  w.on('error', e => { failed = true; console.error(e); });
  w.on('exit', () => { if (--live === 0) finish(); });
}

function finish(){
  const secs = ((Date.now() - t0) / 1000).toFixed(1);
  if (failed){ process.exitCode = 1; return; }
  if (update){
    const out = {};
    for (const c of corpus()) out[keyOf(c)] = got[keyOf(c)];
    fs.writeFileSync(FINGERPRINTS, JSON.stringify(out, null, 1) + '\n');
    console.log(`Wrote ${Object.keys(out).length} fingerprints in ${secs}s.`);
    return;
  }
  const bad = Object.keys(expected).filter(k => got[k] !== expected[k]);
  if (bad.length){
    console.error(`FAIL: ${bad.length} of ${cases.length} boards differ from the fingerprints (${secs}s):`);
    for (const k of bad.slice(0, 20)) console.error(`  pairs ${k.replace('|', ', seed "')}"`);
    process.exitCode = 1;
  } else {
    console.log(`OK: ${cases.length} boards match their fingerprints (${secs}s).`);
  }
}
