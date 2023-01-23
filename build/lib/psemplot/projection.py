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
        else:
            raise ValueError('Invalid gdtype')

    def lcc(self, data_obj):
        self.proj_trans = Proj(proj='lcc', lat_1=data_obj.palp, lat_2=data_obj.pbet, 
          lon_0=data_obj.xcent, lat_0=data_obj.ycent, a=6370000.0, b=6370000.0)
        if data_obj.objtype == 'latlon':
            extents = (min(data_obj.lon), max(data_obj.lon), min(data_obj.lat), max(data_obj.lat))
            # Get four corners plus center points along the edges
            extent_ll = {'ll': (extents[0], extents[2]), 'ur': (extents[1], extents[3]),
              'ul': (extents[0], extents[3]), 'lr': (extents[1], extents[2]),
              'cl': (extents[0], extents[2] + ((extents[3] - extents[2])/2)),
              'cr': (extents[1], extents[2] + ((extents[3] - extents[2])/2)),
              'lc': (extents[0] + ((extents[1] - extents[0])/2), extents[2]),
              'uc': (extents[0] + ((extents[1] - extents[0])/2), extents[3])}
            # Find the bounds with projected coordinates
            extent_proj = {k: self.proj_trans(*extent_ll[k]) for k in extent_ll.keys()}
            xO = min([pt[0] for pt in extent_proj.values()])
            xE = max([pt[0] for pt in extent_proj.values()])
            yO = min([pt[1] for pt in extent_proj.values()])
            yE = max([pt[1] for pt in extent_proj.values()])
        else:
            xO, yO = (data_obj.xorig, data_obj.yorig)
            xE, yE = ((data_obj.xorig + (data_obj.xcell * data_obj.cols)),
              (data_obj.yorig + (data_obj.ycell * data_obj.rows)))
        self.proj_map = Basemap(projection='lcc', lat_1=data_obj.palp, lat_2=data_obj.pbet, lon_0=data_obj.xcent, 
            lat_0=data_obj.ycent, llcrnrx=xO, llcrnry=yO, urcrnrx=xE, urcrnry=yE, rsphere=(6370000.0, 6370000.0),
            resolution='h')
        '''
            lonO, latO = self.proj_trans(data_obj.xorig, data_obj.yorig, inverse=True)
            lonE, latE = self.proj_trans((data_obj.xorig + (data_obj.xcell * data_obj.cols)), 
                (data_obj.yorig + (data_obj.ycell * data_obj.rows)), inverse=True)
        # Lambert Conformal map of lower 48 states.
        self.proj_map = Basemap(projection='lcc', lat_1=data_obj.palp, lat_2=data_obj.pbet, lon_0=data_obj.xcent, 
            lat_0=data_obj.ycent, llcrnrlat=latO, llcrnrlon=lonO, urcrnrlat=latE, urcrnrlon=lonE, rsphere=(6370000.0, 6370000.0))
        '''

    def polar(self, data_obj):
        self.proj_map = Basemap(projection='stere', lat_0=data_obj.ycent, lon_0=data_obj.xcent, 
            width=(data_obj.xcell * data_obj.cols), height=(data_obj.ycell * data_obj.rows), 
            lat_ts=data_obj.pbet) 

