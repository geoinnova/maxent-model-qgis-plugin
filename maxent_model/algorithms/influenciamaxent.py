# -*- coding: utf-8 -*-

"""
Model exported as python.
Name : 42 Recortar variable por zona de influencia
Group : Herramientas auxiliares de procesado
With QGIS : 31609
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
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

class RecortarVariablePorZonaDeInfluencia(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('VariablersterparaMaxent', 'Variable ráster para Maxent', defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('Distancianegativadeinfluencia', 'Distancia negativa de influencia', type=QgsProcessingParameterNumber.Double, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('VariableAmbientalDelimitadaPorInfluencia', 'Variable ambiental delimitada por influencia', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(4, model_feedback)
        results = {}
        outputs = {}

        # Raster calculator
        alg_params = {
            'CELLSIZE': 0,
            'CRS': None,
            'EXPRESSION': '\"Variable ráster para Maxent@1\" * 0',
            'EXTENT': None,
            'LAYERS': parameters['VariablersterparaMaxent'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RasterCalculator'] = processing.run('qgis:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Poligonizar (ráster a vectorial)
        alg_params = {
            'BAND': 1,
            'EIGHT_CONNECTEDNESS': False,
            'EXTRA': '',
            'FIELD': 'DN',
            'INPUT': outputs['RasterCalculator']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PoligonizarRsterAVectorial'] = processing.run('gdal:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Buffer
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': parameters['Distancianegativadeinfluencia'],
            'END_CAP_STYLE': 0,
            'INPUT': outputs['PoligonizarRsterAVectorial']['OUTPUT'],
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Cortar ráster por capa de máscara
        alg_params = {
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': True,
            'DATA_TYPE': 0,
            'EXTRA': '',
            'INPUT': parameters['VariablersterparaMaxent'],
            'KEEP_RESOLUTION': False,
            'MASK': outputs['Buffer']['OUTPUT'],
            'MULTITHREADING': False,
            'NODATA': None,
            'OPTIONS': '',
            'SET_RESOLUTION': False,
            'SOURCE_CRS': 'ProjectCrs',
            'TARGET_CRS': None,
            'X_RESOLUTION': None,
            'Y_RESOLUTION': None,
            'OUTPUT': parameters['VariableAmbientalDelimitadaPorInfluencia']
        }
        outputs['CortarRsterPorCapaDeMscara'] = processing.run('gdal:cliprasterbymasklayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['VariableAmbientalDelimitadaPorInfluencia'] = outputs['CortarRsterPorCapaDeMscara']['OUTPUT']
        return results

    def name(self):
        return 'Recortar variable por zona de influencia'

    def displayName(self):
        return 'Recortar variable por zona de influencia'

    def group(self):
        return 'Herramientas auxiliares de procesado'

    def groupId(self):
        return 'Herramientas auxiliares de procesado'

    def shortHelpString(self):
        return """<html><body><h2>Descripción del algoritmo</h2>
<p>Redimensiona los límites máximos de la zona de trabajo de una capa ráster para omisión de potenciales valores periféricos (fronteras, límites de costa, islas...)</p>
<h2>Parámetros de entrada</h2>
<h3>Variable ráster para Maxent</h3>
<p>Variable ráster ambiental objeto de análisis.</p>
<h3>Distancia negativa de influencia</h3>
<p>Distancia de omisión de límites (valores negativos)</p>
<h2>Salidas</h2>
<h3>Variable ambiental delimitada por influencia</h3>
<p>Variable ráster ambiental acotada perimétricamente.</p>
<br><p align="right">Autor del algoritmo: Roberto Matellanes Ferreras (www.gisandbeers.com)</p></body></html>"""

    def createInstance(self):
        return RecortarVariablePorZonaDeInfluencia()

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QIcon(path.dirname(__file__) + '/icons/icon42.png')