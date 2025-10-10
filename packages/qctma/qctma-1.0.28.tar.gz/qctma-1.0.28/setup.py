from setuptools import setup, find_packages

setup(name='qctma',
      version='1.0.28',
      description="Injects material (Young's modulus) to each element, based on a Dicom stack, and gray level to Young's"
                  "modulus relationships. Specifically designed to be used with Ansys .cdb meshes.",
      long_description="Injects material (Young's modulus) to each element, based on a Dicom stack, and gray level to Young's"
                       "modulus relationships. Specifically designed to be used with Ansys .cdb meshes.",
      url='https://github.com/MarcG-LBMC-Lyos/QCTMA',
      author='Marc Gardegaront',
      author_email='m.gardegaront@gmail.com',
      license='GNU GPLv3',
      packages=find_packages(),
      package_data={'': ['*.json']},
      py_modules=['qctma', 'rw_cdb'],
      install_requires=['matplotlib>=2.2.5', 'numpy>=1.19.5', 'pydicom>=2.1.2', 'scipy>=1.5.4',
                        'reportlab>=3.5.66', 'nibabel>=5.2.0'
                        ],
      python_requires=">=3.6")