from setuptools import setup, find_packages

setup(
    name="pyejs",
    version="0.1.0",
    author="Sanjh",
    author_email="sanjhdeysarker@gmail.com",
    description="A Python template engine inspired by EJS for dynamic HTML rendering.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SanjhDeySarker/pyejs.git",
    packages=find_packages(),
    python_requires=">=3.8",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
)
