from setuptools import setup, find_packages

setup(
    name="logiq-cli",  # Unique PyPI package name; console command remains 'logiq'
    version="1.8.0",
    description="LogiIQ",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Vaibhav M N",
    author_email="vaibhavvaibhu2005@gmail.com",
    url="https://github.com/Vaibhav2154/LogIQ",
    # Map current directory to the 'aiagent' package to ensure module inclusion
    package_dir={
        'aiagent': '.',
        'aiagent.Scripts': 'Scripts',
    },
    packages=['aiagent', 'aiagent.Scripts', 'aiagent.Scripts.models'],
    include_package_data=True,
    install_requires=[
        "aiohttp>=3.8.0",
        "aiofiles>=23.0.0",
        "cryptography>=41.0.0",
        "schedule>=1.2.0",
        "requests>=2.31.0",
        "motor>=3.3.0",
        "pymongo>=4.5.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "rich>=13.0.0",
        "joblib>=1.3.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "redis>=5.0.0",
        "pywin32>=306; platform_system=='Windows'",
    ],
    entry_points={
        "console_scripts": [
            # Primary CLI entry point
            "logiq=aiagent.cli_tool:main",
            # Backward compatible alias
            "forensiq-cli=aiagent.cli_tool:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
