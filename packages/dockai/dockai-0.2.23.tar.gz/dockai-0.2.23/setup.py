from setuptools import setup, find_packages

setup(
    name="dockai",
    version="0.2.23",
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
    description="AI destekli Docker log analiz aracı (CLI + Cloud)",
    license="Apache License 2.0",
    python_requires=">=3.9",
)
