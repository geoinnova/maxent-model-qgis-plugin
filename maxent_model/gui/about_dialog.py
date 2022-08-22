# -*- coding: utf-8 -*-
"""

"""

import os

from qgis.PyQt import QtWidgets
from qgis.PyQt import uic
from qgis.PyQt.QtGui import QPixmap

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'about_dialog.ui'))

UPPATH = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])
CURR_PATH = UPPATH(__file__, 2)

class AboutDialog(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(AboutDialog, self).__init__(parent)
        self.setupUi(self)

        self.logo = QPixmap(os.path.join(CURR_PATH, 'icon.png'))
        self.logo = self.logo.scaledToWidth(30)
        self.lblLogo.setPixmap(self.logo)
        self.tbInfo.setHtml(self.get_about_text())
        self.tbLicense.setPlainText(self.get_license_text())

    def get_about_text(self):
        return self.tr(
            '<p>Este plugin te ayudará a adaptar tu cartografía de coordenadas y variables ambientales para la entrada de archivos en Maxent respetando los formatos y estructura de archivos CSV y ASCII durante la construcción de modelos de distribución potencial de especies (SDM). </p>'
            '<p>This plugin will help you to adapt your coordinates and environmental variables for file input in Maxent respecting CSV and ASCII file formats and structure during the construction of potential species distribution models (SDM).</p>'
            '<p><strong>Developers/Desarrollo:</strong>  <a href="http://www.gisandbeers.com/roberto-aspectos-profesionales-en-sig/">Roberto Matellanes</a> <a href="https://geoinnova.org/">Patricio Soriano. Geoinnova</a></p>'
            '<p><strong>Web:</strong> <a href="https://geoinnova.org/plugin/maxent-model/</a></p>'
            '<p><strong>Help/Ayuda:</strong> <a href="https://github.com/geoinnova/maxent-model-qgis-plugin/blob/master/Manual_Adaptador_Maxent_para_QGIS.pdf/</a></p>'
            '<p><strong>Issues:</strong> <a href="https://github.com/geoinnova/maxent-model-qgis-plugin/issues">GitHub</a></p>'
            '<p><strong>Github:</strong> <a href="https://github.com/geoinnova/maxent-model-qgis-plugin">GitHub</a></p>')

    def get_license_text(self):
        with open(os.path.join(CURR_PATH, 'LICENSE')) as f:
            return f.read()
