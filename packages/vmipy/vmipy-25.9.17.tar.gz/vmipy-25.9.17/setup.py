from setuptools import setup, find_packages

VERSION = "25.9.17"

install_requires = [
    'pyserial',
    'paho-mqtt',
    'websocket-client',
]

setup(
    name="vmipy",
    version=VERSION,
    description="SDK for vmilabs",
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    author="vmilabs",
    author_email="zeekzhou@163.com",
    license="Apache-2.0",
    url="https://github.com/openvmi/vmipy",
    python_requires='>=3.6',
    keywords="vmilabs python SDK",
    install_requires=install_requires,
    packages=find_packages('src'),
    package_dir={'': 'src'},
)
