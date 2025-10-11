from setuptools import setup, find_packages
import os

setup(
    name="amdsmi",
    version="7.0.2",
    author="AMD",
    author_email="amd-smi.support@amd.com",
    description="AMDSMI Python LIB - AMD GPU Monitoring Library",
    url="https://github.com/ROCm/amdsmi",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
    include_package_data=True,
    package_data={
        '': ['*.so'],
    },
    zip_safe=False,
    license='amdsmi/LICENSE',
)
