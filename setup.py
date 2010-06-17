from distutils.core import setup

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
      )
