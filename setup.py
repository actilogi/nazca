# Distutils setup script.
#
# run as
#   python3 setup.py sdist --formats=gztar,zip
#
from distutils.core import setup
#from setuptools import setup
setup(
        name = 'nazca',
        packages = ['nazca', 'nazca.fonts', 'nazca.demofab',
            'nazca.demopackager', 'nazca.pixapp'],
        package_data = {
            'nazca': ['*.csv', '*.gds'],
            'nazca.fonts': ['*.nft'],
            'nazca.demofab': ['*.csv', '*.lyp', '*.gds', 'gdsBB/*.gds',
                'gdsBB/*nazca.txt'],
            'nazca.demopackager': ['*.csv', '*.lyp', '*.gds'],
            },
#        include_package_data = True,
        install_requires = [
            'numpy', 'scipy', 'pandas', 'matplotlib', 'pillow', 'svgwrite', 'IPython'
            ],
        version = '0.5.11',
        description = 'Nazca Design',
        author = 'Ronald Broeke, Xaveer Leijtens',
        author_email = 'R.G.Broeke@gmail.com, X.Leijtens@gmail.com',
        url = 'http://nazca-design.org',
        license = 'AGPLv3+',
        classifiers = ['Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
          'Operating System :: OS Independent',
          'Development Status :: 4 - Beta',
          'Topic :: Scientific/Engineering',
          'Topic :: Scientific/Engineering :: Photonic Design Automation (PDA)',
          ],
        )

