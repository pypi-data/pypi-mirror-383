from setuptools import setup, find_packages

setup(
    name='QRH',
    version='1.0',
    author='Babar Ali Jamali',
    author_email='babar995@gmail.com',
    description='Advanced QR Code Generator Tool (QRH)',
    packages=find_packages(),
    install_requires=['qrcode', 'fpdf'],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'qrh = qrh.qrh:main',  # updated path
        ],
    },
)
