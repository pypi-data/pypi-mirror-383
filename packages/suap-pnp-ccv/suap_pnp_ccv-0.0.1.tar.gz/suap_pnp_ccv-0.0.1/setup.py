from setuptools import find_packages, setup

setup(
    name='suap_pnp_ccv',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[],
    include_package_data=True,
    license='BSD License',
    description='PNP CCV application for SUAP',
    long_description='',
    url='https://gitlab.ifrn.edu.br/cosinf/suap_pnp_ccv',
    author='Breno Silva',
    author_email='breno.silva@ifrn.edu.br',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
