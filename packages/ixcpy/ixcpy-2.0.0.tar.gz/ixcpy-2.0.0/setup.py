from setuptools import setup


with open('README_PyPI.md', 'r', encoding='utf-8') as file:
    readme = file.read()


setup(
    name='ixcpy',
    version='2.0.0',
    license='MIT License',
    author='Felipe Sousa',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='fscarmo@proton.me',
    description=u'Wrapper não oficial para conexão com a API do sistema IXC Provedor',
    url='https://github.com/SousaFelipe/ixcpy',
    packages=['ixcpy'],
    install_requires=['requests'],
    keywords=[
        'ixc',
        'ixcsoft',
        'api ixc',
        'ixc provedor',
        'ixc python'
    ]
)
