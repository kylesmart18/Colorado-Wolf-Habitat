# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 14:00:01 2022

@author: wtick
"""

import arcpy, sys
import os
from arcpy import env
from arcpy.sa import *
import numpy as np


path = sys.path[0]
arcpy.env.workspace = path

env.workspace = path
env.overwriteOutput = 1

env.outputCoordinateSystem = arcpy.Describe('land_cover/clipped_raster.tif').spatialReference

#Mule Deer 
MuleDeer = arcpy.management.Merge(['prey/MuleDeerWinterConc.shp','prey/MuleDeerResident.shp','prey/MuleDeerMigration.shp','prey/MuleDeerConc.shp','prey/MuleDeerLimitedUSe.shp'], "results/MuleDeer.shp", "NO_TEST")

MuleDeerUnion = arcpy.Union_analysis([MuleDeer, MuleDeer], 'results/MuleDeerUnion.shp', "ALL", "", "GAPS")

MuleDeerUSingle = arcpy.MultipartToSinglepart_management(MuleDeerUnion, 'results/MuleDeerUSingle.shp')

MuleDeerRanked = arcpy.SpatialJoin_analysis(MuleDeerUSingle, MuleDeerUSingle, 'results/MuleDeerRanked.shp', "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "ARE_IDENTICAL_TO", "", "")

arcpy.CalculateField_management(MuleDeerRanked, "Join_Count", "Sqr ( [Join_Count]  )", "VB", "")


#Elk 
Elk = arcpy.management.Merge(['prey/ElkWinterConcentration.shp','prey/ElkResident.shp','prey/ElkSummConc.shp','prey/ElkProd.shp'], "results/Elk.shp", "NO_TEST")

ElkUnion = arcpy.Union_analysis([Elk, Elk], 'results/ElkUnion.shp', "ALL", "", "GAPS")

ElkUSingle = arcpy.MultipartToSinglepart_management(ElkUnion, 'results/ElkUSingle.shp')

ElkRanked = arcpy.SpatialJoin_analysis(ElkUSingle, ElkUSingle, 'results/ElkRanked.shp', "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "ARE_IDENTICAL_TO", "", "")

arcpy.CalculateField_management(ElkRanked, "Join_Count", "Sqr ( [Join_Count]  )", "VB", "")


#Moose 
Moose = arcpy.management.Merge(['prey/MooseWinter.shp','prey/MooseConc.shp','prey/MoosePriorityHabitat.shp'], "results/Moose.shp", "NO_TEST")

MooseUnion = arcpy.Union_analysis([Moose, Moose], 'results/MooseUnion.shp', "ALL", "", "GAPS")

MooseUSingle = arcpy.MultipartToSinglepart_management(MooseUnion, 'results/MooseUSingle.shp')

MooseRanked = arcpy.SpatialJoin_analysis(MooseUSingle, MooseUSingle, 'results/MooseRanked.shp', "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "ARE_IDENTICAL_TO", "", "")

arcpy.CalculateField_management(MooseRanked, "Join_Count", "Sqr ( [Join_Count]  )", "VB", "")

#pronghorn
pronghorn = arcpy.management.Merge(['prey/PronghornConc.shp','prey/pronghornResident.shp','prey/pronghornMigration.shp','prey/pronghornLimitedUse.shp'], "results/pronghorn.shp", "NO_TEST")

pronghornUnion = arcpy.Union_analysis([pronghorn, pronghorn], 'results/pronghornUnion.shp', "ALL", "", "GAPS")

pronghornUSingle = arcpy.MultipartToSinglepart_management(pronghornUnion, 'results/pronghornUSingle.shp')

pronghornRanked = arcpy.SpatialJoin_analysis(pronghornUSingle, pronghornUSingle, 'results/pronghornRanked.shp', "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "ARE_IDENTICAL_TO", "", "")

arcpy.CalculateField_management(pronghornRanked, "Join_Count", "Sqr ( [Join_Count]  )", "VB", "")


#Final all prey
AllPrey = arcpy.management.Merge(["results/MuleDeer.shp","results/pronghorn.shp","results/Moose.shp","results/Elk.shp"], "results/AllPrey.shp", "NO_TEST")

AllPreyUnion = arcpy.Union_analysis([AllPrey, AllPrey], 'results/AllPreyUnion.shp', "ALL", "", "GAPS")

AllPreyUSingle = arcpy.MultipartToSinglepart_management(AllPreyUnion, 'results/AllPreyUSingle.shp')

AllPreyRanked = arcpy.SpatialJoin_analysis(AllPreyUSingle, AllPreyUSingle, 'results/AllPreyRanked.shp', "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "ARE_IDENTICAL_TO", "", "")

arcpy.CalculateField_management(AllPreyRanked, "Join_Count", "Sqr ( [Join_Count]  )", "VB", "")

arcpy.conversion.PolygonToRaster('results/AllPreyRanked.shp', "Join_Count", "results/AllPrRnkRast")