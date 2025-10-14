import os
import sys
import shutil
import logging
from pathlib import Path


from lys import load
from lys.Qt import QtWidgets, QtCore, QtGui


class FileSystemView(QtWidgets.QWidget):
    """
    *FileSystemView* is a custom widget to see files, which is mainly used in main window.

    Developers can get selected paths by :meth:`selectedPaths` method.
    Context menu for specified type can be registered by :meth:`registerFileMenu` method.

    See :meth:`selectedPaths` and :meth:`registerFileMenu` for detail and examples

    Args:
        path(str): path to see files.
        model(QFileSystemModel): model used in this view
        drop(bool): Accept drag & drop or not.
        filter(bool): Enable filtering or not.
        menu(bool): Enable context menu or not.
    """

    selectionChanged = QtCore.pyqtSignal(object, object)
    "Emitted when the selected file is changed."

    def __init__(self, path, model=QtWidgets.QFileSystemModel(), drop=False, filter=True, menu=True):
        super().__init__()
        self._path = path
        self.__initUI(self._path, model, drop, filter)
        if menu:
            self._builder = _contextMenuBuilder(self)
        else:
            self._builder = None

    def __loaded(self):
        if not self._tree.rootIndex().isValid():
            self._Model.mod.setRootPath(self._path)
            root = self._Model.mapFromSource(self._Model.mod.index(self._path))
            self._tree.setRootIndex(root)

    def __initUI(self, path, model, drop=False, filter=True):
        self._Model = _FileSystemModel(path, model, drop)
        model.directoryLoaded.connect(self.__loaded)

        self._tree = QtWidgets.QTreeView()
        self._tree.setModel(self._Model)
        self._tree.setRootIndex(self._Model.indexFromPath(path))
        self._tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._buildContextMenu)
        self._tree.selectionModel().selectionChanged.connect(self.selectionChanged.emit)

        self._tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self._tree.setDragEnabled(True)
        self._tree.setAcceptDrops(True)
        self._tree.setDropIndicatorShown(True)
        self._tree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self._tree.setColumnHidden(3, True)
        self._tree.setColumnHidden(2, True)
        self._tree.setColumnHidden(1, True)

        edit = QtWidgets.QLineEdit()
        edit.textChanged.connect(self._setFilter)

        h1 = QtWidgets.QHBoxLayout()
        h1.addWidget(QtWidgets.QLabel("Filter"))
        h1.addWidget(edit)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._tree)
        if filter:
            layout.addLayout(h1)
        self.setLayout(layout)

    def _setFilter(self, filter):
        self._Model.setFilterRegularExpression(filter)
        self._tree.setRootIndex(self._Model.indexFromPath(self._path))

    def _buildContextMenu(self, qPoint):
        if self._builder is not None:
            self._builder.build(self.selectedPaths())

    def selectedPath(self):
        """
        Returns first selected path.

        Return:
            str: path selected
        """
        paths = self.selectedPaths()
        return paths[0]

    def selectedPaths(self):
        """
        Returns selected paths.

        Return:
            list of str: paths selected

        Example::

            from lys import glb
            view = glb.mainWindow().fileView     # access global fileview in main window.
            view.selectedPaths()                 # ["path selected", "path selected2, ..."]
        """
        list = self._tree.selectedIndexes()
        res = []
        for item in list:
            res.append(self._Model.filePath(item))
        if len(res) == 0:
            res.append(self._path)
        return res

    def registerFileMenu(self, ext, menu, add_default=True, **kwargs):
        """register new context menu to filetype specified by *ext*

        Args:
            ext(str): extension of file type, e.g. ".txt", ".csv", etc...
            menu(QMenu): context menu to be added.
            add_default: if True, default menus such as Cut, Copy is automatically added at the end of menu.

        Example::

            from lys import glb
            from lys.Qt import QtWidgets

            action = QtWidgets.QAction("Test", triggered = lambda: print("test"))
            menu = QtWidgets.QMenu()
            menu.addAction(action)

            view = glb.mainWindow().fileView     # access global fileview in main window.
            view.registerFileMenu(".txt", menu)  # By right clicking .txt file, you see 'test' menu.
        """
        self._builder.register(ext, menu, add_default=add_default, **kwargs)

    def setPath(self, path):
        """
        Set root directory of file system.
        Args:
            path(str): root path
        """
        self._path = path
        self._Model.setPath(path)
        self._tree.setRootIndex(self._Model.indexFromPath(path))


class _FileSystemModel(QtCore.QSortFilterProxyModel):
    """Model class for FileSystemView"""
    _exclude = ["__pycache__", "dask-worker-space"]

    def __init__(self, path, model, drop=False):
        super().__init__()
        self._path = path
        self._drop = drop
        self.mod = model
        self.mod.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)
        self.mod.setRootPath(self._path)
        self.setSourceModel(self.mod)
        self.setRecursiveFilteringEnabled(True)

    def setPath(self, path):
        self._path = path
        self.mod.setRootPath(path)

    def indexFromPath(self, path):
        return self.mapFromSource(self.mod.index(path))

    def filterAcceptsRow(self, row, parent):
        index = self.mod.index(row, 0, parent)
        path, root = Path(self.mod.filePath(index)), Path(self._path)
        if root in path.parents:
            for exc in self._exclude:
                if exc in str(path):
                    return False
            return super().filterAcceptsRow(row, parent)
        else:
            return True

    def setFilterRegularExpression(self, filters):
        exp = QtCore.QRegularExpression(filters)
        if exp.isValid():
            super().setFilterRegularExpression(exp)
        else:
            super().setFilterRegularExpression("5314548674534687654867")
        self.mod.setRootPath(self._path)

    def filePath(self, index):
        return self.mod.filePath(self.mapToSource(index))

    def isDir(self, index):
        return self.mod.isDir(self.mapToSource(index))

    def flags(self, index):
        if self._drop:
            return super().flags(index) | QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsDragEnabled
        else:
            return super().flags(index)

    def supportedDropActions(self):
        return QtCore.Qt.MoveAction

    def canDropMimeData(self, data, action, row, column, parent):
        return True

    def dropMimeData(self, data, action, row, column, parent):
        targetDir = Path(self.mod.filePath(self.mapToSource(parent)))
        if targetDir.is_file():
            targetDir = targetDir.parent
        files = [Path(QtCore.QUrl(url).toLocalFile()) for url in data.text().splitlines()]
        targets = [Path(str(targetDir.absolute()) + "/" + f.name) for f in files]
        _moveFiles(files, targets)
        return True


class _contextMenuBuilder:
    """Builder of context menu in FileSystemView"""

    def __init__(self, parent):
        self._parent = parent
        self._SetDefaultMenu()

    def _SetDefaultMenu(self):
        self._new = QtWidgets.QAction('New Directory', triggered=self.__newdir)
        self._load = QtWidgets.QAction('Load', triggered=self.__load)
        self._prt = QtWidgets.QAction('Print', triggered=self.__print)

        self._delete = QtWidgets.QAction('Delete', triggered=self.__del)
        self._rename = QtWidgets.QAction('Rename', triggered=self.__rename)

        self._cut = QtWidgets.QAction('Cut', triggered=self.__cut)
        self._copy = QtWidgets.QAction('Copy', triggered=self.__copy)
        self._paste = QtWidgets.QAction('Paste', triggered=self.__paste)

        menu = {}
        menu["dir_single"] = self._makeMenu([self._new, self._load, self._prt, "sep", self._cut, self._copy, self._paste, "sep", self._rename, self._delete])
        menu["dir_multi"] = self._makeMenu([self._load, self._prt, "sep", self._cut, self._copy, "sep", self._delete])

        menu["mix_single"] = self._makeMenu([self._load, self._prt, "sep", self._cut, self._copy, "sep", self._rename, self._delete])
        menu["mix_multi"] = self._makeMenu([self._load, self._prt, "sep", self._cut, self._copy, "sep", self._delete])

        self.__actions = menu

    def register(self, ext, menu, add_default, hide_load=False, hide_print=False):
        menu_s = self._duplicateMenu(menu)
        menu_m = self._duplicateMenu(menu)
        if add_default:
            if ext == "dir":
                menu_s.addAction(self._new)
                menu_m.addAction(self._new)
            menu_s.addSeparator()
            if not hide_load:
                menu_s.addAction(self._load)
            if not hide_print:
                menu_s.addAction(self._prt)
            menu_s.addSeparator()
            menu_s.addAction(self._cut)
            menu_s.addAction(self._copy)
            menu_s.addSeparator()
            menu_s.addAction(self._rename)
            menu_s.addAction(self._delete)

            menu_m.addSeparator()
            if not hide_load:
                menu_m.addAction(self._load)
            if not hide_print:
                menu_m.addAction(self._prt)
            menu_m.addSeparator()
            menu_m.addAction(self._cut)
            menu_m.addAction(self._copy)
            menu_m.addSeparator()
            menu_m.addAction(self._delete)
        self.__actions[ext + "_single"] = menu_s
        self.__actions[ext + "_multi"] = menu_m

    def _duplicateMenu(self, origin):
        result = QtWidgets.QMenu()
        for m in origin.actions():
            if isinstance(m, QtWidgets.QMenu):
                result.addMenu(self._duplicateMenu(m))
            else:
                result.addAction(m)
        return result

    def _makeMenu(self, list):
        result = QtWidgets.QMenu()
        for item in list:
            if item == "sep":
                result.addSeparator()
            else:
                result.addAction(item)
        return result

    def build(self, paths):
        self._paths = paths
        tp = self._judgeFileType(self._paths)
        self.__actions[tp].exec_(QtGui.QCursor.pos())

    def _test(self, tp):
        return self.__actions[tp]

    def _judgeFileType(self, paths):
        if all([self._parent._Model.isDir(self._parent._Model.indexFromPath(p)) for p in paths]):
            res = "dir"
        else:
            ext = os.path.splitext(paths[0])[1]
            if all([ext == os.path.splitext(p)[1] for p in paths]):
                if ext + "_single" not in self.__actions:
                    res = "mix"
                else:
                    res = ext
            else:
                res = "mix"
        # check if there is multiple files
        if len(paths) == 1:
            res += "_single"
        else:
            res += "_multi"
        return res

    def __load(self):
        from lys import glb
        for p in self._paths:
            nam, ext = os.path.splitext(os.path.basename(p))
            obj = load(p)
            if obj is not None:
                if ext != ".grf":
                    glb.shell().addObject(obj, name=nam)
            else:
                print("Failed to load " + p, file=sys.stderr)

    def __newdir(self):
        text, ok = QtWidgets.QInputDialog.getText(None, 'Create directory', 'Directory name:')
        if ok and not len(text) == 0:
            for p in self._paths:
                os.makedirs(p + '/' + text, exist_ok=True)

    def __del(self):
        paths = self._paths
        msg = QtWidgets.QMessageBox(parent=self._parent)
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText("Are you really want to delete " + str(len(paths)) + " items?")
        msg.setWindowTitle("Caution")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        ok = msg.exec_()
        if ok == QtWidgets.QMessageBox.Ok:
            for p in paths:
                if os.path.isfile(p):
                    os.remove(p)
                if os.path.isdir(p):
                    shutil.rmtree(p)

    def __copy(self):
        self._copyType = "copy"
        self._copyPaths = [Path(p) for p in self._paths]

    def __cut(self):
        self._copyType = "cut"
        self._copyPaths = [Path(p) for p in self._paths]

    def __paste(self):
        if hasattr(self, "_copyType"):
            targetDir = Path(self._paths[0])
            targets = [Path(str(targetDir.absolute()) + "/" + path.name) for path in self._copyPaths]
            _moveFiles(self._copyPaths, targets, copy=self._copyType == "copy")

    def __rename(self):
        file = Path(self._paths[0])
        target, ok = QtWidgets.QInputDialog.getText(None, "Rename", "Enter new name", text=file.name)
        if ok:
            target = Path(str(file.parent.absolute()) + "/" + target)
            _moveFiles(file, target)

    def __print(self):
        for p in self._paths:
            w = load(p)
            print(w)


def _moveFiles(files, targets, copy=False):
    if isinstance(files, Path):
        return _moveFiles([files], [targets], copy=copy)
    state = None
    pair = []
    for orig, newfile in zip(files, targets):
        if orig == newfile:
            continue
        if newfile.exists():
            if state == "yesall":
                pair.append([orig, newfile])
            elif state == "noall":
                pass
            else:
                from lys import glb
                msgBox = QtWidgets.QMessageBox(glb.mainWindow())
                msgBox.setIcon(QtWidgets.QMessageBox.Warning)
                msgBox.setWindowTitle("Caution")
                msgBox.setText(str(newfile.absolute()) + " exists. Do you want to overwrite it?")
                if len(files) == 1:
                    msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
                else:
                    msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.YesAll | QtWidgets.QMessageBox.NoAll | QtWidgets.QMessageBox.Cancel)
                msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
                result = msgBox.exec_()
                if result == QtWidgets.QMessageBox.Yes:
                    pair.append([orig, newfile])
                elif result == QtWidgets.QMessageBox.No:
                    pass
                elif result == QtWidgets.QMessageBox.YesAll:
                    state = "yesall"
                    pair.append([orig, newfile])
                elif result == QtWidgets.QMessageBox.NoAll:
                    state = "noall"
                elif result == QtWidgets.QMessageBox.Cancel:
                    return False
        else:
            pair.append([orig, newfile])
    for orig, newfile in pair:
        if newfile.exists():
            if newfile.is_file():
                os.remove(newfile.absolute())
            else:
                shutil.rmtree(newfile.absolute())
            logging.info(str(newfile.absolute()) + " has been removed.")
        if copy:
            shutil.copyfile(orig.absolute(), newfile.absolute())
            logging.info(str(newfile.absolute()) + " is copied from " + str(orig.absolute()) + ".")
        else:
            orig.rename(newfile)
            logging.info(str(newfile.absolute()) + " is moved from " + str(orig.absolute()) + ".")
