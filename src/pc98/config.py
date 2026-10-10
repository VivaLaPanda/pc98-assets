"""Where things are. Override any of these with environment variables."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]                      # this workspace
def _site() -> Path:
    """The site checkout: $PC98_SITE, else the Mac's (~/git) or rodney's (~/code), whichever exists."""
    if os.environ.get('PC98_SITE'):
        return Path(os.environ['PC98_SITE']).expanduser()
    for p in ('~/git/vivalapanda.moe', '~/code/vivalapanda.moe'):
        if Path(p).expanduser().exists():
            return Path(p).expanduser()
    return Path('~/git/vivalapanda.moe').expanduser()


SITE = _site()
ANIMATIONS = Path(os.environ.get('PC98_ANIMATIONS', '~/animations')).expanduser()
CHROME = os.environ.get('PC98_CHROME', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
ASSETS = ROOT / 'assets'

# The site's sidebar, measured in Chrome (see README, "The sidebar"): each icon is drawn 72 px wide with smooth
# (bilinear) scaling, so a 48x48 icon shows at 1.5x and a 32x32 one at 2.25x. The sidebar is mint #00eebb.
ICON_PX = 48
ICON_SHOWN_PX = 72
SIDEBAR_BG = (0x00, 0xEE, 0xBB)


def site_file(rel):
    p = SITE / rel
    if not p.exists():
        raise FileNotFoundError(f'{p} (set PC98_SITE to the vivalapanda.moe checkout)')
    return p


def font(size=16):
    """The site's own PC-98 font, for labels on sheets. Falls back to PIL's default."""
    from PIL import ImageFont
    try:
        return ImageFont.truetype(str(SITE / 'fonts/pc-9800.ttf'), size)
    except OSError:
        return ImageFont.load_default(size)
