// The real sidebar of contact.html (http://localhost:8765, `microtemplate watch`) at 2x, in the reshuffled layout
// (globe | envelope / CD | newspaper / recipes | home folder, 72 px), each candidate swapped in for
// /img/icons/recipes_recolor.png by request interception. Nothing in the site repo changes.
const puppeteer = require('/Users/vivalapanda/animations/toolkit/render/node_modules/puppeteer-core');
const fs = require('fs');
const R = '/Users/vivalapanda/git/pc98-assets/assets/recipes-icon/out/';
const cands = ['book', 'donburi', 'pancakes'];
(async () => {
  const b = await puppeteer.launch({executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new'});
  for (const c of cands) {
    const p = await b.newPage(); await p.setViewport({width: 1280, height: 900, deviceScaleFactor: 2});
    await p.setRequestInterception(true);
    p.on('request', r => {
      if (r.url().endsWith('/img/icons/recipes_recolor.png'))
        r.respond({status: 200, contentType: 'image/png', body: fs.readFileSync(R + c + '_recolor.png')});
      else r.continue();
    });
    await p.goto('http://localhost:8765/contact.html', {waitUntil: 'networkidle0'});
    const sizes = await p.evaluate(() => [...document.querySelectorAll('#left-sidebar img')].map(i =>
      i.getAttribute('src').split('/').pop() + ' ' + Math.round(i.getBoundingClientRect().width)));
    console.log(c, JSON.stringify(sizes));
    await (await p.$('#left-sidebar')).screenshot({path: R + `review/sidebar/desktop_${c}.png`});
    await p.close();
  }
  await b.close();
})();
