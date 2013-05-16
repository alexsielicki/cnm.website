from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = read('cnm', 'website', 'version.txt').strip()

setup(name='cnm.website',
      version=version,
      description="Custom code for CNM",
      long_description=open('CHANGES.txt').read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Enfold Systems',
      author_email='info@enfoldsystems.com',
      url='http://www.enfoldsystems.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['cnm', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Plone',
          # -*- Extra requirements: -*-
          'oauth2client',
          'google-api-python-client',
          'Products.PloneFormGen',
          'archetypes.schemaextender',
          'collective.plonetruegallery',
          'collective.embedly',
          'collective.googleanalytics',
          'Products.ImageEditor',
          'Products.RedirectionTool',
          'plone.app.dexterity',
          'plone.app.caching',
          'requests',
          'uwosh.simpleemergency',
          'z3c.jbot',
          'collective.contentrules.mailtorole',
          'Products.OpenXml',
          'bpython'
      ],
      tests_require = [
           'zope.testing',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      [plone.recipe.zope2instance.ctl]
      bdebug = cnm.website:bpython_init
""",
      )
