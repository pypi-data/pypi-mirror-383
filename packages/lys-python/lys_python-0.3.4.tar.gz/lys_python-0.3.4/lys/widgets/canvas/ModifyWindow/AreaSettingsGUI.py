import weakref

from lys.Qt import QtWidgets

from .AxisSettingsGUI import AxisSelectionWidget


class MarginAdjustBox(QtWidgets.QGroupBox):
    def __init__(self, canvas):
        super().__init__("Margin")
        self.canvas = canvas
        self._initlayout(canvas)

    def _initlayout(self, canvas):
        self._vals = [QtWidgets.QDoubleSpinBox() for _ in range(4)]
        for v in self._vals:
            v.setRange(0, 1)
            v.setSingleStep(0.05)
            v.setSpecialValueText("Auto")
            v.valueChanged.connect(self._valueChanged)

        m = canvas.getMargin(raw=True)
        self._vals[0].setValue(m[0])
        if m[1] == 0:
            self._vals[1].setValue(0)
        else:
            self._vals[1].setValue(1 - m[1])
        self._vals[2].setValue(m[2])
        if m[3] == 0:
            self._vals[3].setValue(0)
        else:
            self._vals[3].setValue(1 - m[3])

        grid = QtWidgets.QGridLayout()
        grid.addWidget(QtWidgets.QLabel('Left'), 0, 0)
        grid.addWidget(QtWidgets.QLabel('Right'), 0, 2)
        grid.addWidget(QtWidgets.QLabel('Bottom'), 1, 0)
        grid.addWidget(QtWidgets.QLabel('Top'), 1, 2)
        grid.addWidget(self._vals[0], 0, 1)
        grid.addWidget(self._vals[1], 0, 3)
        grid.addWidget(self._vals[2], 1, 1)
        grid.addWidget(self._vals[3], 1, 3)
        self.setLayout(grid)

    def _valueChanged(self):
        m0 = self._vals[0].value()
        m1 = self._vals[1].value()
        if m1 != 0:
            m1 = 1 - m1
        m2 = self._vals[2].value()
        m3 = self._vals[3].value()
        if m3 != 0:
            m3 = 1 - m3
        self.canvas.setMargin(m0, m1, m2, m3)


class ResizeBox(QtWidgets.QGroupBox):
    class _AreaBox(QtWidgets.QGroupBox):
        def __init__(self, title, canvas, axis):
            super().__init__(title)
            self._axis = axis
            self.canvas = canvas
            self._initlayout(canvas)
            self.__loadstate()

        def setPartner(self, partner):
            self._partner = weakref.ref(partner)

        def _initlayout(self, canvas):
            self.cw = QtWidgets.QComboBox()
            self.cw.addItems(['Auto', 'Absolute', 'Per Unit', 'Aspect', 'Plan'])
            self.cw.activated.connect(self.__ModeChanged)

            self.spin1 = QtWidgets.QDoubleSpinBox()
            self.spin1.valueChanged.connect(self.__Changed)
            self.spin1.setDecimals(5)
            self.lab1 = QtWidgets.QLabel(' * Height')
            tmp1 = QtWidgets.QHBoxLayout()
            tmp1.addWidget(self.spin1)
            tmp1.addWidget(self.lab1)

            self.lab2_1 = QtWidgets.QLabel('*')
            self.lab2_2 = QtWidgets.QLabel('Range')
            self.combo2 = AxisSelectionWidget(canvas)
            self.combo2.activated.connect(self.__Changed)
            tmp2 = QtWidgets.QHBoxLayout()
            tmp2.addWidget(self.lab2_1)
            tmp2.addWidget(self.combo2)
            tmp2.addWidget(self.lab2_2)

            self.lab3_1 = QtWidgets.QLabel('/')
            self.lab3_2 = QtWidgets.QLabel('Range')
            self.combo3 = AxisSelectionWidget(canvas)
            self.combo3.activated.connect(self.__Changed)
            tmp3 = QtWidgets.QHBoxLayout()
            tmp3.addWidget(self.lab3_1)
            tmp3.addWidget(self.combo3)
            tmp3.addWidget(self.lab3_2)

            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(self.cw)
            layout.addLayout(tmp1)
            layout.addLayout(tmp2)
            layout.addLayout(tmp3)
            self.setLayout(layout)

        def __loadstate(self):
            self.__loadflg = True
            lis1 = ['Auto', 'Absolute', 'Per Unit', 'Aspect', 'Plan']
            if self._axis == 0:
                param = self.canvas.getSizeParams('Width')
            else:
                param = self.canvas.getSizeParams('Height')
            self.cw.setCurrentIndex(lis1.index(param['mode']))
            self.spin1.setValue(param['value'])
            lis2 = self.canvas.axisList()
            try:
                self.combo2.setCurrentIndex(lis2.index(param['value1']))
            except Exception:
                self.combo2.setCurrentIndex(lis2.index('Left'))
            try:
                self.combo3.setCurrentIndex(lis2.index(param['value2']))
            except Exception:
                self.combo3.setCurrentIndex(lis2.index('Bottom'))
            self._setLook(param['mode'])
            self.__loadflg = False

        def __ModeChanged(self):
            if self.__loadflg:
                return
            self.__loadflg = True
            type = self.cw.currentText()
            size = self.canvas.getCanvasSize()
            if type == 'Absolute':
                if self._axis == 0:
                    self.spin1.setValue(size[0])
                else:
                    self.spin1.setValue(size[1])
            if type == 'Aspect':
                if self._axis == 0:
                    self.spin1.setValue(size[0] / size[1])
                else:
                    self.spin1.setValue(size[1] / size[0])
            if type == 'Per Unit':
                if self._axis == 0:
                    self.combo2.setCurrentIndex(self.canvas.axisList().index('Bottom'))
                    ran = self.canvas.getAxisRange('Bottom')
                    self.spin1.setValue(size[0] / abs(ran[1] - ran[0]))
                else:
                    self.combo2.setCurrentIndex(self.canvas.axisList().index('Left'))
                    ran = self.canvas.getAxisRange('Left')
                    self.spin1.setValue(size[1] / abs(ran[1] - ran[0]))
            if type == 'Plan':
                if self._axis == 0:
                    self.combo2.setCurrentIndex(self.canvas.axisList().index('Bottom'))
                    self.combo3.setCurrentIndex(self.canvas.axisList().index('Left'))
                    ran_l = self.canvas.getAxisRange('Left')
                    ran_b = self.canvas.getAxisRange('Bottom')
                    self.spin1.setValue(size[0] / size[1] * abs(ran_l[1] - ran_l[0]) / abs(ran_b[1] - ran_b[0]))
                else:
                    self.combo2.setCurrentIndex(self.canvas.axisList().index('Left'))
                    self.combo3.setCurrentIndex(self.canvas.axisList().index('Bottom'))
                    ran_l = self.canvas.getAxisRange('Left')
                    ran_b = self.canvas.getAxisRange('Bottom')
                    self.spin1.setValue(size[1] / size[0] * abs(ran_b[1] - ran_b[0]) / abs(ran_l[1] - ran_l[0]))
            self.__loadflg = False
            self.__Changed()

        def __Changed(self):
            if self.__loadflg:
                return
            type = self.cw.currentText()
            self._setPartnerComboBox(type)
            self._setLook(type)
            val = self.spin1.value()
            axis1 = self.combo2.currentText()
            axis2 = self.combo3.currentText()
            if self._axis == 0:
                self.canvas.setCanvasSize('Width', mode=type, value=val, axis1=axis1, axis2=axis2)
            else:
                self.canvas.setCanvasSize('Height', mode=type, value=val, axis1=axis1, axis2=axis2)

        def _setPartnerComboBox(self, type):
            part = self._partner()
            val = part.cw.currentIndex()
            part.cw.clear()
            if type in ['Auto', 'Absolute', 'Per Unit']:
                part.cw.addItems(['Auto', 'Absolute', 'Per Unit', 'Aspect', 'Plan'])
            else:
                part.cw.addItems(['Auto', 'Absolute', 'Per Unit'])
            part.cw.setCurrentIndex(val)

        def _setLook(self, type):
            if type == 'Auto':
                self.spin1.hide()
                self.lab1.setText(' ')
                self._show(2, False)
                self._show(3, False)
            elif type == 'Absolute':
                self.spin1.show()
                self.lab1.setText('cm')
                self._show(2, False)
                self._show(3, False)
            elif type == 'Per Unit':
                self.spin1.show()
                self.lab1.setText('')
                self._show(2, True)
                self._show(3, False)
            elif type == 'Aspect':
                self.spin1.show()
                if self._axis == 0:
                    self.lab1.setText('*Height')
                else:
                    self.lab1.setText('*Width')
                self._show(2, False)
                self._show(3, False)
            elif type == 'Plan':
                self.spin1.show()
                if self._axis == 0:
                    self.lab1.setText('*Height')
                else:
                    self.lab1.setText('*Width')
                self._show(2, True)
                self._show(3, True)

        def _show(self, n, b, text='Range'):
            if n == 2:
                if b:
                    self.lab2_1.setText('*')
                    self.lab2_2.setText(text)
                    self.combo2.show()
                else:
                    self.lab2_1.setText(' ')
                    self.lab2_2.setText(' ')
                    self.combo2.hide()
            if n == 3:
                if b:
                    self.lab3_1.setText('/')
                    self.lab3_2.setText(text)
                    self.combo3.show()
                else:
                    self.lab3_1.setText(' ')
                    self.lab3_2.setText(' ')
                    self.combo3.hide()

    def __init__(self, canvas):
        super().__init__("Graph Size")
        self.canvas = canvas
        layout_h = QtWidgets.QHBoxLayout(self)
        gw = self._AreaBox('Width', canvas, 0)
        gh = self._AreaBox('Height', canvas, 1)
        gw.setPartner(gh)
        gh.setPartner(gw)
        layout_h.addWidget(gw)
        layout_h.addWidget(gh)
        self.setLayout(layout_h)
