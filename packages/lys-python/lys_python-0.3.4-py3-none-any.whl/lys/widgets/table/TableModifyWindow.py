from lys.Qt import QtWidgets
from lys.widgets import AxisSelectionLayout, IndiceSelectionLayout

from .. import LysSubWindow


class TableModifyWindow(LysSubWindow):
    def __init__(self, parent, table):
        super().__init__()
        self._parent = parent
        self.attach(parent)
        self.attachTo()
        self.__initlayout(table)
        self.resize(300, 300)

    def __initlayout(self, table):
        self.setWindowTitle("Table Modify Window")
        self._widget = TableModifyWidget(table)
        self.setWidget(self._widget)
        self.adjustSize()
        self.updateGeometry()
        self.show()

    def setData(self, data):
        self._view.setData(data)


class TableModifyWidget(QtWidgets.QTabWidget):
    def __init__(self, table):
        super().__init__()
        self.__initlayout(table)

    def __initlayout(self, table):
        self._view = _viewTab(table)
        self.addTab(self._view, "View")

    def setData(self, data):
        self._view.setData(data)


class _viewTab(QtWidgets.QWidget):
    def __init__(self, table):
        super().__init__()
        self._table = table
        self.__flg = False
        self.__initlayout()
        self.__updateWidgets()
        self.__updateStates()

    def __initlayout(self):
        self._combo = QtWidgets.QComboBox()
        self._combo.currentTextChanged.connect(self.__stateChanged)
        h1 = QtWidgets.QHBoxLayout()
        h1.addWidget(QtWidgets.QLabel("View type"))
        h1.addWidget(self._combo)

        self._axis1 = AxisSelectionLayout("Horizontal axis")
        self._axis2 = AxisSelectionLayout("Vertical axis")
        self._axis1.axisChanged.connect(self.__axisChanged)
        self._axis2.axisChanged.connect(self.__axisChanged)

        self._indices = IndiceSelectionLayout()
        self._indices.valueChanged.connect(self.__stateChanged)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(h1)
        layout.addLayout(self._axis1)
        layout.addLayout(self._axis2)
        layout.addLayout(self._indices)
        layout.addStretch()
        self.setLayout(layout)

    def __updateWidgets(self):
        self.__flg = True
        self._data = self._table.getData().data
        self._combo.clear()
        self._combo.addItem("Data")
        self._combo.addItems(["Axis" + str(i) for i in range(self._data.ndim)])

        self._axis1.setDimension(self._data.ndim)
        self._axis2.setDimension(self._data.ndim)
        self._indices.setShape(self._data.shape)
        self.__flg = False

    def __updateStates(self):
        self.__flg = True
        slc = self._table.getSlice()
        if isinstance(slc, int) or self._data.ndim <= 2:
            self._axis1.setEnabled(False)
            self._axis2.setEnabled(False)
            self._indices.setEnabled([False for _ in range(self._data.ndim)])
        else:
            self._axis1.setEnabled(True)
            self._axis2.setEnabled(True)
            self._selected = [i for i, s in enumerate(slc) if isinstance(s, slice)]
            self._axis1.setAxis(self._selected[0])
            self._axis2.setAxis(self._selected[1])
            self._indices.setEnabled([isinstance(s, int) for s in slc])
            self._indices.setValues([s if isinstance(s, int) else 0 for s in slc])
        self.__flg = False

    def __axisChanged(self):
        if self.__flg:
            return
        if self._axis2.getAxis() == self._axis1.getAxis():
            self.__flg = True
            self._axis1.setAxis(self._selected[0])
            self._axis2.setAxis(self._selected[1])
            self.__flg = False
            return
        self._selected = [self._axis1.getAxis(), self._axis2.getAxis()]
        self.__stateChanged()

    def __stateChanged(self):
        if self.__flg:
            return
        if self._combo.currentText() != "Data":
            self._table.setSlice(self._combo.currentIndex() - 1)
        elif self._data.ndim == 1:
            self._table.setSlice([slice(None)])
        elif self._data.ndim == 2:
            self._table.setSlice([slice(None), slice(None)])
        elif self._data.ndim > 2:
            slc = [slice(None)] * self._data.ndim
            for i in range(self._data.ndim):
                if i not in self._selected:
                    slc[i] = self._indices.getIndices()[i]
            self._table.setSlice(slc)
        self.__updateStates()
