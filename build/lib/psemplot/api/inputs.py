"""
module loader for custom input types

A custom input type can be created as long as it maps

"""


import os.path
import importlib as il


def load_input(module_name, infile_name):
    '''
    Validate an input module and load the file
    '''
    mod = il.import_module('.%s' %module_name, 'psemplot.inputs')
    
    # Initialize the PsempData object
    try:
        data_obj = mod.PsempData(infile_name)
    except AttributeError:
        raise AttributeError('PsempData class missing in input module %s' %module_name)
    # Check that the required attributes exist
    req_attr = ('sdate','tstep','palp','pbet','xcent','ycent','xorig','yorig','var','close')
    for o_attr in req_attr:
        if not hasattr(data_obj, o_attr):
            raise AttributeError('Attribute %s not defined in module %s' %(o_attr, module_name))
    dt_attr = {'sdate': int, 'tstep': int, 'xorig': float, 'yorig': float, 'palp': float, 'pbet': float,
            'xcent': float, 'ycent': float, 'cols': int, 'rows': int, 'xcell': int, 'ycell': int}
    # Validate parameter types
    for att, chk in dt_attr.items():
        val = getattr(data_obj, att)
        if val is None:
            raise AttributeError('Attribute %s undefined' %att)
        else:
            chk(val)
    return data_obj    
