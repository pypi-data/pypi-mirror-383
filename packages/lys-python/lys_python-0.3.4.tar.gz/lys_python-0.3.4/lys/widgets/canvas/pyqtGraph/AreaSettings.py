from lys.Qt import QtWidgets
from ..interface import CanvasMargin, CanvasSize


class _PyqtGraphMargin(CanvasMargin):
    """Implementation of CanvasMargin for pyqtGraph"""

    def _setMargin(self, left, right, top, bottom):
        self.canvas().setContentsMargins(int(left), int(right), int(top), int(bottom))


_unit = 2.54 / QtWidgets.QDesktopWidget().physicalDpiX()  # cm/pixel


class _PyqtGraphCanvasSize(CanvasSize):
    """Implementation of CanvasSize for pyqtGraph"""

    def _setAuto(self, axis):
        self._adjust()

    def _setAbsolute(self, type, value):
        if type == "Width":
            self._setW(value)
        else:
            self._setH(value)
        self._adjust()

    def _setAspect(self, type, aspect):
        size = self._getSize()
        if type == "Width":
            self._setW(size[1] * aspect)
        else:
            self._setH(size[0] * aspect)
        self._adjust()

    def _getSize(self):
        h = self.canvas().fig.getAxis('left').height()
        w = self.canvas().fig.getAxis('bottom').width()
        return (w * _unit, h * _unit)

    def _setW(self, width):
        fig = self.canvas().fig
        fig.resize(width / _unit + 2 + fig.getAxis('left').width() + fig.getAxis('right').width(), fig.height())

    def _setH(self, height):
        fig = self.canvas().fig
        fig.resize(fig.width(), height / _unit + 2 + fig.getAxis('bottom').height() + fig.getAxis('top').height())

    def _adjust(self):
        size = self.canvas().fig.size()
        self.canvas().resize(int(size.width()), int(size.height()))
        self.canvas().adjustSize()
        # self.canvas().draw()
