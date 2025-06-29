# -*- coding: utf-8 -*-
"""
GISENGINE Plugin for QGIS
Point d'entrée du plugin
"""

def classFactory(iface):
    """
    Load GISENGINEPlugin class from file gisengine_plugin.py
    
    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .gisengine_plugin import GISENGINEPlugin
    return GISENGINEPlugin(iface)