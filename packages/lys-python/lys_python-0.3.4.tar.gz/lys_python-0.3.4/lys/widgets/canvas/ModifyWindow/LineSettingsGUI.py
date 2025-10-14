import numpy as np
from matplotlib import cm
from matplotlib.lines import Line2D

from lys.Qt import QtCore, QtWidgets
from lys.widgets import ColormapSelection, ColorSelection, ScientificSpinBox
from lys.decorators import avoidCircularReference

from .FontGUI import FontSelector


class _LineColorSideBySideDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Select colormap')
        self.__initlayout()

    def __initlayout(self):
        h = QtWidgets.QHBoxLayout()
        h.addWidget(QtWidgets.QPushButton('O K', clicked=self.accept))
        h.addWidget(QtWidgets.QPushButton('CANCEL', clicked=self.reject))

        self.csel = ColormapSelection(opacity=False, log=False, reverse=True, gamma=False)

        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(self.csel)
        lay.addLayout(h)
        self.setLayout(lay)

    def getColor(self):
        return self.csel.currentColor()


class _LineStyleAdjustBox(QtWidgets.QGroupBox):
    __list = ['solid', 'dashed', 'dashdot', 'dotted', 'None']
    widthChanged = QtCore.pyqtSignal(float)
    styleChanged = QtCore.pyqtSignal(str)

    def __init__(self, canvas):
        super().__init__("Line")
        self.canvas = canvas
        self.__initlayout()

    def __initlayout(self):
        self.__combo = QtWidgets.QComboBox()
        self.__combo.addItems(self.__list)
        self.__combo.activated.connect(lambda: self.styleChanged.emit(self.__combo.currentText()))

        self.__spin1 = QtWidgets.QDoubleSpinBox()
        self.__spin1.valueChanged.connect(lambda: self.widthChanged.emit(self.__spin1.value()))

        layout = QtWidgets.QGridLayout()
        layout.addWidget(QtWidgets.QLabel('Type'), 0, 0)
        layout.addWidget(self.__combo, 1, 0)
        layout.addWidget(QtWidgets.QLabel('Width'), 0, 1)
        layout.addWidget(self.__spin1, 1, 1)
        self.setLayout(layout)

    def setWidth(self, width):
        self.__spin1.setValue(width)

    def setStyle(self, style):
        self.__combo.setCurrentText(style)

    def setEnabled(self, b):
        self.__combo.setEnabled(b)
        self.__spin1.setEnabled(b)


class _MarkerStyleAdjustBox(QtWidgets.QGroupBox):
    markerChanged = QtCore.pyqtSignal(str)
    markerFillingChanged = QtCore.pyqtSignal(str)
    markerSizeChanged = QtCore.pyqtSignal(float)
    markerThickChanged = QtCore.pyqtSignal(float)

    def __init__(self, canvas):
        super().__init__("Marker")
        self.canvas = canvas
        self.__list = list(Line2D.markers.values())
        self.__fillist = Line2D.fillStyles
        self.__initlayout()

    def __initlayout(self):
        gl = QtWidgets.QGridLayout()

        self.__combo = QtWidgets.QComboBox()
        self.__combo.addItems(self.__list)
        self.__combo.activated.connect(lambda: self.markerChanged.emit(self.__combo.currentText()))

        self.__spin1 = QtWidgets.QDoubleSpinBox()
        self.__spin1.valueChanged.connect(self.markerSizeChanged.emit)

        self.__fill = QtWidgets.QComboBox()
        self.__fill.addItems(self.__fillist)
        self.__fill.activated.connect(lambda: self.markerFillingChanged.emit(self.__fill.currentText()))

        self.__spin2 = QtWidgets.QDoubleSpinBox()
        self.__spin2.valueChanged.connect(self.markerThickChanged.emit)

        gl.addWidget(QtWidgets.QLabel('Type'), 0, 0)
        gl.addWidget(self.__combo, 1, 0)
        gl.addWidget(QtWidgets.QLabel('Size'), 2, 0)
        gl.addWidget(self.__spin1, 3, 0)
        gl.addWidget(QtWidgets.QLabel('Filling'), 0, 1)
        gl.addWidget(self.__fill, 1, 1)
        gl.addWidget(QtWidgets.QLabel('Thick'), 2, 1)
        gl.addWidget(self.__spin2, 3, 1)
        self.setLayout(gl)

    def setMarker(self, marker):
        self.__combo.setCurrentText(marker)

    def setMarkerFilling(self, filling):
        self.__fill.setCurrentText(filling)

    def setMarkerSize(self, size):
        self.__spin1.setValue(size)

    def setMarkerThick(self, thick):
        self.__spin2.setValue(thick)

    def setEnabled(self, b):
        self.__combo.setEnabled(b)
        self.__spin1.setEnabled(b)
        self.__fill.setEnabled(b)
        self.__spin2.setEnabled(b)


class AppearanceBox(QtWidgets.QWidget):
    def __init__(self, canvas):
        super().__init__()
        self._lines = []

        self._color = ColorSelection()
        self._color.colorChanged.connect(lambda c: [line.setColor(c) for line in self._lines])
        self._side = QtWidgets.QPushButton('Side by Side', clicked=self.__sidebyside)

        self._style = _LineStyleAdjustBox(canvas)
        self._style.widthChanged.connect(lambda w: [line.setWidth(w) for line in self._lines])
        self._style.styleChanged.connect(lambda s: [line.setStyle(s) for line in self._lines])

        self._marker = _MarkerStyleAdjustBox(canvas)
        self._marker.markerChanged.connect(lambda val: [line.setMarker(val) for line in self._lines])
        self._marker.markerSizeChanged.connect(lambda val: [line.setMarkerSize(val) for line in self._lines])
        self._marker.markerFillingChanged.connect(lambda val: [line.setMarkerFilling(val) for line in self._lines])
        self._marker.markerThickChanged.connect(lambda val: [line.setMarkerThick(val) for line in self._lines])

        layout_h1 = QtWidgets.QHBoxLayout()
        layout_h1.addWidget(QtWidgets.QLabel('Color'))
        layout_h1.addWidget(self._color)
        layout_h1.addWidget(self._side)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(layout_h1)
        layout.addWidget(self._style)
        layout.addWidget(self._marker)

        self.setLayout(layout)
        self.__setEnabled(False)

    def __sidebyside(self):
        d = _LineColorSideBySideDialog()
        res = d.exec_()
        if res == QtWidgets.QDialog.Accepted:
            c = d.getColor()
            if c == "" or c == "_r":
                return
            sm = cm.ScalarMappable(cmap=c)
            rgbas = sm.to_rgba(np.linspace(0, 1, len(self._lines)), bytes=True)
            rgbas = [('#{0:02x}{1:02x}{2:02x}').format(r, g, b) for r, g, b, a in rgbas]
            for line, color in zip(self._lines, rgbas):
                line.setColor(color)

    def setLines(self, lines):
        self._lines = lines
        if len(lines) != 0:
            self.__setEnabled(True)
            self._color.setColor(lines[0].getColor())
            self._style.setWidth(lines[0].getWidth())
            self._style.setStyle(lines[0].getStyle())
            self._marker.setMarker(lines[0].getMarker())
            self._marker.setMarkerSize(lines[0].getMarkerSize())
            self._marker.setMarkerFilling(lines[0].getMarkerFilling())
            self._marker.setMarkerThick(lines[0].getMarkerThick())
        else:
            self.__setEnabled(False)

    def __setEnabled(self, b):
        self._color.setEnabled(b)
        self._side.setEnabled(b)
        self._style.setEnabled(b)
        self._marker.setEnabled(b)


class _ErrorAdjustBox(QtWidgets.QGroupBox):
    def __init__(self, direction):
        super().__init__(direction + " error")
        self._data = []
        self.__initlayout()
        self._direction = direction

    def __initlayout(self):
        self.__type = QtWidgets.QComboBox()
        self.__type.addItems(["None", "Const", "Wave note"])
        self.__type.currentTextChanged.connect(self.__typeChanged)

        self.__value = ScientificSpinBox(valueChanged=self.__valueChanged)
        self.__valueLabel = QtWidgets.QLabel("Value")

        self.__note = QtWidgets.QLineEdit(textChanged=self.__noteChanged)
        self.__noteLabel = QtWidgets.QLabel("Key")

        layout = QtWidgets.QGridLayout()
        layout.addWidget(QtWidgets.QLabel("Type"), 0, 0)
        layout.addWidget(self.__valueLabel, 1, 0)
        layout.addWidget(self.__noteLabel, 2, 0)
        layout.addWidget(self.__type, 0, 1)
        layout.addWidget(self.__value, 1, 1)
        layout.addWidget(self.__note, 2, 1)
        self.setLayout(layout)
        self.__typeChanged("None")

    def __setEnabled(self, b):
        self.__type.setEnabled(b)
        self.__value.setEnabled(b)
        self.__note.setEnabled(b)

    def setData(self, data):
        self._data = data
        if len(data) != 0:
            self.__setEnabled(True)
            err = data[0].getErrorbar(self._direction)
            if err is None:
                self.__type.setCurrentText("None")
            elif isinstance(err, str):
                self.__type.setCurrentText("Wave note")
                self.__note.setText(err)
            else:
                self.__type.setCurrentText("Const")
                self.__value.setValue(err)
        else:
            self.__setEnabled(False)

    def __typeChanged(self, txt):
        self.__value.hide()
        self.__valueLabel.hide()
        self.__note.hide()
        self.__noteLabel.hide()
        if txt == "Const":
            self.__value.show()
            self.__valueLabel.show()
            self.__valueChanged()
        elif txt == "Wave note":
            self.__note.show()
            self.__noteLabel.show()
            self.__noteChanged()
        else:
            for d in self._data:
                d.setErrorbar(None, direction=self._direction)

    def __valueChanged(self):
        for d in self._data:
            d.setErrorbar(self.__value.value(), direction=self._direction)

    def __noteChanged(self):
        for d in self._data:
            d.setErrorbar(self.__note.text(), direction=self._direction)


class ErrorBox(QtWidgets.QWidget):
    def __init__(self, canvas):
        super().__init__()
        self.__cap = ScientificSpinBox(valueChanged=self.__capChanged)
        self.__cap.setRange(0, np.inf)
        h1 = QtWidgets.QHBoxLayout()
        h1.addWidget(QtWidgets.QLabel("Cap size"))
        h1.addWidget(self.__cap)

        self._x = _ErrorAdjustBox("x")
        self._y = _ErrorAdjustBox("y")
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(h1)
        layout.addWidget(self._y)
        layout.addWidget(self._x)
        layout.addStretch()
        self.setLayout(layout)

    def setEnabled(self, b):
        self.__cap.setEnabled(b)

    def setData(self, data):
        self._data = data
        if len(data) > 0:
            self.setEnabled(True)
            self.__cap.setValue(data[0].getCapSize())
        else:
            self.setEnabled(False)
        self._x.setData(data)
        self._y.setData(data)

    def __capChanged(self):
        for d in self._data:
            d.setCapSize(self.__cap.value())


class LegendBox(QtWidgets.QWidget):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.canvas.legendPositionChanged.connect(self.__updatePosition)
        self._lines = []
        self.__initlayout()

    def __initlayout(self):
        lay = QtWidgets.QVBoxLayout()

        self.__visible = QtWidgets.QCheckBox("Show legend", toggled=lambda b: [line.setLegendVisible(b) for line in self._lines])
        self.__label = QtWidgets.QLineEdit(textChanged=lambda t: [line.setLegendLabel(t) for line in self._lines])

        h = QtWidgets.QHBoxLayout()
        h.addWidget(QtWidgets.QLabel('Label'))
        h.addWidget(self.__label)

        self.__font = FontSelector('Font')
        self.__font.fontChanged.connect(lambda: self.canvas.setLegendFont(**self.__font.getFont()))
        self.__font.setFont(**self.canvas.getLegendFont())

        lay.addWidget(self.__visible)
        lay.addLayout(h)
        lay.addWidget(self.__appearanceBox())
        lay.addWidget(self.__positionBox())
        lay.addWidget(self.__font)
        lay.addStretch()
        self.setLayout(lay)

    def __positionBox(self):
        pos = self.canvas.getLegendPosition()
        self.__x = QtWidgets.QDoubleSpinBox(valueChanged=self.__changePosition)
        self.__x.setRange(-1, 2)
        self.__x.setSingleStep(0.05)
        self.__x.setDecimals(5)
        self.__y = QtWidgets.QDoubleSpinBox(valueChanged=self.__changePosition)
        self.__y.setRange(-1, 2)
        self.__y.setSingleStep(0.05)
        self.__y.setDecimals(5)
        self.__x.setValue(pos[0])
        self.__y.setValue(pos[1])

        h = QtWidgets.QGridLayout()
        h.addWidget(QtWidgets.QLabel("x"), 0, 0)
        h.addWidget(QtWidgets.QLabel("y"), 0, 1)
        h.addWidget(self.__x, 1, 0)
        h.addWidget(self.__y, 1, 1)

        box = QtWidgets.QGroupBox("Position")
        box.setLayout(h)
        return box

    @avoidCircularReference
    def __updatePosition(self, pos):
        self.__x.setValue(pos[0])
        self.__y.setValue(pos[1])

    def __appearanceBox(self):
        self.__frameVisible = QtWidgets.QCheckBox("Show Frame")
        self.__frameVisible.setChecked(self.canvas.getLegendFrameVisible())
        self.__frameVisible.toggled.connect(self.canvas.setLegendFrameVisible)
        g = QtWidgets.QGridLayout()
        g.addWidget(self.__frameVisible, 0, 0)

        box = QtWidgets.QGroupBox("Appearance")
        box.setLayout(g)
        return box

    def __changePosition(self):
        self.canvas.setLegendPosition((self.__x.value(), self.__y.value()))

    def setData(self, lines):
        self._lines = lines
        if len(lines) != 0:
            self.__setEnabled(True)
            self.__visible.setChecked(lines[0].getLegendVisible())
            self.__label.setText(lines[0].getLegendLabel())
        else:
            self.__setEnabled(False)

    def __setEnabled(self, b):
        self.__visible.setEnabled(b)
        self.__label.setEnabled(b)
