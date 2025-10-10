from setuptools import setup, find_packages

setup(
    name="install-python-studio",
    version="0.0.2",
    packages=find_packages(),
    install_requires=[],
    author="",
    author_email="",
    description="",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    package_data={
        "the_chief.member": ["prompt.jinja"],
    },
)
