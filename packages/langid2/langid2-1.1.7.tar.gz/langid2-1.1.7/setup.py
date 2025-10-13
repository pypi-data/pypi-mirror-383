from setuptools import setup, find_packages
import sys, os

version = '1.1.7'

setup(name='langid2',
      version=version,
      description="langid.py is a standalone Language Identification (LangID) tool. This is a repackaging of the original langid, just to make it a wheel.",
      long_description="""\
""",
      classifiers=[
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering :: Artificial Intelligence',
          'Topic :: Text Processing :: Linguistic',
          'License :: OSI Approved :: BSD License',
      ],
      keywords='language detection',
      author='Marco Lui',
      author_email='saffsd@gmail.com',
      url='https://github.com/saffsd/langid.py',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'numpy',
      ],
      entry_points= {
        'console_scripts': [
          'langid = langid.langid:main',
        ],
      },
      )
