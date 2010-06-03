from distutils.core import setup

setup(name='Firmant',
      version='0.2dev',
      author='Robert Escriva (rescrv)',
      author_email='firmant@mail.robescriva.com',
      packages=['firmant'
               ,'firmant.parsers'
               ,'firmant.routing'
               ,'firmant.utils'
               ,'firmant.writers'
               ],
      scripts=['bin/firmant'],
      url='http://projects.robescriva.com/projects/show/firmant',
      license='LICENSE',
      description='A framework for developing static web applications.',
      long_description=open('doc/README.rst').read(),
      )
