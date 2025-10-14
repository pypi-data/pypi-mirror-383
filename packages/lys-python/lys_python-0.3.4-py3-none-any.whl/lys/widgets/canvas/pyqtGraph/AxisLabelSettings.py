
import warnings

from lys.Qt import QtGui
from lys.errors import NotSupportedWarning
from ..interface import CanvasAxisLabel, CanvasTickLabel

_opposite = {'Left': 'right', 'Right': 'left', 'Bottom': 'top', 'Top': 'bottom'}


class _PyqtgraphAxisLabel(CanvasAxisLabel):
    """Implementation of CanvasAxisLabel for pyqtgraph"""

    def _setAxisLabel(self, axis, text):
        ax = self.canvas().fig.getAxis(axis.lower())
        ax.setLabel(text)
        self.setAxisLabelVisible(axis, self.getAxisLabelVisible(axis))

    def _setAxisLabelVisible(self, axis, b):
        ax = self.canvas().fig.getAxis(axis.lower())
        ax.showLabel(b)

    def _setAxisLabelCoords(self, axis, pos):
        ax = self.canvas().fig.getAxis(axis.lower())
        if axis in ['Left', 'Right']:
            ax.setStyle(tickTextWidth=int(-pos * 100), autoExpandTextSpace=False)
        else:
            ax.setStyle(tickTextHeight=int(-pos * 100), autoExpandTextSpace=False)

    def _setAxisLabelFont(self, axis, font):
        ax = self.canvas().fig.getAxis(axis.lower())
        css = {'font-family': font.fontName, 'font-size': str(font.size) + "pt", "color": font.color}
        ax.setLabel(**css)
        self.setAxisLabel(axis, self.getAxisLabel(axis))


class _PyqtgraphTickLabel(CanvasTickLabel):
    """Implementation of CanvasTickLabel for pyqtgraph"""

    def _setTickLabelVisible(self, axis, tf, mirror=False):
        if mirror:
            ax = self.canvas().fig.getAxis(_opposite[axis])
        else:
            ax = self.canvas().fig.getAxis(axis.lower())
        ax.setStyle(showValues=tf)

    def _setTickLabelFont(self, axis, font):
        ax = self.canvas().fig.getAxis(axis.lower())
        ax.setStyle(tickFont=QtGui.QFont(font.fontName, font.size))
        if font.color != "black" and font.color != "#000000":
            warnings.warn("pyqtGraph does not support changing color of tick.", NotSupportedWarning)
