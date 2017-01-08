# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GNSS_DOC_OPTIMIZER
                                 A QGIS plugin
 Ground Network optimization for GNSS
                             -------------------
        begin                : 2016-12-11
        copyright            : (C) 2016 by Mohamed Ali CHEBBI
        email                : Mohamed-Ali.Chebbi@ensg.eu
        git sha              : $Format:%H$
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

def classFactory(iface):  # pylint: disable=invalid-name
    """Load GNSS_DOC_OPTIMIZER class from file GNSS_DOC_OPTIMIZER.
    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .GNSS_plugin import GNSS_DOC_OPTIMIZER
    return GNSS_DOC_OPTIMIZER(iface)
