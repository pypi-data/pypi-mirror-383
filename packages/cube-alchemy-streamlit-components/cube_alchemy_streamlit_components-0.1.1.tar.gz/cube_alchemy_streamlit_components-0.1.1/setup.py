from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="cube-alchemy-streamlit-components",
    version="0.1.1",
    author="Juan C. Del Monte",
    author_email="delmontejuan92@gmail.com",
    description="Components for Streamlit and Cube Alchemy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cube-alchemy/cube-alchemy-streamlit-components",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={
        "cube_alchemy_streamlit_components": ["filter/frontend/build/**"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.7",
    install_requires=[
        # By definition, a Custom Component depends on Streamlit.
        # If your component has other Python dependencies, list
        # them here.
        "streamlit >= 0.63",
    ],
    extras_require={
        "devel": [
            "wheel",
            "pytest==7.4.0",
            "playwright==1.48.0",
            "requests==2.31.0",
            "pytest-playwright-snapshot==1.0",
            "pytest-rerunfailures==12.0",
        ]
    }
)
