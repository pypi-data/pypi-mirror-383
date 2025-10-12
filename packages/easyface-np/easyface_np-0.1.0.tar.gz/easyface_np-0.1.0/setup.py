from setuptools import setup, find_packages

setup(
    name="easyface-np",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
    "numpy>=1.26",
    "opencv-python>=4.8",
    "onnxruntime>=1.17"
],
    author="Nimalpranav",
    description="A lightweight face recognition library without dlib",
    python_requires='>=3.10, <3.14',
)
