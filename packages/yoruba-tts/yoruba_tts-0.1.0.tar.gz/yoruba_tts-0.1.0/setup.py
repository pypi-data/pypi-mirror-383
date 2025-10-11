from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="yoruba-tts",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Yoruba Text-to-Speech package - downloads models automatically",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=requirements,
    # NO package_data - models will be downloaded
    entry_points={
        'console_scripts': [
            'yoruba-tts=yoruba_tts.cli:main',
        ],
    },
    python_requires=">=3.7",
)