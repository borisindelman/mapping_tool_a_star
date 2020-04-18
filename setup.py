from setuptools import setup

PACKAGE_NAME = 'mapping_tool_a_star'

# Read-in the version
# See 3 in https://packaging.python.org/guides/single-sourcing-package-version/
version_file = './{}/version.py'.format(PACKAGE_NAME)
version = {}
try:
    # Python 2
    execfile(version_file, version)
except NameError:
    # Python 3
    exec(open(version_file).read(), version)

# Read-in the README.md
with open('README.md', 'r') as f:
    readme = f.readlines()
readme = ''.join(readme)

setup(name=PACKAGE_NAME,
      version=version['__version__'],
      url='https://https://github.com/borisindelman/mapping_tool_a_star',
      license='MIT',
      author='Boris Indelman',
      author_email='boris.indelman@gmail.com',
      description='Mapping tool and a* navigation demonstration',
      long_description=readme,
      long_description_content_type="text/markdown",
      keywords='template, python, package',
      packages=[PACKAGE_NAME],
      include_package_data=False,  # => if True, you must provide MANIFEST.in
      entry_points='''
        [console_scripts]
        mapping_tool=mapping_tool_a_star.MappingTool:main
      ''',
      classifiers=[
          "License :: OSI Approved :: MIT License",
      ],
      install_requires=['click', 'six', 'numpy', 'future'],
      zip_safe=True)