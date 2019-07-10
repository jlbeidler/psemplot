"""
Setup the grid projection from the input file metadata
Currently supports I/O API grid types 2 (LCC) and 6 (Polar Stereographic)
Easily extensible to other types as needed
"""

from builtins import object
from pyproj import Proj
from mpl_toolkits.basemap import Basemap

class GridProj(object):
    def __init__(self, data_obj):
        if data_obj.gdtyp == 2:
            self.lcc(data_obj)
            self.name = 'lcc'
        elif data_obj.gdtyp == 6:
            self.polar(data_obj)
            self.name = 'polar'

    def lcc(self, data_obj):
        self.proj_trans = Proj(proj='lcc', lat_1=data_obj.palp, lat_2=data_obj.pbet, lon_0=data_obj.xcent, lat_0=data_obj.ycent, a=6370000.0, b=6370000.0)
        lonO, latO = self.proj_trans(data_obj.xorig, data_obj.yorig, inverse=True)
        lonE, latE = self.proj_trans((data_obj.xorig + (data_obj.xcell * data_obj.cols)), 
            (data_obj.yorig + (data_obj.ycell * data_obj.rows)), inverse=True)
        # Lambert Conformal map of lower 48 states.
        self.proj_map = Basemap(projection='lcc', lat_1=data_obj.palp, lat_2=data_obj.pbet, lon_0=data_obj.xcent, 
            lat_0=data_obj.ycent, llcrnrlat=latO, llcrnrlon=lonO, urcrnrlat=latE, urcrnrlon=lonE, rsphere=(6370000.0, 6370000.0))

    def polar(self, data_obj):
        self.proj_map = Basemap(projection='stere', lat_0=data_obj.ycent, lon_0=data_obj.xcent, 
            width=(data_obj.xcell * data_obj.cols), height=(data_obj.ycell * data_obj.rows), 
            lat_ts=data_obj.pbet) 

