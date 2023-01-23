import numpy as np
import pandas as pd

class PsempData:
    """
    Instance of an input file.
    """
    def __init__(self, infile_name):
        self.src = self.read_emis(infile_name)
        self.objtype = 'latlon'
        self.filename = infile_name
        self.set_lat_lons()

    def __str__(self):
        return self.filename

    def set_lat_lons(self):
        '''
        Set the latitude and longitude arrays
        '''
        self.lat = self.src['latitude'].astype(float).values
        self.lon = self.src['longitude'].astype(float).values

    def read_emis(self, fn):
        '''
        Read in an emis file with latitude, longitude, poll, value
        File must have a header containing:
        #ATTS gdtyp:1,palp:39,pbet:90,pgam:-32,xcent:-30,ycent:40
        And contain the columns:
        latitude, longitude, poll, value
        '''
        with open(fn) as f:
            # Initialize atts with dummy values that aren't required for this type
            attrs = {'cols': 1, 'rows': 1, 'tstep': 1, 'sdate': 1, 'xcell': 1, 'ycell': 1, 
              'xorig': 1, 'yorig': 1}
            for l in f:
                if l.startswith('#'):
                    if l[1:5].upper() == 'ATTS':
                        proj = l[5:].strip().split(',')
                else:
                    break
        for x in proj:
            attrs[x.split(':')[0].strip().lower()] = float(x.split(':')[1].strip())
        for att, val in attrs.items():
            setattr(self, att, val)       
        usecols = ['latitude','longitude','poll','value']
        df = pd.read_csv(fn, usecols=usecols, dtype={'poll': str}, comment='#')
        for col in ['latitude','longitude']:
            df[col] = df[col].round(6).astype(str)
        df = df.groupby(['latitude','longitude','poll'], as_index=False).sum()
        df = pd.pivot_table(df, values='value', index=['latitude','longitude'], columns='poll',
          aggfunc='sum', fill_value=0).reset_index()
        setattr(self, 'rows', len(df))
        return df
    
    def var(self, var_name):
        if var_name in list(self.src.columns):
            arr = self.src[var_name].values
        else:
            raise ValueError('The variable %s does not exist in the file %s.' %(var_name, self.filename))
        return np.reshape(arr, [1,1,self.rows,1])

    def close(self):
        pass

