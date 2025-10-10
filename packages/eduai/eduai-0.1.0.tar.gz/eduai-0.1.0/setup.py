from setuptools import setup, find_packages

setup(
    name="eduai",
    version="0.1.0",
    author="Ahmad",
    author_email="ahmad,sudais.work@example.com",
    description="AI-powered educational translation tool for students and teachers",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/eduai",
    packages=find_packages(),
    install_requires=[
        "openai",
        "googletrans==4.0.0rc1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
