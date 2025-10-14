from setuptools import setup, find_packages

setup(
    name="edik-my-library",  # unikaldırsa qəbul ediləcək
    version="0.1.1",
    packages=find_packages(),  # Avtomatik olaraq bütün qovluqları tapır
    install_requires=[],       # Əgər başqa kitabxanalara ehtiyac varsa buraya əlavə et
    author="Sənin adın",
    author_email="email@example.com",
    description="Bu mənim ilk PyPI kitabxanam",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/username/my_library",  # GitHub linki varsa
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
