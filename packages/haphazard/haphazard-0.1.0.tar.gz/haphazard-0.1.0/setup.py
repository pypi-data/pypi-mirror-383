from setuptools import setup, find_packages

setup(
    name="haphazard",
    version="0.1.0",
    author="Arijit Das",
    author_email="dasarijitjnv@gmail.com",
    description="A modular framework for registering and running haphazard datasets and models.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/theArijitDas/Haphazard-Package/",
    project_urls={
        "Bug Tracker": "https://github.com/theArijitDas/Haphazard-Package/issues",
        "Source Code": "https://github.com/theArijitDas/Haphazard-Package/",
    },
    packages=find_packages(exclude=("tests", "docs")),
    include_package_data=True,
    install_requires=[
        "numpy",
        "pandas",
        "tqdm",
        "scikit-learn",
        "torch",
    ],
    python_requires=">=3.10",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="machine-learning haphazard models datasets registration framework",
)
