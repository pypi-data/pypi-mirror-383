from setuptools import setup, find_packages

setup(
    name="dockai",
    version="0.2.25",
    packages=find_packages(),
    install_requires=[
        "click",
        "docker",
        "openai",
        "requests",
        "termcolor",
        "fastapi",
        "uvicorn",
        "stripe",
        "python-dotenv",
        "jwt"
    ],
    entry_points={
        "console_scripts": [
            "dockai=dockai.cli.commands:cli",
        ],
    },
    author="Ahmet Atakan",
    author_email="ahmetatakan.tech@gmail.com",
    description="AI destekli Docker log analiz aracı (CLI + Cloud)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    python_requires=">=3.9",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Monitoring",
    ],
)
