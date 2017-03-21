from setuptools import setup, find_packages

version = '2.0'

long_description = (
    open('README.rst').read()
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='collective.lesscss',
      version=version,
      description="This package allow theme developers to add LESS stylesheets into a Plone site.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone zope less css',
      author='Victor Fernandez de Alba',
      author_email='sneridagh@gmail.com',
      url='https://github.com/collective/collective.lesscss',
      license='gpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.ResourceRegistries',
          'plone.resource',
          'lesscpy',
          # -*- Extra requirements: -*-
      ],
      extras_require={'test': ['plone.app.testing']},
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
