"""panda-room is a scene, not an icon: paint.py paints it (a hand paint-over of refs/underlay.png, one passage at a
time) and export.py writes the finals and review sheets to out/final/. `uv run pc98 render panda-room` runs the export;
`uv run python assets/panda-room/paint.py <passage>` paints up to one passage and writes a progress sheet beside the
underlay. NOTES.md says how it was made and which techniques worked."""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
runpy.run_path(str(HERE / 'export.py'), run_name='__main__')
