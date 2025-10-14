from pathlib import Path
import anywidget
import traitlets as t

_JS = (Path(__file__).with_name("widget.js")).read_text(encoding="utf-8")


class SsePyWidget(anywidget.AnyWidget):
    """minimal any widget-based widget"""

    _esm = _JS

    width = t.Int(640).tag(sync=True)
    height = t.Int(480).tag(sync=True)
    color = t.Unicode("lightblue").tag(sync=True)
