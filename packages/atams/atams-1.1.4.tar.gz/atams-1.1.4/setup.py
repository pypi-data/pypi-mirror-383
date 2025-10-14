from setuptools import setup, find_packages

setup(
    name="atams",
    version="1.1.4",
    description="Advanced Toolkit for Application Management System",
    author="ATAMS Team",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "sqlalchemy>=2.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "pycryptodome>=3.19.0",
        "httpx>=0.25.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "jinja2>=3.1.0",
        "inflect>=7.0.0",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "atams=atams.cli.main:app",
        ],
    },
    include_package_data=True,
    package_data={
        "atams": ["cli/templates/*.jinja2", "cli/templates/project/*.jinja2"],
    },
)
