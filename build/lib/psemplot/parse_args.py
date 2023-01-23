"""
Process the command line arguments and switches
"""

from optparse import OptionParser, OptionGroup

def parse_args():
    parser = OptionParser(usage = 'usage: %prog INFILE OUTFILE [opts]')
    data_group = OptionGroup(parser, 'Data Selection Options')
    scale_group = OptionGroup(parser, 'Scale Definition Options')
    draw_group = OptionGroup(parser, 'Plotting Options')
    data_group.add_option('-f', '--formula', dest='formula', help='Formula to plot. Specify a species and an input file in the format [SPECIES]_[A...Z] where the A-Z corresponds to the infile order.\
                Single file: VOC_A   Difference plot: CO_A-CO_B   % Diff: (CO_B-CO_A)/(CO_A)', default='')
    data_group.add_option('-s', '--timestep', dest='time_step', help='Timestep to select from file. Default is 0.', default=0)
    draw_group.add_option('-t', '--title', dest='title', help='Top title.  Use @S as speciesname variable in title', default='@S')
    draw_group.add_option('-u', '--sub-title', dest='subtitle', help='Subtitle. Defaults to display max and min values', default='')
    draw_group.add_option('--scale-label', dest='scalelabel', help='Label for scale.  Defaults to tons/year.', default='tons/year')
    scale_group.add_option('-b', dest='bins', help='Turn on gradated plot and set number of color bins.  Number must be greater than 2.', default=False)
    draw_group.add_option('--ticks', dest='ticks', help='Set the number of ticks to display', default=False)
    scale_group.add_option('--vmin', dest='vmin', help='Scale minimum cutoff.  Add "%" to the end to use percentile.', default='0')
    scale_group.add_option('--vmax', dest='vmax', help='Scale maximum cutoff.  Add "%" to the end to use percentile. Defaults to 95th percentile.', default='95%')
    scale_group.add_option('-g', dest='neutral', help='Use neutral color for values within x of 0 (or closest limit to 0).  Defaults to 0.01%.  Use single number 0-100%. 0% Disables neutral.', default='0.01%')
    scale_group.add_option('--cutoffs', dest='cutoff_list', help='Optional list of scale cutoffs to create uneven bins. Currently only works with data values zero or higher.', default='')
    scale_group.add_option('--neutral-labels', dest='neutral_labels', help='Label the edgees of the neutral area', default=False, action='store_true')
    draw_group.add_option('--neutral-color', dest='ncolor', help='Set neutral color to white, grey, or black', default='')
    scale_group.add_option('--neutral-fill', dest='nfill', help='Fill color bins on scale with neutral color rather than overlap', default=False, action='store_true')
    draw_group.add_option('--shape-file', dest='shape_file', help='Path to custom shapefile', default='')
    draw_group.add_option('--shape-att', dest='shape_att', help='Shapefile attribute to plot', default='')
    draw_group.add_option('--cmap', dest='cmap', help='Matplotlib colormap', default=None)
    data_group.add_option('--mask_less', dest='mask_less', help='Mask values lower than the specified value from the plot', default=None)
    scale_group.add_option('--force-diff', dest='force_diff', action='store_true', help='Force a difference colormap even if data has consistent signs', default=False)
    draw_group.add_option('--hi-res', dest='hi_res', action='store_true', help='Output a high resolution plot', default=False)
    scale_group.add_option('--no-autoscale', dest='no_auto', action='store_true', help='Turn off the autoscaling and use exactly what is entered for max and min', default=False)
    scale_group.add_option('--report-max', dest='repmax', help='Report the scale maximum used to a file', default='')
    draw_group.add_option('--minmax-round', dest='mmround', help='Digits past the decimal to round for min-max', default='4')
    data_group.add_option('--bound-scale', dest='boundscale', help='Bound the scale to the specified maximum and minimum and do not include data outside of the bounds', default=False, action='store_true')
    draw_group.add_option('--draw-states', dest='drawstates', help='Draw the state boundaries with thicker lines', action='store_true', default=False)
    draw_group.add_option('-p', dest='plottype', help='Plot type. Currently either gridded or scatter. Defaults to gridded.', default='gridded')
    data_group.add_option('-i', dest='inputtype', help='Input file type. Currently either netcdf or latlon. Defaults to netcdf.', default='netcdf')
    parser.add_option_group(data_group)
    parser.add_option_group(scale_group)
    parser.add_option_group(draw_group)
    (opts, args) = parser.parse_args()
    if len(args) >= 2:
        if len(opts.formula) < 3:
            parser.error('-f Must specify a formula.')
        try:
            int(opts.bins)
        except ValueError:
            parser.error('-b Number of bins must be a positive integer')
    else:
        us = 'usage: %prog INFILE1 [INFILE2]... OUTFILE [opts]'
        parser.error('Use -h for opts help')
    if opts.plottype not in ('gridded','scatter'):
        parser.error('-p Must be gridded or scatter')
    if opts.inputtype not in ('netcdf','latlon'):
        parser.error('-i Must be netcdf or latlon')
    if len(args) > 27:
        parser.error('Current input limit is 26 input files')
    elif len(args) < 2:
        parser.error('Must specify an input and output file')
    return opts, args
parse_args()
