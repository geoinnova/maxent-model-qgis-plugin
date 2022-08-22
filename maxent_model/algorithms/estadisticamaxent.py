# -*- coding: utf-8 -*-

"""
Model exported as python.
Name : 40 Estadísticas de variables continuas sobre distribuciones
Group : Herramientas auxiliares de procesado
With QGIS : 31609
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterBoolean
import processing

from PyQt5.QtGui import QIcon
from os import path

__author__ = 'Roberto Matellanes. Gis&Beers'
__date__ = '2022-08-17'
__copyright__ = '(C) 2022 by Roberto Matellanes. Gis&Beers'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

class EstadsticasDeVariablesContinuasSobreDistribuciones(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('Distribucindecitas', 'Distribución de citas', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('Radiodeinfluencia', 'Radio de influencia', type=QgsProcessingParameterNumber.Double, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('Variableambiental', 'Variable ambiental', defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('EstadisticasDeCitas', 'Estadisticas de citas', type=QgsProcessing.TypeVectorPoint, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # Buffer
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': parameters['Radiodeinfluencia'],
            'END_CAP_STYLE': 0,
            'INPUT': parameters['Distribucindecitas'],
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Estadísticas de zona
        alg_params = {
            'COLUMN_PREFIX': 'Sta_',
            'INPUT': outputs['Buffer']['OUTPUT'],
            'INPUT_RASTER': parameters['Variableambiental'],
            'RASTER_BAND': 1,
            'STATISTICS': [0,1,2,3,4,5,6,7,8,9,10,11],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['EstadsticasDeZona'] = processing.run('native:zonalstatisticsfb', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Centroides
        alg_params = {
            'ALL_PARTS': True,
            'INPUT': outputs['EstadsticasDeZona']['OUTPUT'],
            'OUTPUT': parameters['EstadisticasDeCitas']
        }
        outputs['Centroides'] = processing.run('native:centroids', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['EstadisticasDeCitas'] = outputs['Centroides']['OUTPUT']
        return results

    def name(self):
        return 'Estadísticas de variables continuas sobre distribuciones'

    def displayName(self):
        return 'Estadísticas de variables continuas sobre distribuciones'

    def group(self):
        return 'Herramientas auxiliares de procesado'

    def groupId(self):
        return 'Herramientas auxiliares de procesado'

    def shortHelpString(self):
        return """<html><body><h2>Descripción del algoritmo</h2>
<p>Generación de datos estadísticos de las variables ráster ambientales (continuas) a partir de una zona de influencia sobre cada coordenada de distribución de la especie.
NOTA: no utilizar para obtener datos estadísticos de variables categóricas.</p>
<h2>Parámetros de entrada</h2>
<h3>Distribución de citas</h3>
<p>Coordenadas de distribución de la especie o especies.</p>
<h3>Radio de influencia</h3>
<p>Radio de influencia territorial sobre los que obtener los datos estadísticos de las variables asociadas a cada cita.</p>
<h3>Variable ambiental</h3>
<p>Variable ráster ambiental (continua) objeto de análisis.</p>
<h3>Estadisticas de citas</h3>
<h3>Estadisticas de citas</h3>
<p>Datos de estadística zonal por coordenada de distribución.</p>
<br><p align="right">Autor del algoritmo: Roberto Matellanes Ferreras (www.gisandbeers.com)</p></body></html>"""

    def createInstance(self):
        return EstadsticasDeVariablesContinuasSobreDistribuciones()

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QIcon(path.dirname(__file__) + '/icons/icon40.png')