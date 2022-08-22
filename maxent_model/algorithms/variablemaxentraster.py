"""
Model exported as python.
Name : 22 Estandarización de variables (continua-ráster)
Group : Adaptación de variables ASCII
With QGIS : 31609
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterRasterDestination
from qgis.core import QgsProcessingParameterBoolean
import processing

from PyQt5.QtGui import QIcon
from os import path

__author__ = 'Roberto Matellanes. Gis&Beers'
__date__ = '2022-08-17'
__copyright__ = '(C) 2022 by Roberto Matellanes. Gis&Beers'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

class EstandarizacinDeVariablesContinuarster(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('Limites', 'Límites territoriales de influencia de variables', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('Raster', 'Variable ráster ambiental', defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('Resolucion', 'Resolución de píxel estandarizada para Maxent', type=QgsProcessingParameterNumber.Double, minValue=-1.79769e+308, maxValue=1.79769e+308, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('CapaRasterDeSalidaParaMaxent', 'Capa raster de salida para Maxent', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # Cortar ráster por capa de máscara
        alg_params = {
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': True,
            'DATA_TYPE': 0,
            'EXTRA': '',
            'INPUT': parameters['Raster'],
            'KEEP_RESOLUTION': False,
            'MASK': parameters['Limites'],
            'MULTITHREADING': False,
            'NODATA': None,
            'OPTIONS': '',
            'SET_RESOLUTION': True,
            'SOURCE_CRS': 'ProjectCrs',
            'TARGET_CRS': 'ProjectCrs',
            'X_RESOLUTION': parameters['Resolucion'],
            'Y_RESOLUTION': parameters['Resolucion'],
            'OUTPUT': parameters['CapaRasterDeSalidaParaMaxent']
        }
        outputs['CortarRsterPorCapaDeMscara'] = processing.run('gdal:cliprasterbymasklayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['CapaRasterDeSalidaParaMaxent'] = outputs['CortarRsterPorCapaDeMscara']['OUTPUT']
        return results

    def name(self):
        return 'Estandarización de variables (continua-ráster)'

    def displayName(self):
        return 'Estandarización de variables (continua-ráster)'

    def group(self):
        return 'Adaptación de variables ASCII'

    def groupId(self):
        return 'Adaptación de variables ASCII'

    def shortHelpString(self):
        return """<html><body><h2>Descripción del algoritmo</h2>
<p>Rasterización de variables ambientales ráster contínuas bajo una resolución estandarizada para Maxent.</p>
<h2>Parámetros de entrada</h2>
<h3>Límites territoriales de influencia de variables</h3>
<p>Límites territoriales para los que es efectiva la distribución de citas y vinculadas con las variables territoriales de análisis.</p>
<h3>Variable ráster ambiental</h3>
<p>Variable ráster ambiental objeto de análisis.</p>
<h3>Resolución de píxel estandarizada para Maxent</h3>
<p>Resolución de píxel estandarizada para el proyecto de Maxent.</p>
<h3>Capa raster de salida para Maxent</h3>
<h3>Capa raster de salida para Maxent</h3>
<p>Variable ráster ambiental adaptada para Maxent.</p>
<br><p align="right">Autor del algoritmo: Roberto Matellanes Ferreras (www.gisandbeers.com)</p></body></html>"""

    def createInstance(self):
        return EstandarizacinDeVariablesContinuarster()

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QIcon(path.dirname(__file__) + '/icons/icon22.png')