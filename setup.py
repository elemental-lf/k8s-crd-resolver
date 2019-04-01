try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.rstrip() for line in f]

setup(
    name='k8s-crd-resolver',
    version='0.1.0',
    description='Kubernetes CRD Resolver',
    url='http://github.com/elemental-lf/k8s-crd-resolver',
    author='Lars Fenneberg',
    author_email='lf@elemental.net',
    license='Apache-2.0',
    install_requires=requirements,
    packages=['k8s_crd_resolver'],
    include_package_data=True,
    entry_points="""
        [console_scripts]
            k8s-crd-resolver = k8s_crd_resolver:main
    """,
)
