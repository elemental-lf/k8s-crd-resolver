try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='k8s-crd-resolver',
    version='0.12.0',
    description='Kubernetes CRD Resolver',
    url='http://github.com/elemental-lf/k8s-crd-resolver',
    author='Lars Fenneberg',
    author_email='lf@elemental.net',
    license='Apache-2.0',
    install_requires=[
        'ruamel.yaml>0.17,<0.18', 'prance[osv]>=0.21.8.0', 'openapi-spec-validator<0.5.0', 'jsonpatch>=1.32,<2'
    ],
    packages=['k8s_crd_resolver'],
    include_package_data=True,
    entry_points="""
        [console_scripts]
            k8s-crd-resolver = k8s_crd_resolver.cli:main
    """,
)
