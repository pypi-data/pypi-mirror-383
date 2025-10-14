import unittest
import shutil
import os
import warnings

import matplotlib as mpl
import matplotlib.font_manager as fm

from numpy.testing import assert_array_equal, assert_array_almost_equal
from lys import glb, home, display, errors


class Graph_test(unittest.TestCase):
    path = "test/DataFiles"

    def setUp(self):
        warnings.simplefilter("ignore", errors.NotSupportedWarning)
        if glb.mainWindow() is None:
            if os.path.exists(home() + "/.lys"):
                shutil.rmtree(home() + "/.lys")
            glb.createMainWindow(show=False, restore=True)
        self.graphs = [display(lib=lib) for lib in ["matplotlib", "pyqtgraph"]]

    def __lineStyles(self, obj):
        obj.setLineColor('#ff0000')
        self.assertEqual(obj.getLineColor(), '#ff0000')

        obj.setLineStyle('dashed')
        self.assertEqual(obj.getLineStyle(), 'dashed')

        obj.setLineWidth(3)
        self.assertEqual(obj.getLineWidth(), 3)

        d = obj.saveAppearance()
        obj.setLineColor('#ff00ff')
        obj.setLineStyle('solid')
        obj.setLineWidth(4)

        obj.loadAppearance(d)
        self.assertEqual(obj.getLineColor(), '#ff0000')
        self.assertEqual(obj.getLineStyle(), 'dashed')
        self.assertEqual(obj.getLineWidth(), 3)

    def test_LineAnnotation(self):
        for g in self.graphs:
            c = g.canvas

            line = c.addLineAnnotation()
            line.setPosition([(0, 1), (2, 3)])
            self.assertEqual(line.getPosition(), ((0, 1), (2, 3)))

            self.__lineStyles(line)

    def test_InfiniteLineAnnotation(self):
        for g in self.graphs:
            c = g.canvas

            line = c.addInfiniteLineAnnotation()
            line.setPosition(5)
            self.assertEqual(line.getPosition(), 5)

            self.__lineStyles(line)

    def test_RectAnnotation(self):
        for g in self.graphs:
            c = g.canvas

            rect = c.addRectAnnotation()
            rect.setRegion(([0, 1], [2, 3]))
            self.assertEqual(rect.getPosition(), (0, 2))
            self.assertEqual(rect.getSize(), (1, 1))

            self.__lineStyles(rect)

    def test_RegionAnnotation(self):
        for g in self.graphs:
            c = g.canvas

            rect = c.addRegionAnnotation()
            rect.setRegion((0, 1))
            self.assertEqual(rect.getRegion(), (0, 1))

            self.__lineStyles(rect)

    def test_FreeRegionAnnotation(self):
        for g in self.graphs:
            c = g.canvas

            rect = c.addFreeRegionAnnotation()
            rect.setRegion([(0, 0), (1, 1)])
            assert_array_almost_equal(rect.getRegion(), [(0, 0), (1, 1)])

            self.__lineStyles(rect)

    def test_CrossAnnotation(self):
        for g in self.graphs:
            c = g.canvas

            cross = c.addCrossAnnotation()
            cross.setPosition((0, 1))
            self.assertEqual(cross.getPosition(), (0, 1))

            self.__lineStyles(cross)

    def test_TextAnnotation(self):
        for g in self.graphs:
            text = g.addText("test")
            self.assertEqual(text.getText(), "test")

            text.setText("test1")
            self.assertEqual(text.getText(), "test1")

            text.setPosition((0, 0))
            self.assertTrue(text.getPosition() == (0, 0))

            text.setTransform("data")
            self.assertEqual(text.getTransform(), "data")
            text.setTransform(["axes", "data"])
            text.setTransform("axes")
            self.assertTrue(text.getPosition() == (0, 0))

            family = fm.FontProperties(family=mpl.rcParams['font.family']).get_name()
            text.setFont(family, 11, "#333333")
            self.assertEqual(text.getFont(), {"fname": family, "size": 11, "color": "#333333"})

            text.setBoxStyle("square")
            self.assertEqual(text.getBoxStyle(), "square")

            text.setBoxColor("#111111", "#222222")
            self.assertEqual(text.getBoxColor()[0], "#111111")
            self.assertEqual(text.getBoxColor()[1], "#222222")

            d = g.SaveAsDictionary()
            g.LoadFromDictionary(d)
            text = g.getTextAnnotations()[0]
            self.assertEqual(text.getText(), "test1")
            self.assertTrue(text.getPosition() == (0, 0))
            self.assertEqual(text.getTransform(), "axes")
            self.assertEqual(text.getFont(), {"fname": family, "size": 11, "color": "#333333"})
            self.assertEqual(text.getBoxStyle(), "square")
            self.assertEqual(text.getBoxColor()[0], "#111111")
            self.assertEqual(text.getBoxColor()[1], "#222222")
