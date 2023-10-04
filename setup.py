from setuptools import setup, find_packages, Extension
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
setup(
    name="psemplot",
    version="0.4.2",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.5',
    scripts=['bin/psemplot',],
    setup_requires=['numpy>=1.19.5','netCDF4>=1.2.9','pyproj>=3.6.0','matplotlib','basemap==1.3.0','matplotlib==3.3.4'],
    install_requires=['numpy>=1.19.5','netCDF4>=1.2.9','pyproj>=3.6.0','matplotlib','basemap==1.3.0','matplotlib==3.3.4'],
    author_email='beidler.james@epa.gov'
)

