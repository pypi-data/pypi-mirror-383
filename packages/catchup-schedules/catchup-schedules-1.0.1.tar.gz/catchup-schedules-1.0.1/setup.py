import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="catchup-schedules", # Replace with your own username
    version="1.0.1",
    author="1325OK",
    author_email="1325ok.help@gmail.com",
    description="A robust scheduling module designed to catch up on periodic tasks that were skipped due to system pauses or downtime.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/1325ok/catchup-schedules",
    install_requires=[],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    keywords=['schedules', 'remind', 'continue', 'date', 'task','save','scheduler','catchup','missed'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
