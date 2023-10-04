'''
Handle the drawing of the shapefile, the legend of the plot, and writing the plot
'''

from .plot_data import DataPlot 

class ScatterPlot(DataPlot):
    '''
    Scatter plot subclass of a dataplot
    '''

    def __init__(self, in_file, opts):
        super().__init__(in_file, opts)
        self.x = in_file.lat
        self.y = in_file.lon

    def draw_plot(self, data, vmin, vmax):
        '''
        Draw the plot based on the data and plot type
        '''
        self.data_plot = self.m.scatter(self.x, self.y, c=data, cmap=self.cmap, 
          vmin=vmin, vmax=vmax, latlon=True, s=data)

