"""In-context preview: the real site page, with candidate icons in its real sidebar, screenshotted in headless Chrome.

A local server serves the site checkout at / (read-only) and this workspace at /__ws/, so the page loads the site's
own CSS, frame, fonts and neighbouring icons. The page's sidebar markup is swapped for the layout you ask for; nothing
in the site repo is written.

Any site file can also be overridden by a workspace file (--override img/background-frame.png=assets/x/out/frame.png):
the server answers that URL with your file, so frames, scenes, sprites and icons are all previewed in place on any
page (--page explore/frontdesk.html).

Two ways to place icons:
- swaps (the default way): keep the page's own sidebar, whatever layout the site has today, and replace one icon's
  image, e.g. --swap blog=assets/blog-icon/out/newspaper_recolor.png. This is the faithful view.
- an explicit layout: icons in reading order, two per row. Each is a site icon name ('computer' ->
  /img/icons/computer_recolor.png), a path to a PNG, or '-' for an empty slot. --pad sets the vertical padding.
"""
import base64
import http.server
import json
import os
import re
import subprocess
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

import websocket
from PIL import Image

from .config import ROOT, SITE, CHROME, site_file

FRAME_W, FRAME_H = 1280, 800
SIDEBAR = (6, 439, 250, 787)      # #left-sidebar in frame pixels (css/style.css)


OVERRIDES = {}      # '/img/x.png' -> Path: served instead of the site's file


class _Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = path.split('?', 1)[0].split('#', 1)[0]
        if path in OVERRIDES:
            return str(OVERRIDES[path])
        if path.startswith('/__ws/'):
            base, rel = ROOT, path[len('/__ws/'):]
        else:
            base, rel = SITE, path.lstrip('/')
        p = (base / rel).resolve()
        if base.resolve() not in p.parents and p != base.resolve():
            return str(base / '__forbidden__')
        return str(p)

    def log_message(self, *a):
        pass


def set_overrides(overrides):
    """{site path: workspace file}. Site paths are relative to the site root ('img/background-frame.png')."""
    OVERRIDES.clear()
    for k, v in (overrides or {}).items():
        p = Path(v).resolve()
        if not p.exists():
            raise SystemExit(f'--override: {v} does not exist')
        if not (SITE / k.lstrip('/')).exists():
            print(f'note: {k} is not in the site yet (a new file)')
        OVERRIDES['/' + k.lstrip('/')] = p


def serve():
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), _Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def _icon_url(tok):
    if tok == '-':
        return None
    p = Path(tok)
    if not p.is_absolute():
        p = (Path.cwd() / tok)
    if p.exists():
        p = p.resolve()
        try:
            return '/__ws/' + str(p.relative_to(ROOT.resolve()))
        except ValueError:
            raise SystemExit(f'{tok}: candidates must live inside the workspace ({ROOT})')
    for name in (f'img/icons/{tok}_recolor.png', f'img/icons/{tok}.png', tok):
        if (SITE / name).exists():
            return '/' + name
    raise SystemExit(f'no icon {tok!r}: not a file, and not img/icons/{tok}[_recolor].png in the site')


def _replace_block(html, start_pat):
    """Find the element opening at start_pat and return (start, end) of the whole element (div nesting aware)."""
    m = re.search(start_pat, html)
    if not m:
        raise SystemExit('could not find the left sidebar in the page')
    i, depth = m.end(), 1
    for t in re.finditer(r'<(/?)div\b', html[i:]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return m.start(), i + t.start() + html[i + t.start():].index('>') + 1
    raise SystemExit('unbalanced sidebar markup')


def page_html(icons=None, page='contact.html', dialog=None, swaps=None, pad=None):
    """icons: an explicit layout (two per row), or None to keep the page's own sidebar. swaps: {site icon file name or
    stem: replacement token}, applied to whatever sidebar is used (e.g. {'blog_recolor.png': 'out/x_recolor.png'})."""
    html = site_file(page).read_text()
    s, e = _replace_block(html, r'<div class="subwindow" id="left-sidebar">')
    side = html[s:e]
    if icons:
        rows = [icons[i:i + 2] for i in range(0, len(icons), 2)]
        parts = ['<div class="subwindow" id="left-sidebar">']
        for r in rows:
            parts.append('<div class="nav-row">')
            for tok in r + ['-'] * (2 - len(r)):
                url = _icon_url(tok)
                parts.append(f'<a class="navbutton" href="#"><img src={url!r}></a>' if url
                             else '<span class="navbutton nav-empty"></span>')
            parts.append('</div>')
        parts.append('</div>')
        side = '\n'.join(parts)
    for old, new in (swaps or {}).items():
        old = old if old.endswith('.png') else f'{old}_recolor.png'
        pat = r'(src=["\'])[^"\']*/' + re.escape(old) + r'(["\'])'
        side, n = re.subn(pat, lambda m: m.group(1) + _icon_url(new) + m.group(2), side)
        if not n:
            raise SystemExit(f'--swap: {old} is not in {page}\'s sidebar')
    html = html[:s] + side + html[e:]
    css = ['body{margin:0!important;overflow:hidden} .main-container{margin:0!important}',
           '#boot-screen{display:none!important} .main-window{display:block!important}']
    if pad is not None:
        css.append(f'.nav-row>.navbutton{{padding:{pad}px 25px!important}}')
    html = html.replace('</head>', f'<style>{" ".join(css)}</style>\n</head>', 1)
    if dialog:
        html = re.sub(r'(<div class="text-container">).*?(</div>)',
                      lambda m: f'{m.group(1)}<p class="speaker-text">Ｐａｎｄａ</p><p class="dialog-text">{dialog}</p>{m.group(2)}',
                      html, count=1, flags=re.S)
    return html


class Chrome:
    """Headless Chrome driven over the DevTools protocol: one browser per preview, a throwaway profile, and each shot
    taken after the load event and document.fonts.ready (the dialog uses the PC-98 web font). Chrome's own
    `--screenshot` flag hung on this machine after an update; this path doesn't depend on it."""

    def __enter__(self):
        import shutil  # noqa: F401  (used in __exit__)
        self.prof = tempfile.mkdtemp(prefix='pc98-chrome-')
        self.proc = subprocess.Popen(
            [CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--mute-audio', '--no-first-run',
             '--no-default-browser-check', '--disable-extensions', f'--user-data-dir={self.prof}',
             '--remote-debugging-port=0', 'about:blank'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        f = Path(self.prof) / 'DevToolsActivePort'
        for _ in range(400):
            if f.exists() and f.read_text().strip():
                break
            time.sleep(0.05)
        else:
            self.__exit__(None, None, None)
            raise SystemExit('Chrome did not start (PC98_CHROME?)')
        port = int(f.read_text().split()[0])
        targets = json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json', timeout=10))
        page = next(t for t in targets if t['type'] == 'page')
        self.ws = websocket.create_connection(page['webSocketDebuggerUrl'], timeout=60, suppress_origin=True)
        self.n = 0
        self.call('Page.enable')
        return self

    def call(self, method, **params):
        self.n += 1
        self.ws.send(json.dumps({'id': self.n, 'method': method, 'params': params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get('id') == self.n:
                if 'error' in msg:
                    raise RuntimeError(f'{method}: {msg["error"]}')
                return msg.get('result', {})

    def wait(self, event):
        while True:
            if json.loads(self.ws.recv()).get('method') == event:
                return

    def shot(self, url, out, scale=1, w=None, h=None):
        self.call('Emulation.setDeviceMetricsOverride', width=w or FRAME_W, height=h or FRAME_H,
                  deviceScaleFactor=scale, mobile=False)
        self.call('Page.navigate', url=url)
        self.wait('Page.loadEventFired')
        self.call('Runtime.evaluate', awaitPromise=True,
                  expression='document.fonts.ready.then(() => new Promise(r => setTimeout(r, 250)))')
        data = self.call('Page.captureScreenshot', format='png')['data']
        Path(out).write_bytes(base64.b64decode(data))
        return out

    def __exit__(self, *exc):
        import shutil
        try:
            self.ws.close()
        except Exception:     # noqa: BLE001
            pass
        self.proc.terminate()
        try:
            self.proc.wait(10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        shutil.rmtree(self.prof, ignore_errors=True)


def shoot(url, out, scale=1):
    """One screenshot (starts and stops a browser; use `with Chrome() as c: c.shot(...)` for several)."""
    with Chrome() as c:
        return c.shot(url, out, scale)


def compare(slot, candidates, out, page='contact.html', scale=2, zoom=1, labels=None, overrides=None):
    """One screenshot per candidate, each swapped into `slot` of the page's own sidebar, and their sidebars side by
    side in one image (at `scale` device pixels per CSS pixel, so 2 = a retina screen). Returns the path."""
    from PIL import ImageDraw
    from .config import font
    set_overrides(overrides)
    srv = serve()
    port = srv.server_address[1]
    tmp = ROOT / '.preview'
    tmp.mkdir(exist_ok=True)
    crops = []
    try:
        with Chrome() as chrome:
            for c in candidates:
                fd, name = tempfile.mkstemp(suffix='.html', dir=tmp)
                os.close(fd)
                Path(name).write_text(page_html(None, page, None, {slot: c} if c != '-' else {}))
                shot = Path(name).with_suffix('.png')
                chrome.shot(f'http://127.0.0.1:{port}/__ws/.preview/{Path(name).name}', str(shot), scale)
                x0, y0, x1, y1 = SIDEBAR
                im = Image.open(shot).convert('RGB').crop((x0 * scale, y0 * scale, x1 * scale, y1 * scale))
                if zoom != 1:
                    im = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
                crops.append(im)
                Path(name).unlink(missing_ok=True)
                shot.unlink(missing_ok=True)
    finally:
        srv.shutdown()
    w, h = crops[0].size
    sheet = Image.new('RGB', (len(crops) * (w + 12), h + 28), (0, 0, 0))
    d = ImageDraw.Draw(sheet)
    for i, (im, c) in enumerate(zip(crops, candidates)):
        sheet.paste(im, (i * (w + 12), 28))
        lab = (labels[i] if labels else ('(as the site is)' if c == '-' else Path(c).stem.replace('_recolor', '')))
        d.text((i * (w + 12) + 4, 6), lab, fill=(255, 170, 187), font=font(16))
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return str(out)


def preview(icons, out_dir, page='contact.html', dialog=None, zoom=3, swaps=None, pad=None, overrides=None):
    """Writes context.png (the frame at 1x, as most screens show it), context@2x.png (as a retina screen shows it)
    and sidebar.png (the sidebar from both, enlarged with hard pixels so you can see exactly what Chrome drew).
    Returns the paths."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    set_overrides(overrides)
    srv = serve()
    port = srv.server_address[1]
    tmp = ROOT / '.preview'
    tmp.mkdir(exist_ok=True)
    fd, name = tempfile.mkstemp(suffix='.html', dir=tmp)
    os.close(fd)
    Path(name).write_text(page_html(icons, page, dialog, swaps, pad))
    url = f'http://127.0.0.1:{port}/__ws/.preview/{Path(name).name}'
    try:
        with Chrome() as chrome:
            a = chrome.shot(url, str(out_dir / 'context.png'), 1)
            b = chrome.shot(url, str(out_dir / 'context@2x.png'), 2)
    finally:
        srv.shutdown()
        Path(name).unlink(missing_ok=True)
    x0, y0, x1, y1 = SIDEBAR
    one = Image.open(a).convert('RGB').crop((x0, y0, x1, y1))
    two = Image.open(b).convert('RGB').crop((x0 * 2, y0 * 2, x1 * 2, y1 * 2))
    one = one.resize((one.width * zoom, one.height * zoom), Image.NEAREST)
    two = two.resize((two.width * zoom // 2, two.height * zoom // 2), Image.NEAREST)
    side = Image.new('RGB', (one.width + two.width + 24, one.height), (0, 0, 0))
    side.paste(one, (0, 0)); side.paste(two, (one.width + 24, 0))
    side.save(out_dir / 'sidebar.png')
    return [a, b, str(out_dir / 'sidebar.png')]
