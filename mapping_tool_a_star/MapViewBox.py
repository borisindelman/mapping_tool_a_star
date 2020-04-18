import pyqtgraph as pg
from pyqtgraph.Qt import QtCore


class MapViewBox(pg.ViewBox):
    """
    Re-implement ViewBox to disable dragging and enable right click zoom out and left click Ginput
    """
    SIGNAL_left_click = QtCore.pyqtSignal(tuple)
    SIGNAL_right_click = QtCore.pyqtSignal(tuple)
    SIGNAL_dbl_left_click = QtCore.pyqtSignal()
    SIGNAL_diselect_item = QtCore.pyqtSignal()
    SIGNAL_delete_item = QtCore.pyqtSignal()
    SIGNAL_dbl_right_click = QtCore.pyqtSignal()

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        # Set Mouse to work in Pan Mode
        self.setMouseMode(self.PanMode)

    def mouseClickEvent(self, mouse_event):
        """
        Re-implement right-click to zoom out and left click similar to Ginput
        Args:
            mouse_event:

        Returns:

        """
        # Get Mouse position in the context of the image
        pos = mouse_event.scenePos()
        pos = self.mapSceneToView(pos)
        pos = (int(pos.x()), int(pos.y()))
        print(pos)
        if mouse_event.button() == QtCore.Qt.RightButton:
            self.SIGNAL_diselect_item.emit()
            self.SIGNAL_right_click.emit(pos)
            # pass
        elif mouse_event.button() == QtCore.Qt.MidButton:
            self.autoRange()
        elif mouse_event.button() == QtCore.Qt.LeftButton:
            self.SIGNAL_diselect_item.emit()
            self.SIGNAL_left_click.emit(pos)

    def mouseDoubleClickEvent(self, mouse_event):
        if mouse_event.button() == QtCore.Qt.LeftButton:
            self.SIGNAL_dbl_left_click.emit()
        elif mouse_event.button() == QtCore.Qt.RightButton:
            self.SIGNAL_dbl_right_click.emit()

    def mouseDragEvent(self, mouse_event):
        """
        Re-implement mouse-drag to disable dragging option
        Args:
            mouse_event:

        Returns:

        """
        if mouse_event.button() != QtCore.Qt.MidButton:
            mouse_event.ignore()
        else:
            super().mouseDragEvent(mouse_event)

    def keyPressEvent(self, keyboard_event):
        if keyboard_event.key() == QtCore.Qt.Key_Delete:
            print('delete request')
            self.SIGNAL_delete_item.emit()