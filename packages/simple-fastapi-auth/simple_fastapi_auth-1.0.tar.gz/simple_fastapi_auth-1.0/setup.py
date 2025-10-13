from setuptools import setup, find_packages

setup(
    name='simple_fastapi_auth',
    version='1.0',
    author='Carlo Moro',
    author_email='cnmoro@gmail.com',
    description="A *heavily* opinionated library for simplifying the boilerplate of FastAPI authentication.",
    packages=find_packages(),
    package_data={
        "simple_fastapi_auth": ["*"]
    },
    include_package_data=True,
    install_requires=[
        "python-jose",
        "passlib",
        "bcrypt",
        "fastapi",
        "python-multipart"
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7'
)