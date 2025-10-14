import unittest
import shutil
import os
import warnings

import matplotlib as mpl
import matplotlib.font_manager as fm

from lys import glb, home, display, errors
from numpy.testing import assert_array_equal, assert_array_almost_equal


class Graph_test(unittest.TestCase):
    path = "test/DataFiles"

    def setUp(self):
        warnings.simplefilter("ignore", errors.NotSupportedWarning)
        if glb.mainWindow() is None:
            if os.path.exists(home() + "/.lys"):
                shutil.rmtree(home() + "/.lys")
            glb.createMainWindow(show=False, restore=True)
        self.graphs = [display(lib=lib) for lib in ["matplotlib", "pyqtgraph"]]
        #self.graphs = [Graph(lib=lib) for lib in ["matplotlib"]]

    def test_Area(self):
        for g in self.graphs:
            d = {}
            c = g.canvas

            # set/get margin
            c.setMargin(0, 0, 0, 0)
            self.assertEqual(c.getMargin(raw=True), [0, 0, 0, 0])
            self.assertEqual(c.getMargin(), [0.2, 0.85, 0.2, 0.85])

            # save and load
            c.SaveAsDictionary(d)
            self.assertEqual(d["Margin"], [0, 0, 0, 0])
            c.setMargin(0.1, 0.1, 0.1, 0.1)
            c.LoadFromDictionary(d)
            self.assertEqual(c.getMargin(raw=True), [0, 0, 0, 0])
            self.assertEqual(c.getMargin(), [0.2, 0.85, 0.2, 0.85])

            # set/get area mode
            c.setCanvasSize("Both", "Absolute", 4)
            assert_array_almost_equal(c.getCanvasSize(), [4, 4])
            c.setCanvasSize("Height", "Aspect", 0.5)
            assert_array_almost_equal(c.getCanvasSize(), [4, 2])
            c.setCanvasSize("Both", "Absolute", 4)
            c.setCanvasSize("Width", "Aspect", 0.5)
            assert_array_almost_equal(c.getCanvasSize(), [2, 4])

            # save and load
            c.SaveAsDictionary(d)
            self.assertEqual(d["Size"]["Height"][0], "Absolute")
            self.assertAlmostEqual(d["Size"]["Height"][1], 4)
            self.assertEqual(d["Size"]["Width"][0], "Aspect")
            self.assertAlmostEqual(d["Size"]["Width"][1], 0.5)
            c.LoadFromDictionary(d)
            assert_array_almost_equal(c.getCanvasSize(), [2, 4])

    def test_Axes(self):
        for g in self.graphs:
            d = {}
            c = g.canvas

            # axisIsValid
            self.assertTrue(c.axisIsValid("Left"))
            self.assertFalse(c.axisIsValid("Top"))

            # axisList
            self.assertEqual(c.axisList(), ["Left", 'Bottom'])

            # set/get
            c.setAxisRange("Left", [0, 1])
            c.setAxisRange("Bottom", [0, 2])
            assert_array_almost_equal(c.getAxisRange("Left"), (0, 1))
            assert_array_almost_equal(c.getAxisRange("Bottom"), (0, 2))

            self.assertFalse(c.isAutoScaled('Left'))
            self.assertFalse(c.isAutoScaled('Bottom'))

            # save and load
            c.SaveAsDictionary(d)
            assert_array_almost_equal(d["AxisRange"]["Left"], (0, 1))
            assert_array_almost_equal(d["AxisRange"]["Bottom"], (0, 2))
            self.assertFalse(d["AxisRange"]['Left_auto'])
            self.assertFalse(d["AxisRange"]['Bottom_auto'])
            c.setAxisRange("Left", [0, 2])
            c.setAxisRange("Bottom", [0, 1])
            c.LoadFromDictionary(d)
            assert_array_almost_equal(c.getAxisRange("Left"), (0, 1))
            assert_array_almost_equal(c.getAxisRange("Bottom"), (0, 2))

            # autoscale
            c.setAutoScaleAxis("Left")
            self.assertTrue(c.isAutoScaled("Left"))
            self.assertFalse(c.isAutoScaled("Bottom"))

            # signal
            c.b = False

            def dummy():
                c.b = True
            c.axisRangeChanged.connect(dummy)
            c.setAxisRange("Bottom", [0, 1])
            self.assertTrue(c.b)

            # thick
            c.setAxisThick('Left', 3)
            self.assertEqual(c.getAxisThick('Left'), 3)

            # color
            c.setAxisColor('Left', (0.5, 0.5, 0.5, 1))
            res = c.getAxisColor('Left')
            self.assertTrue(res == (0.5, 0.5, 0.5, 1) or res == "#7f7f7f")

            # mirror
            c.setMirrorAxis("Left", False)
            self.assertFalse(c.getMirrorAxis("Left"))

            # mode
            c.setAxisMode("Left", "linear")
            self.assertEqual(c.getAxisMode("Left"), "linear")

            # save and load
            c.SaveAsDictionary(d)
            self.assertEqual(d['AxisSetting']['Left_thick'], 3)
            res = d['AxisSetting']['Left_color']
            self.assertTrue(res == (0.5, 0.5, 0.5, 1) or res == "#7f7f7f")
            self.assertFalse(d['AxisSetting']['Left_mirror'])
            self.assertEqual(d['AxisSetting']['Left_mode'], 'linear')

            c.setAxisThick('Left', 4)
            c.setAxisColor('Left', (0, 0, 0, 1))
            c.setMirrorAxis("Left", True)

            c.LoadFromDictionary(d)
            self.assertEqual(c.getAxisThick('Left'), 3)
            res = c.getAxisColor('Left')
            self.assertTrue(res == (0.5, 0.5, 0.5, 1) or res == "#7f7f7f")
            self.assertFalse(c.getMirrorAxis("Left"))
            self.assertEqual(c.getAxisMode("Left"), "linear")

            c.addAxis("Right")
            c.addAxis("Top")

            self.assertTrue(c.axisIsValid('Right'))
            self.assertTrue(c.axisIsValid('Top'))

    def test_Ticks(self):
        for g in self.graphs:
            d = {}
            c = g.canvas

            # width
            c.setTickWidth("Left", 3, which="major")
            c.setTickWidth("Bottom", 2, which="minor")
            self.assertEqual(c.getTickWidth("Left", which="major"), 3)
            self.assertEqual(c.getTickWidth("Bottom", which="minor"), 2)

            # length
            c.setTickLength("Left", 3, which="major")
            c.setTickLength("Bottom", 1, which="minor")
            self.assertEqual(c.getTickLength("Left", which="major"), 3)
            self.assertEqual(c.getTickLength("Bottom", which="minor"), 1)

            # interval
            c.setTickInterval("Left", 3, which="major")
            c.setTickInterval("Bottom", 1, which="minor")
            self.assertEqual(c.getTickInterval("Left", which="major"), 3)
            self.assertEqual(c.getTickInterval("Bottom", which="minor"), 1)

            # visible
            c.setTickVisible("Left", False, which="major")
            c.setTickVisible("Bottom", False, which="minor")
            self.assertFalse(c.getTickVisible("Left", which="major"))
            self.assertFalse(c.getTickVisible("Bottom", which="minor"))

            # direction
            c.setTickDirection("Left", "in")
            c.setTickDirection("Bottom", "out")
            self.assertEqual(c.getTickDirection("Left"), "in")
            self.assertEqual(c.getTickDirection("Bottom"), 'out')

            # save and load
            c.SaveAsDictionary(d)
            c.setTickWidth("Left", 2, which="major")
            c.setTickWidth("Bottom", 3, which="minor")
            c.setTickLength("Left", 1, which="major")
            c.setTickLength("Bottom", 3, which="minor")
            c.setTickInterval("Left", 1, which="major")
            c.setTickInterval("Bottom", 3, which="minor")
            c.setTickVisible("Left", True, which="major")
            c.setTickVisible("Bottom", True, which="minor")
            c.setTickDirection("Left", "out")
            c.setTickDirection("Bottom", "in")

            c.LoadFromDictionary(d)
            self.assertEqual(c.getTickWidth("Left", which="major"), 3)
            self.assertEqual(c.getTickWidth("Bottom", which="minor"), 2)
            self.assertEqual(c.getTickLength("Left", which="major"), 3)
            self.assertEqual(c.getTickLength("Bottom", which="minor"), 1)
            self.assertEqual(c.getTickInterval("Left", which="major"), 3)
            self.assertEqual(c.getTickInterval("Bottom", which="minor"), 1)
            self.assertFalse(c.getTickVisible("Left", which="major"))
            self.assertFalse(c.getTickVisible("Bottom", which="minor"))
            self.assertEqual(c.getTickDirection("Left"), "in")
            self.assertEqual(c.getTickDirection("Bottom"), 'out')

    def test_AxisLabel(self):
        for g in self.graphs:
            d = {}
            c = g.canvas

            # set/get axisLabel
            c.setAxisLabel("Left", "left")
            c.setAxisLabel("Bottom", "bottom")
            self.assertEqual(c.getAxisLabel("Left").replace(" ", ""), "left")
            self.assertEqual(c.getAxisLabel("Bottom").replace(" ", ""), "bottom")

            # set/get axisLabel Visible
            c.setAxisLabelVisible("Left", True)
            c.setAxisLabelVisible("Bottom", False)
            self.assertTrue(c.getAxisLabelVisible("Left"))
            self.assertFalse(c.getAxisLabelVisible("Bottom"))

            # set/get axis label coords
            c.setAxisLabelCoords("Left", -0.1)
            c.setAxisLabelCoords("Bottom", -0.14)
            self.assertEqual(c.getAxisLabelCoords("Left"), -0.1)
            self.assertEqual(c.getAxisLabelCoords("Bottom"), -0.14)

            # set/get axis label font
            family = fm.FontProperties(family=mpl.rcParams['font.family']).get_name()
            c.setAxisLabelFont("Left", family, 12, "#000000")
            c.setAxisLabelFont("Bottom", family, 14, "#ffffff")
            self.assertEqual(c.getAxisLabelFont("Left"), {"fname": family, "size": 12, "color": "#000000"})
            self.assertEqual(c.getAxisLabelFont("Bottom"), {"fname": family, "size": 14, "color": "#ffffff"})

            # save and load
            c.SaveAsDictionary(d)
            c.setAxisLabel("Left", "right")
            c.setAxisLabelVisible("Left", False)
            c.setAxisLabelCoords("Left", -0.14)
            c.setAxisLabelFont("Left", family, 11, "#ffffff")

            c.LoadFromDictionary(d)
            self.assertEqual(c.getAxisLabel("Left").replace(" ", ""), "left")
            self.assertTrue(c.getAxisLabelVisible("Left"))
            self.assertEqual(c.getAxisLabelCoords("Left"), -0.1)
            self.assertEqual(c.getAxisLabelFont("Left"), {"fname": family, "size": 12, "color": "#000000"})

    def test_TickLabel(self):
        for g in self.graphs:
            d = {}
            c = g.canvas

            # set/get tickLabelVisible
            c.setTickLabelVisible("Left", True)
            c.setTickLabelVisible("Left", True, mirror=True)
            self.assertTrue(c.getTickLabelVisible("Left"))
            self.assertTrue(c.getTickLabelVisible("Left", mirror=True))

            # set/get tick label font
            family = fm.FontProperties(family=mpl.rcParams['font.family']).get_name()
            c.setTickLabelFont("Left", family, 12, "#000000")
            c.setTickLabelFont("Bottom", family, 14, "#ffffff")
            self.assertEqual(c.getTickLabelFont("Left"), {"fname": family, "size": 12, "color": "#000000"})
            self.assertEqual(c.getTickLabelFont("Bottom"), {"fname": family, "size": 14, "color": "#ffffff"})

            # save and load
            c.SaveAsDictionary(d)
            c.setTickLabelVisible("Left", False)
            c.setTickLabelFont("Left", family, 14, "#000000")

            c.LoadFromDictionary(d)
            self.assertTrue(c.getTickLabelVisible("Left"))
            self.assertEqual(c.getTickLabelFont("Left"), {"fname": family, "size": 12, "color": "#000000"})

    def test_Legend(self):
        for g in self.graphs:
            d = {}
            c = g.canvas

            c.setLegendFrameVisible(False)
            self.assertFalse(c.getLegendFrameVisible())

            c.setLegendPosition((0.4, 0.3))
            self.assertEqual(c.getLegendPosition(), (0.4, 0.3))

            family = fm.FontProperties(family=mpl.rcParams['font.family']).get_name()
            c.setLegendFont(family, 12, "#ffffff")
            self.assertEqual(c.getLegendFont(), {"fname": family, "size": 12, "color": "#ffffff"})

            # save and load
            c.SaveAsDictionary(d)
            c.setLegendFrameVisible(True)
            c.setLegendPosition((0.1, 0.1))
            c.setLegendFont(family, 11, "#000000")

            c.LoadFromDictionary(d)
            self.assertFalse(c.getLegendFrameVisible())
            self.assertEqual(c.getLegendPosition(), (0.4, 0.3))
            self.assertEqual(c.getLegendFont(), {"fname": family, "size": 12, "color": "#ffffff"})
