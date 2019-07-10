'''
Handle the drawing of the shapefile, the legend of the plot, and writing the plot
'''

import matplotlib
matplotlib.use('Agg')
import pylab as p
import numpy as np
import numpy.ma as ma
from matplotlib.collections import LineCollection
from .colors import diff_cmap, data_cmap, VLimit

class GridPlot(object):

    def __init__(self, in_file, shape_file, shape_att):
        from . import projection
        self.proj = projection.GridProj(in_file)
        self.m = self.proj.proj_map
        self.cols = np.array([in_file.xcell * (col + 0.5) for col in range(in_file.cols)])
        self.rows = np.array([in_file.ycell * row for row in range(in_file.rows)])
        self.draw_shape(self.proj.name, shape_file, shape_att)
        self.colors = {}

    def draw_shape(self, proj_name, shape_file, shape_att):
        '''
        Read the shapefile onto the map and drop the lines
        '''
        if shape_file:
            map_shape = self.m.readshapefile(shape_file, shape_att, drawbounds=True, linewidth=0.3)           
        else:
            self.m.drawcountries()
            self.m.drawcoastlines()

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

    def calc_legend_values(self, mask_less):
        '''
        Develop the legend if there are uneven cutoffs
        '''
        proxy_shapes = []
        tags = []
        ticks = self.ticks[:]
        if self.neutral_lim.x > 0:
            ticks.insert(0, self.neutral_lim.x)
            if float(ticks[0]) > float(ticks[1]):
                raise ValueError('Neutral cut off value greater than specified cut off values')
        if mask_less:
            ticks.insert(0, float(mask_less))
        for tick_num, tick_val in enumerate(ticks):
            if tick_num == 0:
                if mask_less:
                    color_val = 'white'
                else:
                    color_val = self.data_plot.to_rgba(tick_val/2.)
                tag = '%s to %s' %(0, self.format_tick(tick_val, True))
            else:
                prev_val = ticks[tick_num-1]
                color_val = self.data_plot.to_rgba(prev_val + (tick_val-prev_val)/2)
                tag = '%s to %s' %(self.format_tick(prev_val, True), self.format_tick(tick_val, True))
            proxy_shapes.append(p.Rectangle((0,0),1,1,fc=color_val))
            tags.append(tag)
            # Append the trailing label
            if tick_num == len(ticks)-1:
                tag = '%s +' %self.format_tick(tick_val, True)
                proxy_shapes.append(p.Rectangle((0,0),1,1,fc=self.data_plot.to_rgba(tick_val*1.1)))
                tags.append(tag)
        return proxy_shapes, tags

    def title_plot(self, options):
        """
        Add the title, optional subtitle, optional scale label
        Put in bold state lines and add scale
        """
        # Increase the font size in hi-res output
        if options.hi_res:
            params = {'legend.fontsize': 18, 'axes.titlesize': 30, 'axes.titlepad': 1}
        else:
             params = {'legend.fontsize': 12}
        matplotlib.rcParams.update(params)
        p.title(options.title.replace('@S',options.formula), fontweight='bold')
        if options.subtitle:
            subtitle = options.subtitle
        else:
            subtitle = 'Max: {:.4}  Min: {:.4}'.format(self.raw_max, self.raw_min) 
        p.text(.1, .1, subtitle, fontsize=14, verticalalignment='bottom')
        if options.cutoff_list:
            proxy_shapes, tags = self.calc_legend_values(options.mask_less)
            leg = p.legend(proxy_shapes, tags, bbox_to_anchor=(1.02,0,0,1), loc='center left') 
            leg.set_title(options.scalelabel, prop = {'size': params['legend.fontsize']})
        else:
            cbar = p.colorbar(self.data_plot, shrink=.75, ticks=(self.ticks))
            tick_labels = [self.format_tick(tick) for tick in self.ticks]
            if len(self.ticks) > 2:
                tick_labels[0] = '<' + tick_labels[0]
                tick_labels[-1] = '>' + tick_labels[-1]
                cbar.ax.set_yticklabels(tick_labels, fontsize=params['legend.fontsize'])
            cbar.set_label(options.scalelabel, fontsize=params['legend.fontsize'])

    def set_neutral_color(self, ncolor):
        '''
        Sets the neutral color for the plots
        '''
        ncolor_dict = {'black': 0.0, 'white': 1.0, 'grey': 0.85}
        if ncolor in list(ncolor_dict.keys()):
            self.ncolor = ncolor_dict[ncolor]
        else:
            print('Neutral color %s not found.\nDefaulting to neutral color.' %ncolor)
            self.ncolor = ncolor_dict['grey']

    def assign_colors(self, data, options):
        """
        Populate the values -> colors -> FIPS for polygon filling
        """
        self.raw_min = data.min()
        self.raw_max = data.max()
        if options.mask_less:
            data = ma.masked_less(data, float(options.mask_less))
        vmax_lim = VLimit(options.vmax, data)
        vmin_lim = VLimit(options.vmin, data)
        self.neutral_lim = VLimit(options.neutral, data)
        if vmax_lim.x < 0:
            print('WARNING: Vmax is negative.  May result in plotting error.')
            # Deal with a scale where all data values are less than zero
            if vmin_lim.x <= 0 and not options.no_auto:
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
        self.ticks = []
        if (((np.amin(data) < 0 and np.amax(data) > 0) and (vmin_lim.x < 0 and vmax_lim.x > 0)) or \
            options.force_diff):
            # Set up a difference color map when the absolute max and min sit on opposite
            # sides of zero
            print('NOTE: Difference data detected')
            # Reset vmin_lim to 100% - vmax_lim if vmax_lim percent was used
            # This sets up a check to help improve the scale around 0
            if vmax_lim.per:
                iv_max = '%s%%' %(100 - vmax_lim.nper + 1e-16)  # Put in some arbitrarily small value so that 0 isn't returned
                print('NOTE: Resetting vmin_lim to %s to balance scale' %iv_max)
                vmin_lim = VLimit(iv_max, data)
            if not options.no_auto:
                # Check if the absolute value of the min is greater than the max
                # If it is, select the max to be the absolute value of the min
                if abs(vmin_lim.x) > vmax_lim.x and vmin_lim.x < 0 and not options.no_auto:
                    print('NOTE: Setting vmax_lim to absolute value of vmin_lim')
                    vmax_lim = VLimit(str(abs(vmin_lim.x)), data)
                else:
                # Otherwise set the min to be the negative of the max
                    print('NOTE: Setting vmin_lim to negative of vmax_lim')
                    vmin_lim = VLimit(str((vmax_lim.x * -1)), data)
            self.cmap, self.ticks = diff_cmap(vmin_lim.x, vmax_lim.x, self.ncolor, self.neutral_lim, options)
        else:
            # Use standard map
            print('NOTE: Standard plot data detected')
            self.cmap, self.ticks = data_cmap(vmin_lim.x, vmax_lim.x, self.ncolor, self.neutral_lim, options)
        self.data_plot = self.m.pcolormesh(self.cols, self.rows, data, cmap=self.cmap, vmin=vmin_lim.x, vmax=vmax_lim.x)

    def write_plot(self, out_file, hi_res):
        """
        Write the PNG, or PDF if the file name ends in PDF and it is hi-res
        """
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
        """
        Display the plot as an X window
        """
        p.show()

