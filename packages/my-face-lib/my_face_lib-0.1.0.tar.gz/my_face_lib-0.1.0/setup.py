from setuptools import setup, find_packages

setup(
    name="my-face-lib",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["opencv-python", "onnxruntime", "numpy"],
    author="Nimalpranav",
    description="A lightweight face recognition library without dlib",
    python_requires=">=3.8",
)
