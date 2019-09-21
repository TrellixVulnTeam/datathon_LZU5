########################################################
# Copyright © Growing Data Pty Ltd, Australia
# AUTHOR: Michael-James Coetzee, Amit Wats
# EMAIL: mj@growingdata.com.au, amit@growingdata.com.au
########################################################

## The file GeneratTiles.py generated the .geojson files that contain the tile GPS coordinates (in the geometries folder) and tile .png images (in the tiles folder)  

import json
from PIL import Image
from shapely import geometry
import geopandas as gpd
#import pandas as pd
#import numpy as np
from GeoLibrary import *
from math import atan,degrees,sqrt
import configparser as ConfigParser


#Prevent Image from throwing warning as the
#Image File is Big
Image.MAX_IMAGE_PIXELS = 1000000000

#Initialise the Config File
config = ConfigParser.ConfigParser()
config.read('geo.config')


GRID_WIDTH=int(config.get('Master Image', 'GRID_WIDTH'))
GRID_HEIGHT=int(config.get('Master Image', 'GRID_HEIGHT'))

FULL_IMAGE_GEOMETRY=config.get('Master Image', 'FULL_GEOMETRY_PATH')
FULL_IMAGE_PATH=config.get('Master Image', 'FULL_IMAGE_PATH')
GEO_GEOMETRY_OUTPUT_FOLDER=config.get('Master Image', 'GEO_JSON_FOLDER')

with open(FULL_IMAGE_GEOMETRY) as f:
    pic = json.load(f)["geometry"]

fullImage=Image.open(FULL_IMAGE_PATH)
fullImageWidth,fullImageHeight = fullImage.size


#we will have 2 lines across and down.
# so staring in top left corner each datetime and denotiong p as 512/dimension(fullImageWidth or fullImageHeight depending)
# go right p portrion across TR tile, down p portion to get BL tile and go portion across followed by p portion down to get BR tile
#note: assumption pictures are squares! Check lines for parallel
# approach scale in x p portion of (x2-x1) and for y scale p portion of (y2-y1) at the started off set of (x1,y1) + current_tile_offset *scale across approach*

top_left_lat_long=tuple([k for k in pic['coordinates'][0][0]])
top_right_lat_long=tuple([k for k in pic['coordinates'][0][1]])
bottom_right_lat_long=tuple([k for k in pic['coordinates'][0][2]])
bottom_left_lat_long=tuple([k for k in pic['coordinates'][0][3]])

def saveGeo(TL,TR,BR,BL,x_bit,y_bit):
    point_TL=geometry.Point(TL[0],TL[1])
    point_TR=geometry.Point(TR[0],TR[1])
    point_BR=geometry.Point(BR[0],BR[1])
    point_BL=geometry.Point(BL[0],BL[1])
    tile= geometry.Polygon([p.x,p.y] for p in [point_TL,point_TR,point_BR,point_BL])
    tile_geoseries=gpd.GeoSeries([tile])
    tile_gpd= gpd.GeoDataFrame(geometry=tile_geoseries)
    tile_gpd.crs = {'init': 'epsg:4326', 'no_defs': True}
    tile_gpd.to_file(GetGeoJSONName(x_bit,y_bit), driver="GeoJSON")

# the GeoLibrary file uses a convention where the
# latitute and longitute are in opposite orders
# This function heps swap the position while passing parameters
# As well as when results from the library are returned


def CreateCroppedImage(coords):
    tile=fullImage.crop((coords[0][0],coords[0][1],coords[2][0],coords[2][1]))
    tile.save(GetTileName(coords[0][0],coords[0][1]))

def GetFourPositions(x,y):
    top_left_pos=(GRID_WIDTH*x,GRID_HEIGHT*y)
    top_right_pos=(GRID_WIDTH*(x+1)-1,GRID_HEIGHT*y)
    bottom_left_pos=(GRID_WIDTH*x,GRID_HEIGHT*(y+1)-1)
    bottom_right_pos=(GRID_WIDTH*(x+1)-1,GRID_HEIGHT*(y+1)-1)
    return [top_left_pos,top_right_pos,bottom_right_pos, bottom_left_pos]


# Can be invoked externally to generate the
# Geo JSON of the x'th and y'th square position
def GenerateAndSaveTileGeo(x,y):
    fourLatLongPositions=[GetLatLongForCoords(r[0],r[1]) for r in GetFourPositions(x,y)]
    saveGeo(fourLatLongPositions[0],fourLatLongPositions[1],
            fourLatLongPositions[2],fourLatLongPositions[3],x*GRID_WIDTH,y*GRID_HEIGHT)
    fourCoordinates=GetFourPositions(x,y)
    CreateCroppedImage(fourCoordinates)

# The main method generates the GEO JSON files in the configured
# folder
if __name__ == "__main__":
    im = Image.open(FULL_IMAGE_PATH)
    numOfXSquares=fullImageWidth//GRID_WIDTH
    numOfYSquares=fullImageHeight//GRID_HEIGHT
    im = Image.open(FULL_IMAGE_PATH)
    print("Generating files ......")
    [GenerateAndSaveTileGeo(x,y) for y in range(numOfYSquares) for x in range(numOfXSquares)]
    print("File Generation completed")
