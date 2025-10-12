from setuptools import setup, find_packages

setup(
    name="my-face-lib",
    version="0.2.0",
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
