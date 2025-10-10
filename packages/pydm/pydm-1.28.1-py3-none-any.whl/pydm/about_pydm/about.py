from qtpy.QtWidgets import QWidget, QTableWidgetItem
from qtpy.QtCore import Qt, qVersion
from pydm.utilities import ACTIVE_QT_WRAPPER, QtWrapperTypes
from .about_ui import Ui_Form
from numpy import __version__ as numpyver
from pyqtgraph import __version__ as pyqtgraphver
import pydm
import sys
from os import path
import inspect
import qtpy

# get Qt binding and version
PYTHON_BINDING_VERSION = ""
if "PyQt" in qtpy.API_NAME:
    PYTHON_BINDING_VERSION = qtpy.QtCore.PYQT_VERSION_STR
elif "PySide" in qtpy.API_NAME:
    PYTHON_BINDING_VERSION = qtpy.QtCore.__version__
else:
    PYTHON_BINDING_VERSION = "Unknown version"


class AboutWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.pydmVersionLabel.setText(str(self.ui.pydmVersionLabel.text()).format(version=pydm.__version__))
        pyver = ".".join([str(v) for v in sys.version_info[0:3]])
        python_binding_name = "PyQt" if ACTIVE_QT_WRAPPER == QtWrapperTypes.PYQT5 else "PySide"
        self.ui.modulesVersionLabel.setText(
            str(self.ui.modulesVersionLabel.text()).format(
                pyver=pyver,
                python_binding=python_binding_name,
                python_binding_ver=PYTHON_BINDING_VERSION,
                qtver=qVersion(),
                pyqtgraphver=pyqtgraphver,
                numpyver=numpyver,
            )
        )
        self.populate_external_tools_list()
        self.populate_plugin_list()
        self.populate_contributor_list()

    def populate_external_tools_list(self):
        col_labels = ["Name", "Group", "Author", "File"]
        self.ui.externalToolsTableWidget.setColumnCount(len(col_labels))
        self.ui.externalToolsTableWidget.setHorizontalHeaderLabels(col_labels)
        self.ui.externalToolsTableWidget.horizontalHeader().setStretchLastSection(True)
        self.ui.externalToolsTableWidget.verticalHeader().setVisible(False)
        self.add_tools_to_list(pydm.tools.ext_tools)

    def add_tools_to_list(self, tools):
        for name, tool in tools.items():
            if isinstance(tool, dict):
                self.add_tools_to_list(tool)
            else:
                tool_info = tool.get_info()
                name_item = QTableWidgetItem(tool_info.get("name", "None"))
                group_item = QTableWidgetItem(tool_info.get("group", "None"))
                author_item = QTableWidgetItem(tool_info.get("author", "None"))
                file_item = QTableWidgetItem(tool_info.get("file", "None"))
                new_row = self.ui.externalToolsTableWidget.rowCount()
                self.ui.externalToolsTableWidget.insertRow(new_row)
                self.ui.externalToolsTableWidget.setItem(new_row, 0, name_item)
                self.ui.externalToolsTableWidget.setItem(new_row, 1, group_item)
                self.ui.externalToolsTableWidget.setItem(new_row, 2, author_item)
                self.ui.externalToolsTableWidget.setItem(new_row, 3, file_item)

    def populate_plugin_list(self):
        col_labels = ["Protocol", "File"]
        self.ui.dataPluginsTableWidget.setColumnCount(len(col_labels))
        self.ui.dataPluginsTableWidget.setHorizontalHeaderLabels(col_labels)
        self.ui.dataPluginsTableWidget.horizontalHeader().setStretchLastSection(True)
        self.ui.dataPluginsTableWidget.verticalHeader().setVisible(False)
        pydm.data_plugins.initialize_plugins_if_needed()
        for protocol, plugin in pydm.data_plugins.plugin_modules.items():
            protocol_item = QTableWidgetItem(protocol)
            file_item = QTableWidgetItem(inspect.getfile(plugin.__class__))
            new_row = self.ui.dataPluginsTableWidget.rowCount()
            self.ui.dataPluginsTableWidget.insertRow(new_row)
            self.ui.dataPluginsTableWidget.setItem(new_row, 0, protocol_item)
            self.ui.dataPluginsTableWidget.setItem(new_row, 1, file_item)

    def populate_contributor_list(self):
        contrib_file = path.join(path.dirname(path.realpath(__file__)), "contributors.txt")
        with open(contrib_file) as f:
            for line in f:
                self.ui.contributorsListWidget.addItem(str(line).strip())
