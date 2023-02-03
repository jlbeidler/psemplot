from setuptools import setup, find_packages
setup(
    name="psemplot",
    version="0.4.0",
    packages = find_packages(),
    scripts = ['bin/psemplot',],
    python_requires='>=3.5',
    setup_requires=['numpy>=1.19.5','netCDF4>=1.2.9','pyproj','matplotlib','basemap==1.3.0','matplotlib==3.3.4'],
    author_email='james.beidler@gmail.com'
)
