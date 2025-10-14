from setuptools import setup

setup(
  name = 'DPConCFil',
  packages = ['DPConCFil'],
  version = '0.0.5',
  description = 'A collection of filament identification and analysis algorithms',
  author = ['Jiang Yu'],
  author_email = 'yujiang@pmo.ac.cn',
  url = 'https://github.com/JiangYuTS/DPConCFil',
#   download_url = '',
  keywords = ['astrophysics', 'DPConCFil', 'filaments'],
  classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
  install_requires=[
      'numpy',
      'scipy',
      'matplotlib',
      'astropy',
      'scikit-learn',
      'scikit-image',
      'networkx',
      'pandas',
      'tqdm',
      'FacetClumps',
      'radfil',
      
  ],
  python_requires='>=3.6',
)

