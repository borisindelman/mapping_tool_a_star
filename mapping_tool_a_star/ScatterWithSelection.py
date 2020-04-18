import pyqtgraph as pg


class ScatterWithSelection(pg.ScatterPlotItem):
    """
    Re-implement Scatter Plot item to enable item selection
    """
    def __init__(self, plot_item_type=None, graph_ref=None, *args, **kargs):
        super().__init__(*args, **kargs)
        self.type = plot_item_type
        self.graph_ref = graph_ref
