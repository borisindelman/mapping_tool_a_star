import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

from mapping_tool_a_star import MappingGuiParams


class PlotCurveItemWithSelection(pg.PlotCurveItem):
    """
    Reimplement PlotCurveItem to enable item selection
    """
    __gui_params = MappingGuiParams()
    def __init__(self, plot_item_type=None, graph_ref=None, *args, **kargs):
        super().__init__(*args, **kargs)
        self.type = plot_item_type
        self.graph_ref = graph_ref
        self.pos = None
        if plot_item_type == self.__gui_params.MarkingLabels[1]:
            self.arrow = pg.CurveArrow(curve=self, pos=1.0, headLen=self.__gui_params.ArrowSize)

    def mouseClickEvent(self, ev):
        if not self.clickable or ev.button() != QtCore.Qt.LeftButton:
            return
        if self.mouseShape().contains(ev.pos()):
            self.pos = ev.scenePos()
            ev.accept()
            self.sigClicked.emit(self)