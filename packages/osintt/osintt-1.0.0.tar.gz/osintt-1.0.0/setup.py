from setuptools import setup

setup(
    name="osintt",
    version="1.0.0",
    author="Darkboy",
    author_email="your-email@example.com",
    description="OSINT Mobile Number Lookup Tool",
    long_description="Mobile number lookup tool for OSINT investigations",
    py_modules=["osintt"],
    install_requires=["requests"],
    entry_points={
        'console_scripts': ['osintt=osintt:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
