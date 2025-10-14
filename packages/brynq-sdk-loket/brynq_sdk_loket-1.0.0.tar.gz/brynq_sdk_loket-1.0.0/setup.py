from setuptools import find_namespace_packages, setup

setup(
    name='brynq_sdk_loket',
    version='1.0.0',
    description='BrynQ SDK for Loket integration',
    long_description='BrynQ SDK for integrating with Loket system',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=4,<5',
        'brynq-sdk-functions>=2',
        'requests>=2,<=3'
    ],
    zip_safe=False,
)
