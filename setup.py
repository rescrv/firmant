from distutils.core import setup


classifiers = [ 'Development Status :: 4 - Beta'
              , 'Intended Audience :: Developers'
              , 'License :: OSI Approved :: BSD License'
              , 'Operating System :: MacOS :: MacOS X'
              , 'Operating System :: POSIX :: Linux'
              , 'Operating System :: Unix'
              , 'Programming Language :: Python :: 2.6'
              , 'Topic :: Internet :: WWW/HTTP :: Site Management'
              ]

setup(name='Firmant',
      version='0.2dev',
      author='Robert Escriva (rescrv)',
      author_email='firmant@mail.robescriva.com',
      packages=['firmant'
               ,'firmant.parsers'
               ,'firmant.routing'
               ,'firmant.templates'
               ,'firmant.utils'
               ,'firmant.writers'
               ],
      package_dir={'firmant': 'firmant'},
      package_data={'firmant': ['templates/*.html',
                                'templates/*/*.html']},
      scripts=['bin/firmant'],
      url='http://firmant.org/',
      license='3-clause BSD',
      description='A framework for static web applications.',
      long_description=open('doc/README.rst').read(),
      classifiers=classifiers,
      )
