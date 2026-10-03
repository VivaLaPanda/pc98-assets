// Node harness: node run.js <outdir> [jsonOpts]  -> renders the test set with pc98.js into <outdir>
'use strict';
const fs = require('fs');
const path = require('path');
const png = require('./pngio');
// the filter itself lives in the site repo; set PC98=/path/to/pc98.js to use another copy
const PC98 = require(process.env.PC98 || path.resolve(__dirname, '../../vivalapanda.moe/js/pc98.js'));

const SET = [
  ['cb1e981b', 'covers/cb1e981b.png', 'Dubai at night (cover)'],
  ['6883511c', 'covers/6883511c.png', 'aerial suburbs (cover)'],
  ['c2f74e39', 'covers/c2f74e39.png', 'storefront (cover)'],
  ['f3b8a872', 'covers/f3b8a872.png', 'truck and kid (cover)'],
  ['f847dd0c', 'covers/f847dd0c.png', 'B&W model (cover)'],
  ['b1944e70', 'covers/b1944e70.png', 'UI collage (cover)'],
  ['62672586', 'covers/62672586.png', 'default illustration (cover)'],
  ['00_01', 'inline/00_01.png', 'Burj at night'],
  ['05_01', 'inline/05_01.png', 'face + sculpture'],
  ['09_02', 'inline/09_02.png', 'Hong Kong neon'],
  ['09_05', 'inline/09_05.png', 'Tokyo alley'],
  ['09_01', 'inline/09_01.png', 'bike street'],
  ['08_01', 'inline/08_01.png', 'night walker'],
  ['09_04', 'inline/09_04.png', 'flower poster (illus.)'],
  ['face', 'faces/face.png', 'portrait (CC BY-SA, Wikimedia)'],
  ['face2', 'faces/face2.png', 'studio portrait (CC BY-SA, Wikimedia)'],
];

const out = process.argv[2] || 'out';
const opts = JSON.parse(process.argv[3] || '{}');
fs.mkdirSync(out, { recursive: true });
const only = process.env.ONLY ? process.env.ONLY.split(',') : null;
const times = {};
for (const [id, file] of SET) {
  if (only && !only.includes(id)) continue;
  const img = png.decode(file);
  const t0 = process.hrtime.bigint();
  const res = PC98.process(img.data, img.width, img.height, Object.assign({ width: 240 }, opts));
  const ms = Number(process.hrtime.bigint() - t0) / 1e6;
  times[id] = ms;
  const up = PC98.upscale(res, res.pixel);
  fs.writeFileSync(path.join(out, id + '.png'), png.encode(up));
  fs.writeFileSync(path.join(out, id + '_native.png'), png.encode({ width: res.width, height: res.height, data: res.rgba }));
  if (res.layers) {
    fs.writeFileSync(path.join(out, id + '_base.png'), png.encode({ width: res.width, height: res.height, data: res.layers.flat }));
    fs.writeFileSync(path.join(out, id + '_target.png'), png.encode({ width: res.width, height: res.height, data: res.layers.target }));
    if (res.layers.lines) {
      const m = new Uint8ClampedArray(res.rgba);
      for (let i = 0; i < res.layers.lines.length; i++) if (res.layers.lines[i]) { m[i * 4] = 255; m[i * 4 + 1] = 0; m[i * 4 + 2] = 255; }
      fs.writeFileSync(path.join(out, id + '_lines.png'), png.encode({ width: res.width, height: res.height, data: m }));
    }
  }
  console.log(id.padEnd(10), `${res.width}x${res.height}`, `${res.palette.length} cols`, ms.toFixed(1) + 'ms',
    res.palette.map(c => c.map(v => (v / 17).toString(16)).join('')).join(' '));
}
fs.writeFileSync(path.join(out, 'times.json'), JSON.stringify(times));
