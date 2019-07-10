from setuptools import setup, find_packages
setup(
    name="psemplot",
    version="0.1",
    packages = find_packages(),
    scripts = ['bin/psemplot',],
    python_requires='>=3.5',
    setup_requires=['numpy>=1.12','netCDF4>=1.2.9','pyproj','matplotlib'],
    author_email='james.beidler@gmail.com'
)
