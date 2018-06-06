# coding: utf-8

# Based on https://github.com/blumdrew/voronoi-europe
# Actually,it's 80% plagiarism

from scipy.spatial import Voronoi
import geopandas as gpd
import pandas as pd
import os
from shapely.ops import unary_union
from shapely.geometry import Polygon, Point, MultiPolygon    
from shapely.geometry.base import BaseGeometry
import matplotlib.pyplot as plt


# The following code was made in Pelotas-RS
# Hometown of the Flying Priest (RIP)

Geometry=[]
for i in range(27):
    Geometry.append(None)

cap = pd.read_csv('capitais.csv')

# PART 1: Get each state's shape
os.chdir(os.getcwd()+'/gis')
data = gpd.read_file('ne_10m_admin_1_states_provinces.shp')
os.chdir('..')
for i in range(len(data)):
    state_data = data.loc[i]
    if state_data['iso_a2']=="BR":
        for j in range(27):
            if (state_data['postal']==cap['Estado'][j]):
                Geometry[j] = state_data['geometry']
                break
cap["Geometria"] = Geometry
# PART 2: Create Voronoi shape
voronoi_frame = gpd.GeoDataFrame()
voronoi_frame['points'] = None
voronoi_frame['geometry'] = None
capital_locations = []
for i in range(27):
    city = cap.iloc[i]
    capital_locations.append((city["Latitude"],city["Longitude"]))
#The original coder inserted those extra points for some reason
capital_locations.append((-80,170))
capital_locations.append((-80,-65))
capital_locations.append((140,170))
capital_locations.append((140,-65))
capital_locations.append((10,-65))
vor = Voronoi(capital_locations)
pts = vor.vertices
regions = vor.regions
i = 0
for part in regions:
    loop_points=[]
    for j in range(len(part)):
        skip = False
        if -1 in part:
            skip=True
        if not skip:
            loop_points.append(pts[part[j]])
    try:
        x,y = list(zip(*loop_points))
        loop_points = list(zip(y,x))
        poly = Polygon(loop_points)
        voronoi_frame.loc[i,'geometry'] = []
        voronoi_frame.loc[i,'points'] = poly
        i +=1
    except (ValueError,TypeError):
        True

# PART 3:  Make Voronoi shapes fit Brazil's shape
voronoi_frame['area'] = None
br_geoms = [cap.loc[i]['Geometria'] for i in range(len(cap))]
all_br=unary_union(br_geoms)
for i in range(len(voronoi_frame)):
    cur_shape = voronoi_frame.loc[i]['points']
    intersect = BaseGeometry.intersection(all_br.buffer(0),cur_shape.buffer(0))
    if i==0:                                    # We have to deal this way with the State of Acre
        intersect = (all_br.buffer(0))          # This state is known as nowhere land. It's the Brazilian Wyoming.
    voronoi_frame.loc[i,'geometry'] = intersect
    voronoi_frame.loc[i,'area']=intersect.area


# PART 4:  Plot the map
voronoi_frame['map color'] = [1,2,3,4,3,4,1,2,4,2,2,1,1,2,3,4,1,2,3,4,2,1,4,3,4,2,1]
capital_pts = [(cap.loc[index]['Latitude'],cap.loc[index]['Longitude']) for index in range(len(cap))]
fig, ax =plt.subplots()
plt.figure(dpi=500)
ax=plt.gca()
ax.set_aspect('equal')
ax.axis('off')
clist = list(zip(*capital_pts))
xcap=[float(val) for val in clist[1]]
ycap=[float(val) for val in clist[0]]
plt.plot(xcap,ycap,'ko',markersize=1)
voronoi_frame.plot(ax=ax,column="map color",cmap='viridis',linewidth=0.5)

plt.savefig('output.png', bbox_inches='tight')

