from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="alphalens-modify",
    version='0.1.0',
    author="XiaoYinXu",
    author_email="965418170@qq.com",
    description="A modified version of alphalens with updated dependencies and fixes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GenjiYin/alphalens-modify",
    packages=find_packages(),
    keywords=["finance", "quantitative", "factor", "analysis", "investment"], 
    install_requires=[
        "pandas==2.2.3",
        "numpy==1.26.4",
        "scipy==1.14.1",
        "statsmodels==0.14.5",
        "matplotlib==3.9.2",
        "seaborn==0.13.2",
        "IPython",
    ]
)