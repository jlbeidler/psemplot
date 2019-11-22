"""
Process the command line arguments and switches
"""

from optparse import OptionParser, OptionGroup

def parse_args():
    parser = OptionParser(usage = 'usage: %prog INFILE OUTFILE [options]')
    parser.add_option('-f', '--formula', dest='formula', help='Formula to plot. Specify a species and an input file in the format [SPECIES]_[A...Z] where the A-Z corresponds to the infile order.\
                Single file: VOC_A   Difference plot: CO_A-CO_B   % Diff: (CO_B-CO_A)/(CO_A)', default='')
    parser.add_option('-s', '--timestep', dest='time_step', help='Timestep to select from file. Default is 0.', default=0)
    parser.add_option('-t', '--title', dest='title', help='Top title.  Use @S as speciesname variable in title', default='@S')
    parser.add_option('-u', '--sub-title', dest='subtitle', help='Subtitle. Defaults to display max and min values', default='')
    parser.add_option('--scale-label', dest='scalelabel', help='Label for scale.  Defaults to tons/year.', default='tons/year')
    parser.add_option('-b', dest='bins', help='Turn on gradated plot and set number of color bins.  Number must be greater than 2.', default=False)
    parser.add_option('--ticks', dest='ticks', help='Set the number of ticks to display', default=False)
    parser.add_option('--vmin', dest='vmin', help='Scale minimum cutoff.  Add "%" to the end to use percentile.', default='0')
    parser.add_option('--vmax', dest='vmax', help='Scale maximum cutoff.  Add "%" to the end to use percentile. Defaults to 95th percentile.', default='95%')
    parser.add_option('-g', dest='neutral', help='Use neutral color for values within x of 0 (or closest limit to 0).  Defaults to 0.01%.  Use single number 0-100%. 0% Disables neutral.', default='0.01%')
    parser.add_option('--cutoffs', dest='cutoff_list', help='Optional list of scale cutoffs to create uneven bins. Currently only works with data values zero or higher.', default='')
    parser.add_option('--neutral-color', dest='ncolor', help='Set neutral color to white, grey, or black', default='')
    parser.add_option('--neutral-fill', dest='nfill', help='Fill color bins on scale with neutral color rather than overlap', default=False, action='store_true')
    parser.add_option('--shape-file', dest='shape_file', help='Path to custom shapefile', default='')
    parser.add_option('--shape-att', dest='shape_att', help='Shapefile attribute to plot', default='')
    parser.add_option('--cmap', dest='cmap', help='Matplotlib colormap', default=None)
    parser.add_option('--mask_less', dest='mask_less', help='Mask values lower than the specified value from the plot', default=None)
    parser.add_option('--force-diff', dest='force_diff', action='store_true', help='Force a difference colormap even if data has consistent signs', default=False)
    parser.add_option('--hi-res', dest='hi_res', action='store_true', help='Output a high resolution plot', default=False)
    parser.add_option('--no-autoscale', dest='no_auto', action='store_true', help='Turn off the autoscaling and use exactly what is entered for max and min', default=False)
    parser.add_option('--report-max', dest='repmax', help='Report the scale maximum used to a file', default='')
    (options, args) = parser.parse_args()
    if len(args) >= 2:
        if len(options.formula) < 3:
            parser.error('-f Must specify a formula.')
        try:
            int(options.bins)
        except ValueError:
            parser.error('-b Number of bins must be a positive integer')
    else:
        us = 'usage: %prog INFILE1 [INFILE2]... OUTFILE [options]'
        parser.error('Use -h for options help')
    if len(args) > 27:
        parser.error('Current input limit is 26 input files')
    elif len(args) < 2:
        parser.error('Must specify an input and output file')
    return options, args

