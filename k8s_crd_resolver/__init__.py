#!/usr/bin/env python3
import argparse
import sys
from io import SEEK_SET
from tempfile import NamedTemporaryFile

from prance import ResolvingParser
import ruamel.yaml

OPENAPI_V3_SKELETON = """
openapi: 3.0.0
info:
  version: v1
  title: CRD
paths: {}
components:
  schemas:
    crd_schema:
"""

# Kubernetes 1.15 introduces the concept of structural schemata with some OpenAPI extensions.
# Exclude these extensions from pruning as they can used by CRD authors.
STRUCTURAL_SCHEMA_EXTENSIONS = (
    'x-kubernetes-embedded-resource',
    'x-kubernetes-int-or-string',
    'x-kubernetes-preserve-unknown-fields',
)


def remove_k8s_extentions(schema):
    if isinstance(schema, dict):
        for k in list(schema.keys()):
            if k.startswith('x-kubernetes-') and k not in STRUCTURAL_SCHEMA_EXTENSIONS:
                del schema[k]
            else:
                remove_k8s_extentions(schema[k])


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, allow_abbrev=False)
    parser.add_argument('source', help='Source ("-" for stdin)')
    parser.add_argument('destination', help='Destination ("-" for stdout)')
    args = parser.parse_args()

    # Load CRD
    if args.source != '-':
        with open(args.source, 'r', encoding='utf-8') as source_f:
            source = ruamel.yaml.load(source_f, Loader=ruamel.yaml.SafeLoader)
    else:
        source = ruamel.yaml.load(sys.stdin, Loader=ruamel.yaml.SafeLoader)

    # Insert schema into OpenAPI specification skeleton
    openapi_spec = ruamel.yaml.load(OPENAPI_V3_SKELETON, Loader=ruamel.yaml.SafeLoader)
    openapi_spec['components']['schemas']['crd_schema'] = source['spec']['validation']['openAPIV3Schema']

    with NamedTemporaryFile('w+', encoding='utf-8', suffix='.yaml') as openapi_spec_f:
        # Write OpenAPI specification to temporary file
        ruamel.yaml.dump(openapi_spec, openapi_spec_f)
        openapi_spec_f.flush()
        openapi_spec_f.seek(0, SEEK_SET)

        # Parse file and resolve references
        parser = ResolvingParser(openapi_spec_f.name, backend='openapi-spec-validator')

    resolved_schema = parser.specification['components']['schemas']['crd_schema']

    # Remove any Kubernetes extensions
    remove_k8s_extentions(resolved_schema)

    # Implant resolved schema into CRD
    source['spec']['validation']['openAPIV3Schema'] = resolved_schema

    if args.destination != '-':
        with open(args.destination, 'w', encoding='utf-8') as destination_f:
            ruamel.yaml.dump(source, destination_f)
    else:
        ruamel.yaml.dump(source, sys.stdout)
