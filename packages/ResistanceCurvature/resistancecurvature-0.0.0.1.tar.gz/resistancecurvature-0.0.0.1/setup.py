import codecs
import os
from setuptools import setup, find_packages

# these things are needed for the README.md show on pypi (if you dont need delete it)
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()


setup(
    name="ResistanceCurvature",
    version="0.0.0.1",
    author="Chaoqun Fei, Tinglve Zhou, Yangyang Li",
    author_email="1079484353@qq.com",
    description='Calculate resistance curvature',
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    license="Apache-2.0",
    license_files=["LICENSE"],
    keywords=['python', 'Curvature', 'Resistance','Geometry','windows','mac','linux'],
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Environment :: GPU :: NVIDIA CUDA",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=1.10.0",
    ],
)
