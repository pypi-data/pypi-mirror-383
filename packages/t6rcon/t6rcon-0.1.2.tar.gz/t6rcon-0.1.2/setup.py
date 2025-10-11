from setuptools import setup, find_packages

setup(
    name="t6rcon",
    version="0.1.2",
    author="budiworld",
    author_email="budi.world@yahoo.com",
    description="A RCON module for Plutonium T6",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/Yallamaztar/iw4m", 
    packages=find_packages(),
    install_requires=[
        "pydantic"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)