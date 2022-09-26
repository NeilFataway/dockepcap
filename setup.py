from setuptools import setup, find_packages

install_requires = [
    "Flask",
    "netns",
    "docker",
    "psutil"
]

entry_points = {
    "console_scripts": [
        "ddump:dockerpcap.ddumps:ddump",
        "ddump-server:dockerpcap.main:"
    ]
}

setup(
    name="dockerpcap",
    version="1.0.0",
    author="Neil Feng",
    author_email="Neil_Feng@foxmail.com",
    packages=find_packages("."),
    license="Apache 2.0",
    description="docker pcap agent used to capture container network namespace traffic",
    install_requires=install_requires,
    entry_points=entry_points
)