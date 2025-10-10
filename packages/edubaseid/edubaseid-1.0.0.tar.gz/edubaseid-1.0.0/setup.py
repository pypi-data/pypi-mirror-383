from setuptools import setup, find_packages

setup(
    name='edubaseid',
    version='1.0.0',
    author='Sadriddin Axmadullayev',  # O'zingizning ismingiz
    author_email='saxhmadullayev@gmail.com',
    description='EduBaseID OAuth2/OpenID Connect client SDK for Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/dev-723743344',  # GitHub yoki boshqa repo URL
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests>=2.25.0',
        'click>=8.0.0',
        # Qo'shimcha: 'django', 'djangorestframework' agar kerak bo'lsa
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
    entry_points={
        'console_scripts': [
            'edubaseid=edubaseid.cli:cli',
        ],
    },
    tests_require=['pytest'],
)