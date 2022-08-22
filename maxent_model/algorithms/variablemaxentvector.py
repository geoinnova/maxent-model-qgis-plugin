"""
Model exported as python.
Name : 21 Estandarización de variables (categorica-vector)
Group : Adaptación de variables ASCII
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

class EstandarizacinDeVariablesCategoricavector(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('Limitesterritorialesdeinfluenciadevariables', 'Límites territoriales de influencia de variables', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('Variablevectorial', 'Variable vectorial ambiental', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterField('Campoquecontieneelvalordelavariable', 'Campo que contiene el valor de la variable', type=QgsProcessingParameterField.Numeric, parentLayerParameterName='Variablevectorial', allowMultiple=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterNumber('Resoluciondepixel', 'Resolución de píxel estandarizada para Maxent', type=QgsProcessingParameterNumber.Double, minValue=-1.79769e+308, maxValue=1.79769e+308, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('CapaVectorialRasterizadaDeSalidaParaMaxent', 'Capa vectorial rasterizada de salida para Maxent', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # Extraer por ubicacion 
        alg_params = {
            'INPUT': parameters['Variablevectorial'],
            'INTERSECT': 'Limite_Demarcacion_Ebro_c837559a_0494_4177_882f_71dd55fdeb90',
            'PREDICATE': [0],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtraerPorUbicacion'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Variable vectorial rasterizada
        alg_params = {
            'BURN': 0,
            'DATA_TYPE': 5,
            'EXTENT': parameters['Limitesterritorialesdeinfluenciadevariables'],
            'EXTRA': '',
            'FIELD': parameters['Campoquecontieneelvalordelavariable'],
            'HEIGHT': parameters['Resoluciondepixel'],
            'INIT': None,
            'INPUT': outputs['ExtraerPorUbicacion']['OUTPUT'],
            'INVERT': False,
            'NODATA': 0,
            'OPTIONS': '',
            'UNITS': 1,
            'WIDTH': parameters['Resoluciondepixel'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['VariableVectorialRasterizada'] = processing.run('gdal:rasterize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Cortar ráster por capa de máscara
        alg_params = {
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': True,
            'DATA_TYPE': 0,
            'EXTRA': '',
            'INPUT': outputs['VariableVectorialRasterizada']['OUTPUT'],
            'KEEP_RESOLUTION': False,
            'MASK': parameters['Limitesterritorialesdeinfluenciadevariables'],
            'MULTITHREADING': False,
            'NODATA': None,
            'OPTIONS': '',
            'SET_RESOLUTION': True,
            'SOURCE_CRS': 'ProjectCrs',
            'TARGET_CRS': 'ProjectCrs',
            'X_RESOLUTION': parameters['Resoluciondepixel'],
            'Y_RESOLUTION': parameters['Resoluciondepixel'],
            'OUTPUT': parameters['CapaVectorialRasterizadaDeSalidaParaMaxent']
        }
        outputs['CortarRsterPorCapaDeMscara'] = processing.run('gdal:cliprasterbymasklayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['CapaVectorialRasterizadaDeSalidaParaMaxent'] = outputs['CortarRsterPorCapaDeMscara']['OUTPUT']
        return results

    def name(self):
        return 'Estandarización de variables (categorica-vector)'

    def displayName(self):
        return 'Estandarización de variables (categorica-vector)'

    def group(self):
        return 'Adaptación de variables ASCII'

    def groupId(self):
        return 'Adaptación de variables ASCII'

    def shortHelpString(self):
        return """<html><body><h2>Descripción del algoritmo</h2>
<p>Rasterización de variables ambientales vectoriales categóricas bajo una resolución estandarizada para Maxent.</p>
<h2>Parámetros de entrada</h2>
<h3>Límites territoriales de influencia de variables</h3>
<p>Límites territoriales para los que es efectiva la distribución de citas y vinculadas con las variables territoriales de análisis.</p>
<h3>Variable vectorial ambiental</h3>
<p>Variable ambiental vectorial a procesar.</p>
<h3>Campo que contiene el valor de la variable</h3>
<p>Campo que contiene el identificador categórico de la variable.</p>
<h3>Resolución de píxel estandarizada para Maxent</h3>
<p>Resolución de píxel estandarizada para el proyecto de Maxent.</p>
<h2>Salidas</h2>
<h3>Capa vectorial rasterizada de salida para Maxent</h3>
<p>Capa vectorial categórica rasterizada.</p>
<br><p align="right">Autor del algoritmo: Roberto Matellanes Ferreras (www.gisandbeers.com)</p></body></html>"""

    def createInstance(self):
        return EstandarizacinDeVariablesCategoricavector()

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QIcon(path.dirname(__file__) + '/icons/icon21.png')