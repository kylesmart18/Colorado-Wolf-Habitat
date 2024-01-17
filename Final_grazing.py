# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 12:35:02 2022

@author: louis
"""

import arcpy 
from arcpy import env
from arcpy import sa
import numpy as np

path = sys.path[0]
arcpy.env.workspace = path

env.overwriteOutput=1

raster= 'land_cover\colorado_raster.tif'

env.outputCoordinateSystem = arcpy.Describe(raster).spatialReference

'''reproject
'''
f = 'grazing\grazing_allot\allot.shp'
arcpy.Project_management(f,'grazing\allot_project.shp',env.outputCoordinateSystem)


'''
clip the BLM grazing land to the Colorado Raster
'''

arcpy.analysis.Clip('grazing\allot_project.shp', 'state_boundries\colorado.shp', 'grazing\grazing_clip.shp')


