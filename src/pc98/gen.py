"""Reference generation through fal, reusing ~/animations' client, key and ledger code (nothing copied).

The key stays in ~/animations/secrets.txt, read by ~/animations/toolkit/py/keys.py; it is never printed, logged or
copied here. Spend goes to this workspace's own ledger (ledger.csv, tracked: it holds dates, endpoints, estimated
costs, output paths and prompts, no secrets) under this workspace's budget, so it can't block or be blocked by a film.

Generated images are references: you trace them, borrow a silhouette or ignore them. They never ship as pixels.
"""
import concurrent.futures as cf
import csv
from pathlib import Path
import importlib
import os
import sys
from collections import defaultdict

from .config import ROOT, ANIMATIONS

DEFAULT_BUDGET = 25.0     # dollars, for the whole workspace; raise it in the environment (PC98_FAL_BUDGET) on purpose

# Estimated $ per image (fal pricing pages, Oct 2026). fal has no balance API, so the ledger is only as honest as these.
PRICE = {
    'fal-ai/nano-banana-pro/edit': 0.15,
    'fal-ai/nano-banana-pro': 0.15,
    'fal-ai/nano-banana/edit': 0.039,
    'fal-ai/nano-banana': 0.039,
    'bytedance/seedream/v5/pro/edit': 0.0675,
}


def _fal():
    os.environ['FAL_LEDGER'] = str(ROOT / 'ledger.csv')
    os.environ['FAL_BUDGET'] = os.environ.get('PC98_FAL_BUDGET', str(DEFAULT_BUDGET))
    py = ANIMATIONS / 'toolkit' / 'py'
    if not (py / 'fal.py').exists():
        sys.exit(f'needs {py}/fal.py (set PC98_ANIMATIONS to the animations checkout)')
    if str(py) not in sys.path:
        sys.path.insert(0, str(py))
    return importlib.import_module('fal')


def generate(outs, prompt, endpoint='fal-ai/nano-banana-pro/edit', refs=(), aspect='1:1', extra=None, cost=None,
             max_spend=None, workers=4):
    """Generate one image per path in `outs` (skipping ones that exist). Returns the paths written."""
    fal = _fal()
    cost = PRICE.get(endpoint) if cost is None else cost
    if cost is None:
        sys.exit(f'no price known for {endpoint}: pass --cost so the ledger stays honest')
    todo = [o for o in outs if not os.path.exists(o)]
    est = cost * len(todo)
    if max_spend is not None and est > max_spend:
        sys.exit(f'refusing: {len(todo)} images x ${cost:.3f} = ${est:.2f} > --max ${max_spend:.2f}')
    if fal.spent() + est > fal.BUDGET * 0.99:
        sys.exit(f'refusing: ${est:.2f} would pass the workspace budget (spent ${fal.spent():.2f} of ${fal.BUDGET:.0f})')
    print(f'{len(todo)} images, est ${est:.2f} (workspace spent ${fal.spent():.2f} of ${fal.BUDGET:.0f})', flush=True)
    refs = [str(r) for r in refs]
    ex = dict(extra or {})

    def one(o):
        try:
            fal.job('image', endpoint, str(o), prompt, cost, refs=refs, aspect=aspect, extra=dict(ex))
            return f'ok   {o}'
        except Exception as e:      # noqa: BLE001 - report and carry on with the batch
            return f'FAIL {o}: {e}'
    done = []
    with cf.ThreadPoolExecutor(workers) as pool:
        for o, msg in zip(todo, pool.map(one, todo)):
            print(msg, flush=True)
            if msg.startswith('ok'):
                done.append(o)
    print(f'workspace spent ${fal.spent():.2f}', flush=True)
    return done


def ledger():
    """Spend per asset folder, and the total."""
    path = ROOT / 'ledger.csv'
    if not path.exists():
        print('no spend yet')
        return
    per = defaultdict(float)
    n = defaultdict(int)
    for r in csv.DictReader(open(path)):
        try:
            key = Path(r['out']).resolve().relative_to((ROOT / 'assets').resolve()).parts[0]
        except ValueError:
            key = '(other)'
        per[key] += float(r['cost']); n[key] += 1
    for k in sorted(per):
        print(f'{k:24s} {n[k]:4d} images  ${per[k]:.2f}')
    print(f'{"TOTAL":24s} {sum(n.values()):4d} images  ${sum(per.values()):.2f}  '
          f'(budget ${float(os.environ.get("PC98_FAL_BUDGET", DEFAULT_BUDGET)):.0f})')
