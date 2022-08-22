"""
Model exported as python.
Name : Adaptación de variables por distancia
Group : Adaptación de variables ASCII
With QGIS : 31609
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterRasterDestination
from qgis.core import QgsProcessingParameterBoolean

import processing

from PyQt5.QtGui import QIcon

from os import path

__author__ = 'Roberto Matellanes. Gis&Beers'
__date__ = '2022-08-17'
__copyright__ = '(C) 2022 by Roberto Matellanes. Gis&Beers'

__revision__ = '$Format:%H$'

class AdaptacinDeVariablesPorDistancia(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('Limitesterritorialesdeinfluenciadevariables', 'Límites territoriales de influencia de variables', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('Variablevectorial', 'Variable vectorial ambiental a rellenar', types=[QgsProcessing.TypeVector], defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('Distanciamxima', 'Distancia máxima', type=QgsProcessingParameterNumber.Double, defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('Valordecontrolderelleno', 'Valor de control de relleno', type=QgsProcessingParameterNumber.Double, defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('Resoluciondepixel', 'Resolución de píxel estandarizada para Maxent', type=QgsProcessingParameterNumber.Double, minValue=-1.79769e+308, maxValue=1.79769e+308, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('rasterdereferencia', 'Variable raster de referencia', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('RellenoDeVariableAmbiental', 'Relleno de variable ambiental', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(6, model_feedback)
        results = {}
        outputs = {}

        # Rasterizar a cero
        alg_params = {
            'CELLSIZE': 0,
            'CRS': None,
            'EXPRESSION': '\"Variable raster de referencia@1\" * 0',
            'EXTENT': None,
            'LAYERS': parameters['rasterdereferencia'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RasterizarACero'] = processing.run('qgis:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Cortar elementos territoriales
        alg_params = {
            'INPUT': parameters['Variablevectorial'],
            'OVERLAY': parameters['Limitesterritorialesdeinfluenciadevariables'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CortarElementosTerritoriales'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Variable vectorial rasterizada
        alg_params = {
            'BURN': 0,
            'DATA_TYPE': 5,
            'EXTENT': parameters['rasterdereferencia'],
            'EXTRA': '',
            'FIELD': '',
            'HEIGHT': parameters['Resoluciondepixel'],
            'INIT': None,
            'INPUT': outputs['CortarElementosTerritoriales']['OUTPUT'],
            'INVERT': False,
            'NODATA': 0,
            'OPTIONS': '',
            'UNITS': 1,
            'WIDTH': parameters['Resoluciondepixel'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['VariableVectorialRasterizada'] = processing.run('gdal:rasterize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Proximidad (distancia ráster)
        alg_params = {
            'BAND': 1,
            'DATA_TYPE': 5,
            'EXTRA': '',
            'INPUT': outputs['VariableVectorialRasterizada']['OUTPUT'],
            'MAX_DISTANCE': parameters['Distanciamxima'],
            'NODATA': parameters['Valordecontrolderelleno'],
            'OPTIONS': '',
            'REPLACE': 0,
            'UNITS': 0,
            'VALUES': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ProximidadDistanciaRster'] = processing.run('gdal:proximity', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Relleno valores nulos
        alg_params = {
            '-c': False,
            '-f': False,
            '-i': False,
            '-n': False,
            '-r': False,
            'GRASS_RASTER_FORMAT_META': '',
            'GRASS_RASTER_FORMAT_OPT': '',
            'GRASS_REGION_CELLSIZE_PARAMETER': 0,
            'GRASS_REGION_PARAMETER': None,
            'map': outputs['ProximidadDistanciaRster']['OUTPUT'],
            'null': parameters['Valordecontrolderelleno'],
            'setnull': '',
            'output': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RellenoValoresNulos'] = processing.run('grass7:r.null', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Recortar raster rellenado
        alg_params = {
            'GRID': outputs['RellenoValoresNulos']['output'],
            'MASK': outputs['RasterizarACero']['OUTPUT'],
            'MASKED': parameters['RellenoDeVariableAmbiental']
        }
        outputs['RecortarRasterRellenado'] = processing.run('saga:rastermasking', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['RellenoDeVariableAmbiental'] = outputs['RecortarRasterRellenado']['MASKED']
        return results

    def name(self):
        return 'Adaptación de variables por distancia'

    def displayName(self):
        return 'Adaptación de variables por distancia'

    def group(self):
        return 'Adaptación de variables ASCII'

    def groupId(self):
        return 'Adaptación de variables ASCII'

    def shortHelpString(self):
        return """<html><body><h2>Descripción del algoritmo</h2>
<p>Genera una variable continua por influencia de distancia para elementos lineales o aislados basados en varibles como ríos, carreteras, masas de agua, núcleos urbanos, etc.</p>
<h2>Parámetros de entrada</h2>
<h3>Límites territoriales de influencia de variables</h3>
<p>Límites territoriales para los que es efectiva la distribución de citas y vinculadas con las variables territoriales de análisis.</p>
<h3>Variable vectorial ambiental a rellenar</h3>
<p>Variable ambiental vectorial dispersa o lineal objeto de procesado.</p>
<h3>Distancia máxima</h3>
<p>Distancia máxima de cálculo de influencia sobre los elementos vectoriales.</p>
<h3>Valor de control de relleno</h3>
<p>Valor de píxel de relleno.</p>
<h3>Resolución de píxel estandarizada para Maxent</h3>
<p>Resolución de píxel estandarizada para el proyecto de Maxent.</p>
<h3>Variable raster de referencia</h3>
<p>Límites de otra variable ráster ambiental de referencia espacial.</p>
<h3>Relleno de variable ambiental</h3>
<p>Variable ráster de distancia.</p>
<p></p>
<h2>Salidas</h2>
<h3>Relleno de variable ambiental</h3>
<p>Variable ráster de distancia.</p>
<br><p align="right">Autor del algoritmo: Roberto Matellanes Ferreras (www.gisandbeers.com)</p></body></html>"""

    def createInstance(self):
        return AdaptacinDeVariablesPorDistancia()

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QIcon(path.dirname(__file__) + '/icons/icon20.png')