from setuptools import setup, find_packages

setup(
    name="lf_pollywog",
    version="0.1.1",
    description="Python library for working with Leapfrog calculation sets (.lfcalc files)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Arthur Endlein",
    author_email="endarthur@gmail.com",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.7",
    include_package_data=True,
    extras_require={
        "conversion": ["scikit-learn"],
        "dev": ["pytest", "scikit-learn", "pandas"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
