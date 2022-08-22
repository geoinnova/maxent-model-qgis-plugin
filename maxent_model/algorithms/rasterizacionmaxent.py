# -*- coding: utf-8 -*-

"""
Model exported as python.
Name : 41 Rasterización de variables categóricas
Group : Herramientas auxiliares de procesado
With QGIS : 31609
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterField
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

class RasterizacinDeVariablesCategricas(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('Variableambientalvectorialarasterizar', 'Variable vectorial ambiental a rasterizar', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterField('Campodevalordevariable', 'Campo de valor de variable', type=QgsProcessingParameterField.Any, parentLayerParameterName='Variableambientalvectorialarasterizar', allowMultiple=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterNumber('ResolucindepxelestandarizadaparaMaxent', 'Resolución de píxel estandarizada para Maxent', type=QgsProcessingParameterNumber.Double, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('VariableVectorialAmbientalRasterizada', 'Variable vectorial ambiental rasterizada', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # Rasterizacion variable vectorial
        alg_params = {
            'BURN': 0,
            'DATA_TYPE': 5,
            'EXTENT': parameters['Variableambientalvectorialarasterizar'],
            'EXTRA': '',
            'FIELD': parameters['Campodevalordevariable'],
            'HEIGHT': parameters['ResolucindepxelestandarizadaparaMaxent'],
            'INIT': None,
            'INPUT': parameters['Variableambientalvectorialarasterizar'],
            'INVERT': False,
            'NODATA': 0,
            'OPTIONS': '',
            'UNITS': 1,
            'WIDTH': parameters['ResolucindepxelestandarizadaparaMaxent'],
            'OUTPUT': parameters['VariableVectorialAmbientalRasterizada']
        }
        outputs['RasterizacionVariableVectorial'] = processing.run('gdal:rasterize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['VariableVectorialAmbientalRasterizada'] = outputs['RasterizacionVariableVectorial']['OUTPUT']
        return results

    def name(self):
        return 'Rasterización de variables categóricas'

    def displayName(self):
        return 'Rasterización de variables categóricas'

    def group(self):
        return 'Herramientas auxiliares de procesado'

    def groupId(self):
        return 'Herramientas auxiliares de procesado'

    def shortHelpString(self):
        return """<html><body><h2>Descripción del algoritmo</h2>
<p>Convierte una variable ambiental vectorial en una variable ráster a partir de un identificador de clase.</p>
<h2>Parámetros de entrada</h2>
<h3>Variable vectorial ambiental a rasterizar</h3>
<p>Variable vectorial ambiental objeto de análisis.</p>
<h3>Campo de valor de variable</h3>
<p>Campo que contiene el identificador categórico de la variable.</p>
<h3>Resolución de píxel estandarizada para Maxent</h3>
<p>Resolución de píxel estandarizada para el proyecto de Maxent.</p>
<h2>Salidas</h2>
<h3>Variable vectorial ambiental rasterizada</h3>
<p>Variable vectorial rasterizada.</p>
<br><p align="right">Autor del algoritmo: Roberto Matellanes Ferreras (www.gisandbeers.com)</p></body></html>"""

    def createInstance(self):
        return RasterizacinDeVariablesCategricas()

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QIcon(path.dirname(__file__) + '/icons/icon41.png')