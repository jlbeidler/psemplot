'''
Handle the drawing of the shapefile, the legend of the plot, and writing the plot
'''

import matplotlib
matplotlib.use('Agg')
import os
import pylab as p
import numpy as np
import numpy.ma as ma
from matplotlib.collections import LineCollection
from .colors import Colors, VLimit

class DataPlot:

    def __init__(self, in_file, opts):
        from . import projection
        self.proj = projection.GridProj(in_file)
        self.m = self.proj.proj_map
        self.x = False
        self.y = False 
        self.draw_shape(self.proj.name, opts.shape_file, opts.shape_att, opts.drawstates)
        self.set_fontsize(opts)
        self.norm = False

    def draw_shape(self, proj_name, shape_file, shape_att, draw_states):
        '''
        Read the shapefile onto the map and drop the lines
        '''
        if shape_file:
            map_shape = self.m.readshapefile(shape_file, shape_att, drawbounds=True, linewidth=0.3)           
        if not shape_file or draw_states:
            self.m.drawstates()
            self.m.drawcountries()
            self.m.drawcoastlines()

    def set_fontsize(self, opts):
        '''
        Setup the fontsizes for the legend and titles
        '''
        if opts.hi_res:
            self.params = {'legend.fontsize': 28, 'axes.titlesize': 30, 'axes.titlepad': 1}
            self.subtitle_fontsize = 22
        else:
            self.params = {'legend.fontsize': 12}
            self.subtitle_fontsize = 14

    def format_tick(self, tick, use_absolute=False):
        '''
        Autoformat the numeric label on the legend
        '''
        if use_absolute:
            f_val = abs(tick)
        else:
            f_val = abs(self.ticks[-1])
            if f_val == 0:
                f_val = abs(self.ticks[int(len(self.ticks)/2)])
        if f_val >= 100000 or f_val < 0.02:
            tick = '%.2e' %tick
        elif f_val < 100000 and f_val >= 20:
            tick = '%i' %tick
        elif f_val < 20 and f_val >= 2:
            tick = '%.1f' %tick
        elif f_val < 2 and f_val >= 0.2:
            tick = '%.2f' %tick
        elif f_val < 0.2 and f_val >= 0.02:
            tick = '%.3f' %tick
        return tick

    def calc_legend_values(self, opts):
        '''
        Develop the legend if there are uneven cutoffs
        '''
        proxy_shapes = []
        tags = []
        ticks = self.ticks[:]
        if self.neutral_lim.x > 0 and ticks[0] >= 0:
            ticks.insert(0, self.neutral_lim.x)
            if float(ticks[0]) > float(ticks[1]):
                raise ValueError('Neutral cut off value greater than specified cut off values')
        for tick_num, tick_val in enumerate(ticks):
            if tick_num > 0:
                prev_val = ticks[tick_num-1]
                tag = '%s to %s' %(self.format_tick(prev_val, True), self.format_tick(tick_val, True))
                if not opts.boundscale:
                    if tick_num == 1:
                        tag = '< %s' %self.format_tick(tick_val, True)
                    elif tick_num == len(ticks)-1:
                        tag = '> %s' %self.format_tick(ticks[tick_num-1], True)
                tags.append(tag)
        # Remap the values to the scale 
        cnums = [(ticks[n+1] - ticks[n])/2 + ticks[n] for n in range(len(ticks)-1)]
        [proxy_shapes.append(p.Rectangle((0,0),1,1,fc=self.data_plot.to_rgba(val))) for val in cnums]
        return proxy_shapes, tags

    def draw_title(self, opts):
        '''
        Add the title, optional subtitle, optional scale label
        Put in bold state lines and add scale
        '''
        matplotlib.rcParams.update(self.params)
        p.title(opts.title.replace('@S',opts.formula), fontweight='bold')
        if opts.subtitle:
            subtitle = opts.subtitle
        else:
            subtitle = 'Max: %s  Min: %s' %(round(self.raw_max, int(opts.mmround)), 
              round(self.raw_min, int(opts.mmround)))
        p.text(.1, .1, subtitle, fontsize=self.subtitle_fontsize, verticalalignment='bottom')

    def draw_legend(self, opts):
        '''
        Draw the legend
        '''
        if opts.box_legend:
            proxy_shapes, tags = self.calc_legend_values(opts)
            leg = p.legend(proxy_shapes, tags, bbox_to_anchor=(1.02,0,0,1), loc='center left') 
            leg.set_title(opts.scalelabel, prop = {'size': self.params['legend.fontsize']})
        else:
            if opts.boundscale:
                cbar = p.colorbar(self.data_plot, shrink=0.75, ticks=(self.ticks), 
                  extend='neither', spacing='uniform')
            else:
                cbar = p.colorbar(self.data_plot, shrink=.75, ticks=(self.ticks), extend='both', 
                  extendrect=True, extendfrac='auto', spacing='uniform')
            tick_labels = [self.format_tick(tick) for tick in self.ticks]
            if len(self.ticks) > 2:
                if not opts.boundscale:
                    tick_labels[0] = '<' + tick_labels[0]
                    tick_labels[-1] = '>' + tick_labels[-1]
                cbar.ax.set_yticklabels(tick_labels, fontsize=self.params['legend.fontsize'])
            cbar.set_label(opts.scalelabel, fontsize=self.params['legend.fontsize'])

    def set_neutral_color(self, ncolor):
        '''
        Sets the neutral color for the plots
        '''
        ncolor_dict = {'black': 0.0, 'white': 1.0, 'grey': 0.85}
        if ncolor in list(ncolor_dict.keys()):
            self.ncolor = ncolor_dict[ncolor]
        else:
            print('Defaulting to grey neutral color.') # C.Allen removed %ncolor from this
            self.ncolor = ncolor_dict['grey']

    def define_diff(self, vmin_lim, vmax_lim, data, no_auto):
        '''
        Define the min and max for difference data
        '''
        # Reset vmin_lim to 100% - vmax_lim if vmax_lim percent was used
        # This sets up a check to help improve the scale around 0
        if vmax_lim.per:
            iv_max = '%s%%' %(100 - vmax_lim.nper + 1e-16)  # Put in some arbitrarily small value so that 0 isn't returned
            print('NOTE: Resetting vmin_lim to %s to balance scale' %iv_max)
            vmin_lim = VLimit(iv_max, data)
        # Fix scale limits of very sparse difference data 
        if (vmin_lim.x == vmax_lim.x) and vmax_lim.per:
            print('NOTE: Very sparse data, resetting scale max to percentage of data max')
            vmax_lim.x = vmax_lim.nper/100 * vmax_lim.data_max
            print(vmax_lim.x)
        if not no_auto:
            # Check if the absolute value of the min is greater than the max
            # If it is, select the max to be the absolute value of the min
            if abs(vmin_lim.x) > vmax_lim.x and vmin_lim.x < 0 and not no_auto:
                print('NOTE: Setting vmax_lim to absolute value of vmin_lim')
                vmax_lim = VLimit(str(abs(vmin_lim.x)), data)
            else:
            # Otherwise set the min to be the negative of the max
                print('NOTE: Setting vmin_lim to negative of vmax_lim')
                vmin_lim = VLimit(str((vmax_lim.x * -1)), data)
        return (vmin_lim.x, vmax_lim.x)

    def assign_colors(self, data, opts):
        '''
        Populate the values -> colors -> FIPS for polygon filling
        '''
        self.raw_min = data.min()
        self.raw_max = data.max()
        if opts.mask_less:
            data = ma.masked_less(data, float(opts.mask_less))
        # If there is a cutoff list override any specified vmax and vmin
        if opts.cutoff_list:
            print('NOTE: Using cutoffs. Ignoring max and min specifications. Turning off autoscaling.')
            cuts = sorted([float(n) for n in opts.cutoff_list.strip().split(',')])
            opts.vmax = str(cuts[-1])
            opts.vmin = str(cuts[0])
            opts.no_auto = True 
        vmax_lim = VLimit(opts.vmax, data)
        vmin_lim = VLimit(opts.vmin, data)
        self.neutral_lim = VLimit(opts.neutral, data)
        # Check to see if this is a "negative only" plot
        if vmax_lim.x < 0:
            print('WARNING: Vmax is negative.  May result in plotting error.')
            # Deal with a scale where all data values are less than zero
            if vmin_lim.x <= 0 and not opts.no_auto:
                print('WARNING: Vmax and vmin are both negative.')
                if vmax_lim.per:
                    iv_max = '%s%%' %(100 - vmax_lim.nper)
                    print('NOTE: Resetting vmin to %s' %iv_max)
                    vmin_lim = VLimit(iv_max, data)
                else:
                    print('NOTE: Resetting vmin to %s' %(vmax_lim.x * -1))
                    vmin_lim = VLimit(str(vmax_lim.x * -1), data)
                neutral_per = '%s%%' %(100 - self.neutral_lim.nper) 
                self.neutral_lim = VLimit(neutral_per, data)
        # Setup the ticks for the legend
        colors = Colors(vmin_lim.x, vmax_lim.x, self.neutral_lim)
        # Is it difference data?
        if (((np.amin(data) < 0 and np.amax(data) > 0) and (vmin_lim.x < 0 and vmax_lim.x >= 0)) or \
            opts.force_diff):
            # Set up a difference color map when the absolute max and min sit on opposite sides of 0
            print('NOTE: Difference data detected')
            vmin_lim.x, vmax_lim.x = self.define_diff(vmin_lim, vmax_lim, data, opts.no_auto)
            colors.vmin, colors.vmax = (vmin_lim.x, vmax_lim.x)
            if not opts.ncolor:
                self.ncolor = 0.82
            self.cmap, self.ticks = colors.diff_cmap(self.ncolor, opts)
        else:
            # Use standard map
            print('NOTE: Standard plot data detected')
            self.cmap, self.ticks = colors.data_cmap(self.ncolor, opts)
        if opts.repmax:
            self.report_scale_max(opts.repmax, vmax_lim.x)
        data = self.set_data_bounds(data, vmin_lim.x, vmax_lim.x, opts)
        # Normalize the colormap for a cutoff list
        if opts.cutoff_list:
            self.norm =  matplotlib.colors.BoundaryNorm(boundaries=self.ticks, ncolors=len(self.ticks)+1, extend='both')
        # Draw the colormesh
        self.draw_plot(data, vmin_lim.x, vmax_lim.x)

    def set_data_bounds(self, data, vmin, vmax, opts):
        '''
        Cap or mask the data based on command line options
        '''
        # Mask values above and below the max/min if bounded
        if opts.boundscale:
            data = ma.masked_less(data, vmin)
            data = ma.masked_greater(data, vmax)
        # For an unbounded scale set the data above and below the limits to the limits
        else:
            data[data < vmin] = vmin
            data[data > vmax] = vmax
        return data

    def report_scale_max(self, repmax, vmax):
        '''
        Write the scale max to a file for use in subsequent plots
        '''
        print('NOTE: Scale maximum set to %s' %vmax)
        with open(repmax, 'w') as f:
            f.write(str(vmax))

    def write_plot(self, out_file, hi_res):
        '''
        Write the PNG, or PDF if the file name ends in PDF and it is hi-res
        '''
        fig = p.gcf()
        fmt = 'png'
        if hi_res:
            fig.set_size_inches(32,20)
            dpi = 200
            if out_file.endswith('pdf'):
                fmt = 'pdf'
        else:
            fig.set_size_inches(16,10)
            dpi = 100
        print('Writing to %s' %out_file)
        fig.savefig(out_file, dpi=dpi, bbox_inches='tight', format=fmt)

    def get_fig(self):
        return p.gcf()

    def disp_plot(self):
        '''
        Display the plot as an X window
        '''
        p.show()


