from setuptools import setup, find_packages
import sys, os

version = "1.34"

setup(
    name="tk_hauteskundeak",
    version=version,
    description="Tokikerako hauteskundeetarako tresna",
    long_description="""\
""",
    classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords="",
    author="jargarate",
    author_email="jargarate@codesyntax.com",
    url="",
    license="",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "django-highcharts == 0.1.7",
        "django-colorfield == 0.7.2",
        "xmltodict == 0.13.0",
        "django-object-actions == 4.1.0",
        "django-import-export",
    ],
    entry_points="""
      # -*- Entry points: -*-
      """,
)
