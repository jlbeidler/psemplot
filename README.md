# psemplot
SMOKE gridded emissions visualizer

# Overview
Psemplot is designed to rapidly create gridded emissions plots from SMOKE output for quality assurance and evaluation purposes. It is built using common Python libraries and can be used across multiple platforms. Autoscaling features allow for plots to be created without manual interaction and with minimal command line arguments. However, many configuration options exist to tweak the appearance and selection of the gridded data. Psemplot supports most gridded I/O API compatible netCDFs as inputs, including SMOKE emissions outputs and CMAQ gridded concentration files.

# Requirements
Python 3.5 or later is required. 
Psemplot is tested with numpy 1.12, netCDF4 1.2.9, pyproj, and matplotlib with basemap. Variations in module versions may introduce incompatibilities.

# Installation
Installation may be done using Python setuptools.
Simply run python3 setup.py install to begin the process.

# Example Command Lines
Creation of simple autoscaled plot of NOX:

`psemplot 2016_hemi_108k_annual.ncf 2016_hemi_nox.png -f "NO_A+NO2_A+HONO_A" -t "Hemispheric NOx"`

Generation of a high resolution difference plot using a custom background shapefile and a scale maximum of 100 tons:

`psemplot ptfire_2016.ncf ptfire_2017.ncf ptfire_pec.png -f "PEC_B-PEC_A" -t "Wildland Fire PEC Difference" --scale-label=tons --hi-res --force-diff --vmax=100 -g 0.5% -b 16 --shape-file usgs_na_2006`

