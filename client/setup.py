from setuptools import setup, find_packages

setup(
    name='Sauvegardeur',
    version='1.0.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'sauvegardeur = client_package.client:main'
        ]
    },
    install_requires=[
        'requests'
    ],
)
