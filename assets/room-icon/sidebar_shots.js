const puppeteer = require('/Users/vivalapanda/animations/toolkit/render/node_modules/puppeteer-core');
const fs = require('fs');
const OUT = '/Users/vivalapanda/git/pc98-assets/assets/room-icon/out2/';
const cands = ['old', 'tuckedin', 'nightwindow', 'ajar', 'moonpanda'];
(async () => {
  const b = await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless:'new'});
  for (const [tag, vp] of [['desktop', {width:1280, height:900, deviceScaleFactor:2}]]) {
    for (const c of cands) {
      const p = await b.newPage(); await p.setViewport(vp);
      await p.setRequestInterception(true);
      p.on('request', r => {
        if (c !== 'old' && r.url().includes('/img/icons/room_recolor.png'))
          r.respond({status:200, contentType:'image/png', body: fs.readFileSync(OUT + c + '_recolor.png')});
        else r.continue();
      });
      await p.goto('http://localhost:8765/contact.html', {waitUntil:'networkidle0'});
      const el = await p.$('#left-sidebar');
      const box = await el.boundingBox();
      console.log(tag, c, JSON.stringify(box), await p.$eval('#left-sidebar img[src*="room"]', i => [i.naturalWidth, Math.round(i.getBoundingClientRect().width)]));
      await el.screenshot({path: OUT + `review/sidebar/${tag}_${c}.png`});
      await p.close();
    }
  }
  await b.close();
})();
