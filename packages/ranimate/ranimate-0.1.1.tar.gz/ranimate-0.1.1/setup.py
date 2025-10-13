from setuptools import setup, find_packages

setup(
    name="ranimate",
    version="0.1.1",
    author="Repaa",
    author_email="personal@repaa.xyz",
    description="Animation Library",
    long_description="",
    long_description_content_type="text/markdown",
    url="https://github.com/repaa818/ranimate",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pygame",
        "numpy",
        "opencv-python",
        "moviepy",
        "decorator",
        "proglog",
        "imageio",
        "imageio-ffmpeg"
    ],
    python_requires=">=3.10",
)
