import netCDF4 as ncf

class PsempData:
    """
    Instance of an input file.
    """
    def __init__(self, infile_name):
        self.src = ncf.Dataset(infile_name)
        self.filename = infile_name
        self.get_attr()

    def __str__(self):
        return self.filename

    def var(self, var_name):
        if var_name in list(self.src.variables.keys()):
            arr = self.src.variables[var_name]
        else:
            raise ValueError('The variable %s does not exist in the file %s.' %(var_name, self.filename))
        return arr[:]

    def close(self):
        self.src.close()

    def get_attr(self):
        '''
        set the psempdata API attributes to the I/O API attribute values
        '''
        attr_dict = {'cols': 'NCOLS', 'rows': 'NROWS', 'palp': 'P_ALP', 'pbet': 'P_BET', 'xcent': 'XCENT',
                'ycent': 'YCENT', 'xorig': 'XORIG', 'yorig': 'YORIG', 'xcell': 'XCELL', 
                'ycell': 'YCELL', 'sdate': 'SDATE', 'tstep': 'TSTEP', 'gdtyp': 'GDTYP', 'pgam': 'P_GAM'}
        for out_attr, in_attr in attr_dict.items():
            try:
                val = getattr(self.src, in_attr)
            except AttributeError:
                raise AttributeError('Attribute %s not found in %s' %(in_attr, self.filename))
            else:
                setattr(self, out_attr, val)

