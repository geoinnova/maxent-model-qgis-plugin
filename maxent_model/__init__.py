# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MaxentModel
                                 A QGIS plugin
 Maxent Model Description
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-08-17
        copyright            : (C) 2022 by Roberto Matellanes. Gis&Beers
        email                : correo@correo.es
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'Roberto Matellanes. Gis&Beers'
__date__ = '2022-08-17'
__copyright__ = '(C) 2022 by Roberto Matellanes. Gis&Beers'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load MaxentModel class from file MaxentModel.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .maxent_model import MaxentModelPlugin
    return MaxentModelPlugin(iface)