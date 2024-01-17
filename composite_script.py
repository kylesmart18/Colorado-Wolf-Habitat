# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 17:18:24 2022

@author: kyles
"""

import arcpy, sys
import math
from arcpy import env
from arcpy.sa import *
import pandas as pd
import numpy as np
from arcpy import sa
from arcpy.sa import *

path = sys.path[0]
arcpy.env.workspace = path

grazing = 'grazing\grazing_clip.shp'

#clip colorado to grazing boundry to make grazing one polygon
arcpy.Clip_analysis('state_boundries\colorado.shp',grazing,
                      'grazing\grazing_polygon.shp')

#erase single polygon grazing shapefile from colorado polygon
arcpy.analysis.Erase('state_boundries\colorado.shp', 'grazing\grazing_polygon.shp', 
                     'grazing\colorado_grazing_erased.shp')

#clip raster to grazing boundry
arcpy.Clip_management('land_cover\split_raster_colorado\composite_raster.tif',
                      '-1146479.879393 1566911.199632 -504612.461596 2073714.577637',
                      'land_cover\rng.tif','grazing\colorado_grazing_erased.shp',
                      '0','ClippingGeometry','NO_MAINTAIN_EXTENT')

#dissolve 
arcpy.management.Dissolve('results\AllPreyRanked.shp',
                          'land_cover\prey_range_dissolved.shp')

#clip raster to prey range to make final raster
inp = 'land_cover\rng'
output = 'land_cover\rng_prey.tif' #fix the \r issues in variable explorer
arcpy.Clip_management(inp,
                      '-1146474.409964 1566913.562029 -513480.273169 2073713.415332',
                      output,'land_cover\prey_range_dissolved.shp',
                      '0','ClippingGeometry','NO_MAINTAIN_EXTENT')

