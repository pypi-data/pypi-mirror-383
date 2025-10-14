import unittest
import shutil
import os
import warnings

import numpy as np

from lys import glb, home, Wave, display, errors, filters


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

    def test_CanvasData(self):
        for g in self.graphs:
            d = {}
            c = g.canvas

            # append data
            data1d = Wave([1, 2, 3])
            data2d = Wave([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
            data2dc = Wave([[1 + 1j, 2 + 2j], [3 + 3j, 4 + 4j]])
            line = c.Append(data1d)
            line2 = c.Append(data1d, axis="TopRight")
            image = c.Append(data2d)
            #ont = c.Append(data2d, contour=True)
            rgb = c.Append(data2dc)
            # vec = c.Append(data2dc, vector=True)

            # get wave data
            self.assertEqual(len(c.getLines()), 2)
            self.assertEqual(len(c.getImages()), 1)
            #self.assertEqual(len(c.getContours()), 1)
            self.assertEqual(len(c.getRGBs()), 1)
            #self.assertEqual(len(c.getVectorFields()), 1)

            c.SaveAsDictionary(d)

            # remove
            c.Remove(line)
            c.Remove(image)
            # c.Remove(cont)
            c.Remove(rgb)

            self.assertEqual(len(c.getLines()), 1)
            self.assertEqual(len(c.getImages()), 0)
            #self.assertEqual(len(c.getContours()), 0)
            self.assertEqual(len(c.getRGBs()), 0)

            # load
            c.LoadFromDictionary(d)
            self.assertEqual(len(c.getLines()), 2)
            self.assertEqual(len(c.getImages()), 1)
            #self.assertEqual(len(c.getContours()), 1)
            self.assertEqual(len(c.getRGBs()), 1)

            c.Clear()
            self.assertEqual(len(c.getWaveData()), 0)

    def test_WaveData(self):
        for g in self.graphs:
            c = g.canvas

            line = c.Append(Wave([1, 2, 3]))
            line.setVisible(False)
            self.assertFalse(line.getVisible())

            line.setOffset((1, 1, 2, 2))
            self.assertEqual(line.getOffset(), (1, 1, 2, 2))

            f = filters.SimpleMathFilter('+', 1)
            line.setFilter(f)
            self.assertEqual(line.getFilter(), f)

            line.setZOrder(11)
            self.assertEqual(line.getZOrder(), 11)

    def test_Line(self):
        for g in self.graphs:
            c = g.canvas

            line = c.Append(Wave([1, 2, 3]))
            line.setColor('#ff0000')
            self.assertEqual(line.getColor(), '#ff0000')

            line.setWidth(3)
            self.assertEqual(line.getWidth(), 3)

            line.setStyle("dashed")
            self.assertEqual(line.getStyle(), 'dashed')

            line.setMarker('circle')
            self.assertEqual(line.getMarker(), 'circle')

            line.setMarkerSize(5)
            self.assertEqual(line.getMarkerSize(), 5)

            line.setMarkerThick(3)
            self.assertEqual(line.getMarkerThick(), 3)

            line.setMarkerFilling('full')
            self.assertEqual(line.getMarkerFilling(), 'full')

            line.setErrorbar(4, direction="y")
            line.setErrorbar(3, direction="x")
            self.assertEqual(line.getErrorbar("y"), 4)
            self.assertEqual(line.getErrorbar("x"), 3)

            line.setCapSize(3)
            self.assertEqual(line.getCapSize(), 3)

            line.setLegendVisible(True)
            self.assertTrue(line.getLegendVisible())

            line.setLegendLabel("test")
            self.assertEqual(line.getLegendLabel(), "test")

            ap = line.saveAppearance()
            line.setColor('#ff00ff')
            line.setWidth(4)
            line.setStyle("solid")
            line.setMarker('nothing')
            line.setMarkerSize(3)
            line.setMarkerThick(2)
            line.setMarkerFilling('none')
            line.setErrorbar(5, direction="y")
            line.setCapSize(2)
            line.setLegendVisible(False)
            line.setLegendLabel("aaa")

            line.loadAppearance(ap)
            self.assertEqual(line.getWidth(), 3)
            self.assertEqual(line.getStyle(), 'dashed')
            self.assertEqual(line.getMarker(), 'circle')
            self.assertEqual(line.getMarkerSize(), 5)
            self.assertEqual(line.getMarkerThick(), 3)
            self.assertEqual(line.getMarkerFilling(), 'full')
            self.assertEqual(line.getErrorbar("y"), 4)
            self.assertEqual(line.getCapSize(), 3)
            self.assertTrue(line.getLegendVisible())
            self.assertEqual(line.getLegendLabel(), "test")

    def test_Image(self):
        for g in self.graphs:
            c = g.canvas

            im = c.Append(Wave([[1, 2, 3], [4, 5, 6]]))
            im.setColormap('bwr')
            self.assertEqual(im.getColormap(), 'bwr')

            im.setGamma(0.5)
            self.assertEqual(im.getGamma(), 0.5)

            im.setOpacity(0.7)
            self.assertEqual(im.getOpacity(), 0.7)

            im.setColorRange(1, 3)
            self.assertEqual(im.getColorRange(), (1, 3))

            im.setLog(True)
            self.assertTrue(im.isLog())

            ap = im.saveAppearance()
            im.setColormap('gray')
            im.setGamma(0.4)
            im.setOpacity(0.6)
            im.setColorRange(2, 4)
            im.setLog(False)

            im.loadAppearance(ap)
            self.assertEqual(im.getColormap(), 'bwr')
            self.assertEqual(im.getGamma(), 0.5)
            self.assertEqual(im.getOpacity(), 0.7)
            self.assertEqual(im.getColorRange(), (1, 3))
            self.assertTrue(im.isLog())

    def test_RGB(self):
        for g in self.graphs:
            c = g.canvas

            im = c.Append(Wave([[1 + 1j, 2, 3], [4, 5, 6]]))
            im.setColorRotation(99)
            self.assertEqual(im.getColorRotation(), 99)

            im.setColorRange(0, 5)
            self.assertEqual(im.getColorRange(), (0, 5))

            ap = im.saveAppearance()
            im.setColorRotation(9)
            im.setColorRange(0, 2)

            im.loadAppearance(ap)
            self.assertEqual(im.getColorRotation(), 99)
            self.assertEqual(im.getColorRange(), (0, 5))

    def test_Vector(self):
        for g in [self.graphs[0]]:
            c = g.canvas

            v = c.Append(Wave([[1 + 1j, 2, 3], [4, 5, 6]]), vector=True)
            v.setWidth(3)
            self.assertEqual(v.getWidth(), 3)

            v.setScale(4)
            self.assertEqual(v.getScale(), 4)

            v.setPivot('tail')
            self.assertEqual(v.getPivot(), 'tail')

            v.setColor('#ff0000')
            self.assertEqual(v.getColor(), '#ff0000')

            ap = v.saveAppearance()
            v.setWidth(5)
            v.setScale(6)
            v.setPivot('middle')
            v.setColor('#ff00ff')

            v.loadAppearance(ap)
            self.assertEqual(v.getWidth(), 3)
            self.assertEqual(v.getScale(), 4)
            self.assertEqual(v.getPivot(), 'tail')
            self.assertEqual(v.getColor(), '#ff0000')

    def test_Contour(self):
        for g in self.graphs:
            c = g.canvas

            line = c.Append(Wave(np.random.rand(100, 100)), contour=True)
            line.setLevel(0.5)
            self.assertEqual(line.getLevel(), 0.5)

            line.setColor('#ff0000')
            self.assertEqual(line.getColor(), '#ff0000')

            line.setWidth(3)
            self.assertEqual(line.getWidth(), 3)

            line.setStyle("dashed")
            self.assertEqual(line.getStyle(), 'dashed')

            ap = line.saveAppearance()
            line.setLevel(0.4)
            line.setColor('#ff00ff')
            line.setWidth(4)
            line.setStyle("solid")

            line.loadAppearance(ap)
            self.assertEqual(line.getLevel(), 0.5)
            self.assertEqual(line.getColor(), '#ff0000')
            self.assertEqual(line.getWidth(), 3)
            self.assertEqual(line.getStyle(), 'dashed')
