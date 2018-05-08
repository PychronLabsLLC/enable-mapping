from setuptools import setup, find_packages

from mapping import __version__, __requires__


setup(
    name='mapping',
    version=__version__,
    author='Enthought, Inc.',
    author_email='info@enthought.com',
    maintainer='ETS Developers',
    maintainer_email='enthought-dev@enthought.com',
    classifiers=[c.strip() for c in """\
        Development Status :: 5 - Production/Stable
        Intended Audience :: Developers
        Intended Audience :: Science/Research
        License :: OSI Approved :: BSD License
        Operating System :: MacOS
        Operating System :: Microsoft :: Windows
        Operating System :: OS Independent
        Operating System :: POSIX
        Operating System :: Unix
        Programming Language :: Python
        Topic :: Scientific/Engineering
        Topic :: Software Development
        Topic :: Software Development :: Libraries
        """.splitlines() if len(c.strip()) > 0],
    description='application tools',
    long_description=open('README.rst').read(),
    include_package_data=True,
    package_data={
        'mapping': ['data/*'],
    },
    install_requires=__requires__,
    license='BSD',
    packages=find_packages(exclude=['ci']),
    platforms=["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    zip_safe=False,  # We have data files, and use __file__!
)
