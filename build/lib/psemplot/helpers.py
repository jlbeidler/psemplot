"""
Miscellaneous functions
"""

def parse_form(form):
    '''
    Convert the entered formula into one that can be mathematically evaluated using
    Python variables. Return both the formula and the pollutants found
    '''
    import re
    # Split the formula using possible mathematical symbols
    pols = re.split('\-|\+|\*|\/|\%|\(|\)|\[|\]|\^', form)
    pol_list = []
    for pol in pols:
        pol = pol.strip()
        # A proper pollutant name will have at least 3 characters
        #  and contain an underscore
        if len(pol) >= 3 and '_' in pol and pol not in pol_list:
            pol_list.append(pol)
            # Susbstitute the species names back into the formula
            # Use a negative lookbehind for A-Z so that partial names are not
            #  replaced. ie: NO could partially replace HONO
            form = re.sub('(?<![A-Z])%s' %pol, 'species[\"%s\"]' %pol, form)
    if len(pol_list) < 1:
        raise ValueError('No pollutants detected in pollutant list')
    return form, pol_list

def get_inputs(in_list, inputtype='netcdf'):
    '''
    Open the input netCDF(s)
    Check for dimensional mismatches
    '''
    from .api.inputs import load_input
    inf_dict = dict((chr(x + ord('A')), load_input(inputtype,in_list[x])) for x in range(len(in_list))) 
    if len(list(inf_dict.keys())) > 1:
        ref = inf_dict['A']
        for in_file in list(inf_dict.values()):
            if in_file.cols != ref.cols or in_file.rows != ref.rows or in_file.xcell != ref.xcell or \
                in_file.xorig != ref.xorig or in_file.yorig != ref.yorig:
                    raise ValueError('Dimensional mismatch between %s and %s' %(ref, in_file))
    return inf_dict

