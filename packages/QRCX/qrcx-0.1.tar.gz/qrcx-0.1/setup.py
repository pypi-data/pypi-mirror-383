from setuptools import setup, find_packages

setup(
    name='QRCX',
    version='0.1',
    author='Babar Ali Jamali',
    author_email='babar995@gmail.com',
    description='Advanced QR Code Generator Tool (QRCX)',
    packages=find_packages(),
    install_requires=['qrcode', 'fpdf'],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'qrcx = qrcx.qrcx:main',  # updated path
        ],
    },
)
