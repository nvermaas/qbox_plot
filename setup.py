from setuptools import setup, find_packages

setup(name='qbox_plot',
      version='1.1.0',
      description='Plotting QBoxNext text files.',
      url='',
      author='Nico Vermaas',
      author_email='nvermaas@astron.nl',
      license='BSD',
      install_requires=['plotly','requests'],
      packages=find_packages(),
      entry_points={
            'console_scripts': [
                  'qbox_plot=qbox_plot.qbox_plot:main',
            ],
      },
      scripts=['scripts/qbx_dump_and_copy.sh']
      )