from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_zucchetti',
    version='1.0.0',
    description='Zucchetti HR PERSONAL DATA import wrapper from BrynQ',
    long_description='Zucchetti HR PERSONAL DATA (HRANAGRAFICO) SOAP import wrapper for BrynQ SDK',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'requests>=2,<=3',
        'pydantic>=2,<3',
        'pandas>=2.2.0,<3.0.0',
        'zeep>=4.0.0,<5.0.0',
    ],
    zip_safe=False,
)
