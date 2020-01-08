"""
Determine the colors and mappings for the data and legend
"""

import pylab as p
import matplotlib.colors as mpcol 
import numpy as np

# Compatability with 1.5 matplotlib colormaps
# Viridis_r is popular
from . import colormaps as cmaps
p.register_cmap(name='viridis_r', cmap=cmaps.viridis_r)
p.register_cmap(name='magma_r', cmap=cmaps.magma_r)
p.register_cmap(name='plasma_r', cmap=cmaps.plasma_r)

# Custom color mappings
diff_dict = {
'blue': [(0.0, 0.58203125, 0.58203125), (0.125, 0.703125, 0.703125), (0.25, 0.81640625, 0.81640625), (0.375, 0.91015625, 0.91015625), (0.4999, 0.96875, 0.96875), (0.5, 1.0, 1.0), (0.5001, 0.5625, 0.5625), (0.625, 0.37890625, 0.37890625), (0.75, 0.26171875, 0.26171875), (0.875, 0.15234375, 0.15234375), (1.0, 0.1484375, 0.1484375)], 
'green': [(0.0, 0.2109375, 0.2109375), (0.125, 0.45703125, 0.45703125), (0.25, 0.67578125, 0.67578125), (0.375, 0.84765625, 0.84765625), (0.4999, 0.94921875, 0.94921875), (0.5, 1.0, 1.0), (0.5001, 0.875, 0.875), (0.625, 0.6796875, 0.6796875), (0.75, 0.42578125, 0.42578125), (0.875, 0.1875, 0.1875), (1.0, 0.0, 0.0)], 
'red': [(0.0, 0.19140625, 0.19140625), (0.125, 0.26953125, 0.26953125), (0.25, 0.453125, 0.453125), (0.375, 0.66796875, 0.66796875), (0.4999, 0.875, 0.875), (0.5, 1.0, 1.0), (0.5001, 0.9921875, 0.9921875), (0.625, 0.98828125, 0.98828125), (0.75, 0.953125, 0.953125), (0.875, 0.83984375, 0.83984375), (1.0, 0.64453125, 0.64453125)]}
rb_diff_cmap = mpcol.LinearSegmentedColormap('mod_diff', diff_dict)
# Custom color mappings
cool_dict = {'blue': [(0.0, 0.0916, 0.0916), (0.365, 1.0, 1.0), (1.0, 1.0, 1.0)], 
  'green': [(0.0, 0.0, 0.0), (0.365, 0.0, 0.0), (1.0, 1.0, 1.0)], 
  'red': [(0.0, 0.0, 0.0), (0.746, 0.0, 0.0), (1.0, 0.0, 0.0)]}
cool_cmap = mpcol.LinearSegmentedColormap('mod_cool', cool_dict)

class VLimit(object):
    """
    Calculate data plot limits
    """
    def __init__(self, x, data):
        self.per = ''
        self.get_lim(x, data)
        self.data_min = data.min()
        self.data_max = data.max()

    def __call__(self):
        return self.x

    def __str__(self):
        return str(self.x)

    def get_lim(self, x, data):
        """
        Return a numerical value based on a numerical limit
        or on a percentile 
        """
        if '%' in x:
            self.per = x
            # Calculate the percentile value
            self.nper = float(x.split('%')[0])
            if self.nper > 0:
                x = np.percentile(data, self.nper)
            else:
                x = 0
        try:
            vx = float(x)
        except TypeError:
            raise TypeError('Invalid limit.  Check vmax and vmin values.')
        self.x = vx    

def calc_bins(bins):
    '''
    Use the command line argument of bins or default to a whole bunch (256)
    '''
    if not bins or int(bins) < 3:
        bins = 256
    else:
        bins = int(bins)
    return bins

def calc_tick_total(bins, num_ticks):
    '''
    Calculate the number of ticks on the legend based on the number of bins
    '''
    if num_ticks:
        tick_total = int(num_ticks) + 1
    elif int(bins) > 2 and int(bins) < 100:
        tick_total = bins + 1
    else:
        tick_total = 6
    return tick_total

def calc_ticks(tick_total, vmax, vmin, boundscale):
    '''
    Locate the ticks
    '''
    ticks = []
    for x in range(tick_total):
        if x not in (0, tick_total - 1):
            tick = ((float(x)/float(tick_total-1)) * (vmax-vmin)) + vmin
            if round(tick, 8) == 0:
                tick = 0
            ticks.append(tick)
        # Keep the high and low ticks for bounded scales
        elif boundscale:
            if x == 0:
                ticks.append(vmin)
            elif x == tick_total - 1:
                ticks.append(vmax)
    # Insert a 0 for difference plots
    if vmin < 0 and vmax > 0 and 0 not in ticks:
            ticks.append(0)
    ticks.sort()
    return ticks

def calc_scale_frac(neutral_lim, vmin, vmax, scale_center=0):
    '''
    Calculate fraction of the scale +/- from zero to use
    Percentages will use +% from 0 and -% from zero
    Raw numbers will be +number from 0 and -number from zero
    '''
    if neutral_lim.per:
        scale_frac = float(neutral_lim.nper/100.)
    else:
        scale_frac = ((neutral_lim.x - vmin)/(vmax - vmin)) - scale_center
    return scale_frac

def parse_cutoffs(cutoff_list):
    '''
    Parse the optional cutoff list into a sorted list of values
    '''
    cutoffs = []
    for val in cutoff_list.split(','):
        try:
            val = float(val.strip())
        except TypeError:
            raise TypeError('Invalid cutoff value in cutoff list.')
        cutoffs.append(val)
    cutoffs.sort()
#    if cutoffs[0] <= 0:
#        raise ValueError('Lowest cutoff value must be greater than zero.')
    return cutoffs

def data_cmap(vmin, vmax, ncolor, neutral_lim, options):
    """
    Generate a gradated colormap or continous, depending on bins specified
    Continuous really 256 colors gradated, but with ability to extend neutral.
    The neutral cut off is not used for gradated color maps.  Grey is either the first bin
        or neutral is turned off entirely.
    """
    scale_frac = calc_scale_frac(neutral_lim, vmin, vmax)
    colors = []
    # Set cool maps with neutral cut off
    if vmin < 0 and vmax <= 0:
        cmap = cool_cmap
        lowx = scale_frac
        highx = 1
    # Set hot maps with neutral cut off
    else:
        if options.cmap:
            if ',' in options.cmap:
                # Create a colormap from a list of colors
                color_list = options.cmap.split(',')
                colors = [(x/(len(color_list) - 1), color.lower()) for x, color in enumerate(color_list)]
                cmap = mpcol.LinearSegmentedColormap.from_list('', colors)
            else:
                cmap = p.get_cmap(options.cmap)
        else:
            cmap = p.cm.summer_r
        lowx = 0
        highx = scale_frac
    # Setup the ticks and bins
    if options.cutoff_list:
        cutoff_list = parse_cutoffs(options.cutoff_list)
        ticks = cutoff_list
        cmap = uneven_colormap(cmap, cutoff_list)
    else:
        bins = calc_bins(options.bins)
        tick_total = calc_tick_total(bins, options.ticks)
        ticks = calc_ticks(tick_total, vmax, vmin, options.boundscale)
        # Do some scaling and insert neutral if colors were not specific
        if not colors:
            cmap = bin_colormap(cmap, bins)
            # Insert neutral at the position closest to zero
            if scale_frac > 0:
                in_cdict = cmap._segmentdata
                cdict = {'red': [], 'green': [], 'blue': []}
                for cnum,color in enumerate(('red','green','blue')):
                    # Remove color entries between the center neutral cutoff
                    cdict[color] = [cbin for cbin in in_cdict[color] if cbin[0] > highx or cbin[0] < lowx]
                    # Add the boundaries of the neutral center
                    cdict[color].append((lowx, cmap(lowx)[cnum], ncolor))
                    cdict[color].append((highx, ncolor, cmap(highx)[cnum]))
                    cdict[color].sort()
            if options.nfill and not options.cutoff_list:
                cmap = mpcol.LinearSegmentedColormap('neutral_jet_disc', cdict, N=bins)
            else:
                cmap = mpcol.LinearSegmentedColormap('neutral_jet_disc', cdict, N=100000)
    return (cmap, ticks)

def bin_colormap(cmap, bins):
    '''
    Descretize the colormap based on the number of bins
    '''
    cuts = bins + 1
    cdict = {'red': [], 'green': [], 'blue': []}
    for cut_num in range(cuts):
        x = (1./float(bins)) * float(cut_num)
        if x > 1:
            x = 1.
        for cnum, color in enumerate(('red','green','blue')):
            if cut_num == 0:
                try:
                    ya = cmap(0)[cnum]
                except TypeError:
                    raise ValueError('CMAP %s not found' %scale_cmap)
                yb = cmap(x)[cnum]
            else:
                ya = cdict[color][cut_num - 1][2]
                yb = cmap((1./float(bins - 1)) * float(cut_num))[cnum]
            cdict[color].append((x, ya, yb))
    return mpcol.LinearSegmentedColormap('neutral_jet_disc', cdict, bins)

def uneven_colormap(cmap, cutoff_list):
    '''
    Descretize the colormap based on a list
    '''
    cdict = {'red': [], 'green': [], 'blue': []}
    # To accomodate negative values add the smallest value to each number and then calculate cut list
    min_val = abs(sorted(cutoff_list)[0])
    max_val = abs(sorted(cutoff_list)[-1])
    x_cutlist = [((cut_value + min_val)/(max_val + min_val)) for cut_value in cutoff_list]
    # Add a leading 0 and 1 if needed
    if x_cutlist[0] != 0:
        x_cutlist = [0,] + x_cutlist
    if x_cutlist[-1] != 1:
        x_cutlist.append(1)
    cmap_colors = [cmap((2*n + 1)/((len(x_cutlist) - 1)*2)) for n in range(len(x_cutlist) - 1)]
    # Assign the colors for each bin
    for cut_num, x in enumerate(x_cutlist):
        for cnum, color in enumerate(('red','green','blue')):
            if cut_num == 0:
                ya = cmap_colors[cut_num][cnum]
            else:
                ya = cmap_colors[cut_num - 1][cnum]
            if cut_num == len(x_cutlist) - 1:
                ya = cmap_colors[cut_num - 1][cnum]
            else:
                yb = cmap_colors[cut_num][cnum]
            cdict[color].append((x, ya, yb))
    return mpcol.LinearSegmentedColormap('neutral_jet_disc', cdict)
    
def diff_cmap(vmin, vmax, ncolor, neutral_lim, options):
    """
    Generate a gradated colormap or continous, depending on bins specified
    Continuous really 256 colors gradated, but with ability to extend neutral.
    The neutral cut off is not used for gradated color maps.  Grey is either the first bin
        or neutral is turned off entirely.
    """
    colors = []
    # Setup color map
    if options.cmap:
        if ',' in options.cmap:
            # Create a colormap from a list of colors
            color_list = options.cmap.split(',')
            colors = [(x/(len(color_list) - 1), color.lower()) for x, color in enumerate(color_list)]
            cmap = mpcol.LinearSegmentedColormap.from_list('', colors)
        else:
            cmap = p.get_cmap(options.cmap)
    else:
        cmap = rb_diff_cmap
    # Setup the ticks and bins
    if options.cutoff_list:
        cutoff_list = parse_cutoffs(options.cutoff_list)
        ticks = cutoff_list
        cmap = uneven_colormap(cmap, cutoff_list)
    else:
        bins = calc_bins(options.bins)
        tick_total = calc_tick_total(bins, options.ticks)
        ticks = calc_ticks(tick_total, vmax, vmin, options.boundscale)
        # Do some scaling and insert neutral if colors were not specific
        if not colors: 
            cmap = bin_colormap(cmap, bins)
            # Insert neutral around the mid point using the new colormap
            in_cdict = cmap._segmentdata
            cdict = {'red': [], 'green': [], 'blue': []}
            if options.no_auto:
                scale_center = abs((0-vmin)/(vmax-vmin))
            else:
                scale_center = 0.5
            scale_frac = calc_scale_frac(neutral_lim, vmin, vmax, scale_center)
            lowx = scale_center - scale_frac
            highx = scale_center + scale_frac
            if lowx < 0 or highx > 1:
                raise ValueError('Neutral value outside scale of plot')
            for cnum, color in enumerate(('red','green','blue')):
                # Remove color entries between the center neutral cutoff
                cdict[color] = [cbin for cbin in in_cdict[color] if cbin[0] > highx or cbin[0] < lowx]
                # Add the boundaries of the neutral center
                # Select a multi-grade color for difference if the ncolor is 0.82
                if ncolor == 0.82:
                    low_neutral = 0.82
                    high_neutral = 0.88
                else:
                    low_neutral = ncolor
                    high_neutral = ncolor
                cdict[color].append((lowx, cmap(lowx)[cnum], low_neutral))
                cdict[color].append((scale_center, low_neutral, high_neutral))
                cdict[color].append((highx, high_neutral, cmap(highx)[cnum]))
                cdict[color].sort()
            if options.nfill:
                cmap = mpcol.LinearSegmentedColormap('neutral_jet_disc', cdict, N=bins)
            else:
                cmap = mpcol.LinearSegmentedColormap('neutral_jet_disc', cdict)
    return(cmap, ticks)

