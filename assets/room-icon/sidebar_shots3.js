// Round 3: the real sidebar of contact.html (http://localhost:8765, `microtemplate watch`) at 2x, with each candidate
// swapped in for /img/icons/room_recolor.png by request interception. Run with node + puppeteer-core.
const puppeteer = require('/Users/vivalapanda/animations/toolkit/render/node_modules/puppeteer-core');
const fs = require('fs');
const R = '/Users/vivalapanda/git/pc98-assets/assets/room-icon/';
const cands = [['now_tuckedin', null], ['r2_ajar', R + 'out2/ajar_recolor.png'],
  ...['homefolder', 'homefolder2', 'door', 'house', 'cutaway'].map(n => [n, R + `out3/${n}_recolor.png`])];
(async () => {
  const b = await puppeteer.launch({executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new'});
  for (const [name, file] of cands) {
    const p = await b.newPage(); await p.setViewport({width: 1280, height: 900, deviceScaleFactor: 2});
    await p.setRequestInterception(true);
    p.on('request', r => {
      if (file && r.url().includes('/img/icons/room_recolor.png'))
        r.respond({status: 200, contentType: 'image/png', body: fs.readFileSync(file)});
      else r.continue();
    });
    await p.goto('http://localhost:8765/contact.html', {waitUntil: 'networkidle0'});
    await (await p.$('#left-sidebar')).screenshot({path: R + `out3/review/sidebar/desktop_${name}.png`});
    console.log('shot', name);
    await p.close();
  }
  await b.close();
})();
