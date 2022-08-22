# -*- coding: utf-8 -*-

"""
Model exported as python.
Name : 10 Adaptación de coordenadas de especies
Group : Adaptación de coordenadas CSV
With QGIS : 31609
"""

__author__ = 'Roberto Matellanes. Gis&Beers'
__date__ = '2022-08-17'
__copyright__ = '(C) 2022 by Roberto Matellanes. Gis&Beers'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterField
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterDefinition
import processing

from PyQt5.QtGui import QIcon
from os import path

class AdaptacinDeCoordenadasDeEspecies(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('Citasdeespecies', 'Coordenadas de citas de especies', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        param = QgsProcessingParameterField('Campodenombreespecie', 'Campos de omisión', optional=True, type=QgsProcessingParameterField.Any, parentLayerParameterName='Citasdeespecies', allowMultiple=True, defaultValue='')
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
        self.addParameter(QgsProcessingParameterVectorLayer('Limitesinfluencia', 'Límites de influencia de variables', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('CoordenadasAdaptadasAMaxent', 'Coordenadas adaptadas a Maxent', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # Extraer por ubicacion 
        alg_params = {
            'INPUT': parameters['Citasdeespecies'],
            'INTERSECT': parameters['Limitesinfluencia'],
            'PREDICATE': [0],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtraerPorUbicacion'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Quitar campo(s)
        alg_params = {
            'COLUMN': parameters['Campodenombreespecie'],
            'INPUT': outputs['ExtraerPorUbicacion']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['QuitarCampos'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Añadir campos X/Y a capa
        alg_params = {
            'CRS': 'ProjectCrs',
            'INPUT': outputs['QuitarCampos']['OUTPUT'],
            'PREFIX': 'Coordenada ',
            'OUTPUT': parameters['CoordenadasAdaptadasAMaxent']
        }
        outputs['AadirCamposXyACapa'] = processing.run('native:addxyfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['CoordenadasAdaptadasAMaxent'] = outputs['AadirCamposXyACapa']['OUTPUT']
        return results

    def name(self):
        return 'Adaptación de coordenadas de especies'

    def displayName(self):
        return 'Adaptación de coordenadas de especies'

    def group(self):
        return 'Adaptación de coordenadas CSV'

    def groupId(self):
        return 'Adaptación de coordenadas CSV'

    def shortHelpString(self):
        return """<html><body><h2>Descripción del algoritmo</h2>
<p>Adapta la cartografía de coordenadas de distribución de especies para hacerla compatible al formato CSV de Maxent empleando los nombres de las especies y sus coordenadas de referencia dentro de la zona de trabajo.</p>
<h2>Parámetros de entrada</h2>
<h3>Coordenadas de citas de especies</h3>
<p>Coordenadas de distribución de la especie o especies objeto de análisis.</p>
<h3>Campos de omisión</h3>
<p>Campos a omitir en la salida de los datos finales.</p>
<h3>Límites de influencia de variables</h3>
<p>Límites territoriales para los que es efectiva la distribución de citas y vinculadas con las variables territoriales de análisis.</p>
<h2>Salidas</h2>
<h3>Coordenadas adaptadas a Maxent</h3>
<p>Coordenadas de distribución adaptadas a Maxent.</p>
<br><p align="right">Autor del algoritmo: Roberto Matellanes Ferreras (www.gisandbeers.com)</p></body></html>"""

    def createInstance(self):
        return AdaptacinDeCoordenadasDeEspecies()

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QIcon(path.dirname(__file__) + '/icons/icon10.png')

