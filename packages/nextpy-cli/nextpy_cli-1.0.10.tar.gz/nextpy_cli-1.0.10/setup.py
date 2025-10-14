from setuptools import setup, find_packages

setup(
    name="nextpy",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'nextpy': ['templates/**/*'],
    },
)
