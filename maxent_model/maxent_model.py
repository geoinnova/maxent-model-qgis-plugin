# -*- coding: utf-8 -*-

__author__ = 'Roberto Matellanes. Gis&Beers'
__date__ = '2022-08-17'
__copyright__ = '(C) 2022 by Roberto Matellanes. Gis&Beers'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'


import os
from os import path
import sys
import inspect

from qgis.core import QgsApplication

from PyQt5.QtWidgets import QMenu
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5.QtGui import QIcon

from qgis.core import QgsApplication

from .gui.about_dialog import AboutDialog

from .maxent_model_provider import MaxentModelProvider

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

class MaxentModelPlugin(object):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):

        # Save reference to the QGIS interface

        self.iface = iface
        self.dlgAbout = AboutDialog()
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'MaxentModelPlugin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.pluginIsActive = False
        self.dockwidget = None
        self.provider = None
        self.first_start = None
        self.menu = self.tr(u'&Maxent Model')  # Procesing

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Maxent Model', message)

    def add_action(self, text, callback, icon_path=None, status_tip=None, whats_this=None):
        """Add a toolbar icon to the toolbar.
        """
        if icon_path is not None:
            icon = QIcon(icon_path)
            action = QAction(icon, text, self.iface.mainWindow())
        else:
            action = QAction(text, self.iface.mainWindow())

        action.triggered.connect(callback)
        # action.triggered.connect( lambda param1: callback(param1))

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        self.actions.append(action)

        return action

    def initGui(self):
        # create action that will start plugin configuration


        icon_about = self.plugin_dir + '/icon.png'

        self.action_about = self.add_action("&About",
                                            self.open_dlg_about,
                                            icon_about,
                                            "About",
                                            "Open About dialog")

        # add toolbar button and menu item

        self.iface.addToolBarIcon(self.action_about)
        # self.iface.addToolBarIcon(self.action2)

        # Add plugins menu items
        self.main_menu = None  # GeoEASIN-plugin-menyn

        #  Action about
        # self.main_menu.addAction(self.action_about)

        self.initProcessing()

    def unload(self):
        # remove the plugin menu item and icon
        for action in self.actions:
            self.iface.removePluginMenu("&Maxent model", action)
            self.iface.removeToolBarIcon(action)


        QgsApplication.processingRegistry().removeProvider(self.provider)

    def initProcessing(self):
        self.provider = MaxentModelProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    # --------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        self.pluginIsActive = False


    def open_dlg_about(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False

        # show the dialog
        self.dlgAbout.show()
        # Run the dialog event loop
        result = self.dlgAbout.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass