from setuptools import setup, find_packages


setup(
    name="R2Install",
    version="0.1",
    packages=find_packages(),

    entry_points = {
        'console_scripts': [
            'r2install=R2Install.main:main'
        ]
    }
)