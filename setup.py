import os
import re
from setuptools import setup, find_packages
from subprocess import check_output


MAJOR = 1
MINOR = 0
MICRO = 1

IS_RELEASED = False

VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)


# Return the git revision as a string
def git_version():
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}

        for k in ['SYSTEMROOT', 'PATH', 'HOME']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = check_output(cmd, env=env)
        return out
    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        git_revision = out.strip().decode('ascii')
    except OSError:
        git_revision = "Unknown"
    try:
        out = _minimal_ext_cmd(['git', 'rev-list', '--count', 'HEAD'])
        git_count = out.strip().decode('ascii')
    except OSError:
        git_count = '0'
    return git_revision, git_count


def write_version_py(filename='mapping/_version.py'):
    template = """\
# THIS FILE IS GENERATED FROM mapping SETUP.PY
version = '{version}'
full_version = '{full_version}'
git_revision = '{git_revision}'
is_released = {is_released}

if not is_released:
    version = full_version
"""
    # Adding the git rev number needs to be done inside
    # write_version_py(), otherwise the import of mapping._version messes
    # up the build under Python 3.
    fullversion = VERSION
    if os.path.exists('.git'):
        git_rev, dev_num = git_version()
    elif os.path.exists('mapping/_version.py'):
        # must be a source distribution, use existing version file
        try:
            from mapping._version import git_revision as git_rev
            from mapping._version import full_version as full_v
        except ImportError:
            raise ImportError("Unable to import git_revision. Try removing "
                              "mapping/_version.py and the build directory "
                              "before building.")

        match = re.match(r'.*?\.dev(?P<dev_num>\d+)', full_v)
        if match is None:
            dev_num = '0'
        else:
            dev_num = match.group('dev_num')
    else:
        git_rev = 'Unknown'
        dev_num = '0'

    if not IS_RELEASED:
        fullversion += '.dev{0}'.format(dev_num)

    with open(filename, "wt") as fp:
        fp.write(template.format(version=VERSION,
                                 full_version=fullversion,
                                 git_revision=git_rev,
                                 is_released=IS_RELEASED))
    return fullversion

DEPENDENCIES = [
    'enable',
    'chaco',
    'geojson',
    'requests',
]


if __name__ == "__main__":
    __version__ = write_version_py()

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
            'mapping.enable': ['fonts/*'],
        },
        install_requires=DEPENDENCIES,
        license='BSD',
        packages=find_packages(exclude=['ci']),
        platforms=["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
        zip_safe=False,  # We have data files, and use __file__!
    )
