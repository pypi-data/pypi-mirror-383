from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_visma_lon_hr',
    version='3.1.0',
    description='Visma Lon & HR wrapper from BrynQ',
    long_description='Visma Lon & HR wrapper from BrynQ',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=4,<5',
        'brynq-sdk-functions>=2.1.3,<3',
        'pandas>=2,<3',
        'pydantic>=2',
        'requests>=2',
        'xmltodict>=0.13',
        'aiohttp>=3.8',
        'python-dotenv>=1.0'
    ],
    zip_safe=False,
)
