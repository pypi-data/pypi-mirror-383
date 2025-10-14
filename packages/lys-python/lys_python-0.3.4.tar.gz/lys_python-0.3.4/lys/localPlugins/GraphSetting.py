from lys import home, SettingDict, glb, display
from lys.widgets import Graph
from lys.Qt import QtWidgets

_setting = SettingDict(home() + "/.lys/settings/graph.dic")


def changeLibrary(lib):
    Graph.graphLibrary = lib
    _setting["GraphLibrary"] = lib


def _register():
    menu = glb.mainWindow().menuBar()
    graph = menu.addMenu("Graph")

    # graph library
    Graph.graphLibrary = _setting.get("GraphLibrary", "matplotlib")
    lib = graph.addMenu("Default Library")
    l1 = lib.addAction("Matplotlib")
    l1.setCheckable(True)
    l2 = lib.addAction("pyqtGraph")
    l2.setCheckable(True)
    group = QtWidgets.QActionGroup(lib)
    group.addAction(l1)
    group.addAction(l2)
    if Graph.graphLibrary == "matplotlib":
        l1.setChecked(True)
    else:
        l2.setChecked(True)
    l1.triggered.connect(lambda: changeLibrary("matplotlib"))
    l2.triggered.connect(lambda: changeLibrary("pyqtgraph"))

    graph.addSeparator()
    makeNew = graph.addAction("Create blank Graph")
    makeNew.triggered.connect(display)

    # close all
    close = graph.addAction("Close all Graphs")
    close.triggered.connect(glb.mainWindow().closeAllGraphs)
    close.setShortcut("Ctrl+K")


_register()
