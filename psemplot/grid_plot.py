'''
Handle the drawing of the shapefile, the legend of the plot, and writing the plot
'''

import numpy as np
from .plot_data import DataPlot

class GridPlot(DataPlot):
    '''
    Gridded plot subclass of a dataplot
    '''

    def __init__(self, in_file, opts):
        super().__init__(in_file, opts)
        self.x = np.array([in_file.xcell * (col + 0.5) for col in range(in_file.cols)])
        self.y = np.array([in_file.ycell * row for row in range(in_file.rows)])

    def draw_plot(self, data, vmin, vmax):
        '''
        Draw the plot based on the data and plot type
        '''
        self.data_plot = self.m.pcolormesh(self.x, self.y, data, cmap=self.cmap, vmin=vmin, vmax=vmax)

