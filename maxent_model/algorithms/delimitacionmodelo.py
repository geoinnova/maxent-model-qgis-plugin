# -*- coding: utf-8 -*-

"""
Model exported as python.
Name : 30 Delimitación de zonas
Group : Analisis postmodelado
With QGIS : 31609
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterRasterDestination
from qgis.core import QgsProcessingParameterBoolean

from qgis.PyQt.QtCore import QCoreApplication

import processing

from PyQt5.QtGui import QIcon
from os import path

__author__ = 'Roberto Matellanes. Gis&Beers'
__date__ = '2022-08-17'
__copyright__ = '(C) 2022 by Roberto Matellanes. Gis&Beers'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

class DelimitacinDeZonas(QgsProcessingAlgorithm):

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('ModeloprocesadoporMaxent', 'Modelo procesado por Maxent', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('ponderacion', 'Clasificación de tipologías', types=[QgsProcessing.TypeVector], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('DelimitacinDeZonasVector', 'Delimitación de zonas (vector)', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('DelimitacinDeZonasRaster', 'Delimitación de zonas (raster)', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        outputs = {}

        # Reclasificar por capa
        alg_params = {
            'DATA_TYPE': 5,
            'INPUT_RASTER': parameters['ModeloprocesadoporMaxent'],
            'INPUT_TABLE': parameters['ponderacion'],
            'MAX_FIELD': 'Max',
            'MIN_FIELD': 'Min',
            'NODATA_FOR_MISSING': False,
            'NO_DATA': -9999,
            'RANGE_BOUNDARIES': 0,
            'RASTER_BAND': 1,
            'VALUE_FIELD': 'Categoria',
            'OUTPUT': parameters['DelimitacinDeZonasRaster']
        }
        outputs['ReclasificarPorCapa'] = processing.run('native:reclassifybylayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['DelimitacinDeZonasRaster'] = outputs['ReclasificarPorCapa']['OUTPUT']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Píxeles ráster a polígonos
        alg_params = {
            'FIELD_NAME': 'VALUE',
            'INPUT_RASTER': outputs['ReclasificarPorCapa']['OUTPUT'],
            'RASTER_BAND': 1,
            'OUTPUT': parameters['DelimitacinDeZonasVector']
        }
        outputs['PxelesRsterAPolgonos'] = processing.run('native:pixelstopolygons', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['DelimitacinDeZonasVector'] = outputs['PxelesRsterAPolgonos']['OUTPUT']
        return results

    def name(self):
        return 'Delimitación de zonas'

    def displayName(self):
        return self.tr('Delimitación de zonas')

    def group(self):
        return self.tr('Analisis postmodelado')

    def groupId(self):
        return 'Analisis postmodelado'

    def shortHelpString(self):
        return self.tr("""<html><body><h2>Descripción del algoritmo</h2>
<p>Delimita territorialmente las zonas por éxito del modelo generado en Maxent a través de límites vectoriales y límites ráster.</p>
<h2>Parámetros de entrada</h2>
<h3>Modelo procesado por Maxent</h3>
<p>Modelo ASCII generado por Maxent.</p>
<h3>Clasificación de tipologías</h3>
<p>Asignación de tipologías territoriales a través de archivo CSV. Los campos disponibles deben estar separados por comas y con la estructura de campos: Categoria, Min, Max
Categoria: clase de la zona
Min: valor mínimo de la clase
Max: valor máximo de la clase</p>
<h2>Salidas</h2>
<h3>Delimitación de zonas (vector)</h3>
<p>Zonas territoriales de éxito del modelo (vector).</p>
<h3>Delimitación de zonas (raster)</h3>
<p>Zonas territoriales de éxito del modelo (ráster).</p>
<br><p align="right">Autor del algoritmo: Roberto Matellanes Ferreras (www.gisandbeers.com)</p></body></html>""")

    def createInstance(self):
        return DelimitacinDeZonas()

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QIcon(path.dirname(__file__) + '/icons/icon30.png')