import setuptools
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="streamlit-audio-stream-player",
    version="0.2.0",
    author="Benson Sung",
    author_email="benson.bs.sung@gmail.com",
    description="Beautiful audio stream player component for Streamlit with frequency visualization and state animations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bensonbs/streamlit-audio-stream-player",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="streamlit, audio, visualizer, frequency, component",
    python_requires=">=3.8",
    install_requires=[
        "streamlit >= 1.0.0",
    ],
)

