from distutils.core import setup
import setuptools

setup(
    # Application name:
    name="percato",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Sadiq SheshKhan",
    author_email="sadiqush@gmail.com",

    # Packages
    packages=["percato"],

    keywords=["percato", "ocr", "farsi", "persian", "dataset"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="http://pypi.org/project/percato",

    # license
    license="GPLv3",
    description="Farsi data generator and an OCR tool for Farsi using Detectron2",

    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    # Dependent packages (distributions)
    install_requires=[
        "pillow",
        "opencv-python",
        "imagecorruptions",
        "imgaug"
    ],
    setup_requires=[
        "pillow",
        "opencv-python",
        "imagecorruptions",
        "imgaug"
    ],
    python_requires='>= 3',

    entry_points={'console_scripts': ['percato = percato.run:run']}
)
