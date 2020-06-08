import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="puree",
    version="1.0.2",
    author="Jay Sullivan",
    author_email="jay@identity.pub",
    description="PUREE: Password-based Uniform-Random-Equivalent Encryption",
    url="https://puree.cc",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    scripts=['puree'],
    data_files = [('man/man1', ['docs/puree.1'])],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: Public Domain",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
    install_requires=[
        'pysodium>=0.7.5', 'pysodium<1.0.0',
        'argon2-cffi>=20.1.0', 'argon2-cffi<21.0.0'
    ]
)
