from distutils.core import  setup
import setuptools
packages = ['Maclip']# 唯一的包名，自己取名
setup(name='Maclip',
	version='1.0',
	author='Beyond Cosine Similarity: Magnitude-Aware CLIP for No-Reference Image Quality Assessment',
    packages=packages, 
    package_dir={'requests': 'requests'},)
