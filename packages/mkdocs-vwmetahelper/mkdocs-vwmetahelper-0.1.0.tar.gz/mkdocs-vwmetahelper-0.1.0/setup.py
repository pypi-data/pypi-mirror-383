from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_desc = f.read()

setup(
    name="mkdocs-vwmetahelper",
    version="0.1.0",
    description="MkDocs plugin providing get_meta() and call_macro() with lazy front-matter indexing.",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    author="Che Wei Chang & Contributors",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "mkdocs>=1.5",
        "Jinja2>=3.0",
        "PyYAML>=6.0",
    ],
    entry_points={
        "mkdocs.plugins": [
            "vwmetahelper = mkdocs_vwmetahelper.plugin:VWMetaHelperPlugin",
        ]
    },
    python_requires=">=3.8",
    url="https://github.com/your-org/mkdocs-vwmetahelper",
    project_urls={
        "Issues": "https://github.com/your-org/mkdocs-vwmetahelper/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: MkDocs",
    ],
)
