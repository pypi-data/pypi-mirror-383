from setuptools import setup, find_packages

setup(
    name='grouped_timeserie_cv',
    version='0.1.1',
    packages=find_packages(),
    install_requires=["plotly", 'pandas', 'scikit-learn', 'matplotlib'],
    author='Zenta AB',
    author_email='admin@zenta.se',
    description='A machine learning library based on sklearn that supports grouped time series cross-validation',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/zenta-ab/grouped_timeserie_cv',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)