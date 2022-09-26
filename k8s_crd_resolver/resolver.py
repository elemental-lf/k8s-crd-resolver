import sys
from io import SEEK_SET
from tempfile import NamedTemporaryFile
from typing import Any, Dict

import ruamel.yaml
from jsonpatch import JsonPatch
from prance import ResolvingParser

OPENAPI_V3_SKELETON = """
openapi: 3.0.0
info:
  version: v1
  title: CRD
paths: {}
components:
  schemas:
    crd_schema: null
"""

# Kubernetes 1.15 and above introduce some custom extensions.
# Exclude these extensions from pruning as they can used by CRD authors.
K8S_SCHEMA_EXTENSIONS = (
    'x-kubernetes-embedded-resource',
    'x-kubernetes-int-or-string',
    'x-kubernetes-preserve-unknown-fields',
    'x-kubernetes-list-map-keys',
    'x-kubernetes-list-type',
    'x-kubernetes-map-type',
    'x-kubernetes-validator',
)


def remove_k8s_extentions(schema: Dict[str, Any]) -> None:
    if isinstance(schema, dict):
        for k in list(schema.keys()):
            if k.startswith('x-kubernetes-') and k not in K8S_SCHEMA_EXTENSIONS:
                del schema[k]
            else:
                remove_k8s_extentions(schema[k])


# This function only removes descriptions that originate in included references.
# It will leave description supplied in the CRD alone.
def remove_k8s_descriptions(schema: Dict[str, Any], source_schema: Dict[str, Any]) -> None:
    if isinstance(schema, dict):
        for k in list(schema.keys()):
            if isinstance(source_schema, dict) and k in source_schema:
                remove_k8s_descriptions(schema[k], source_schema[k])
            else:
                if k == 'description':
                    del schema[k]
                else:
                    remove_k8s_descriptions(schema[k], None)


def parse_and_resolve(schema: Dict[str, Any], *, remove_desciptions: bool = False) -> Dict[str, Any]:
    # Insert schema into OpenAPI specification skeleton
    openapi_spec = ruamel.yaml.load(OPENAPI_V3_SKELETON, Loader=ruamel.yaml.SafeLoader)
    openapi_spec['components']['schemas']['crd_schema'] = schema

    with NamedTemporaryFile('w+', encoding='utf-8', suffix='.yaml') as openapi_spec_f:
        # Use default_flow_style=False to always force block-style for collections, otherwise ruamel.yaml's C parser
        # has problems parsing results like "collection: {$ref: ...}".
        ruamel.yaml.dump(openapi_spec, openapi_spec_f, default_flow_style=False)
        openapi_spec_f.flush()
        openapi_spec_f.seek(0, SEEK_SET)

        # Parse file and resolve references
        parser = ResolvingParser(openapi_spec_f.name, backend='openapi-spec-validator')

    resolved_schema = parser.specification['components']['schemas']['crd_schema']

    # Remove any Kubernetes extensions
    remove_k8s_extentions(resolved_schema)

    # Remove descriptions if requested
    if remove_desciptions:
        remove_k8s_descriptions(resolved_schema, schema)

    return resolved_schema


def resolve_crd(source: str, destination: str, *, jsonpatch: str = None, remove_descriptions: bool = False) -> None:
    # Load CRD
    if source != '-':
        with open(source, 'r', encoding='utf-8') as source_f:
            source = ruamel.yaml.load(source_f, Loader=ruamel.yaml.SafeLoader)
    else:
        source = ruamel.yaml.load(sys.stdin, Loader=ruamel.yaml.SafeLoader)

    # Load JSON patch (if any)
    jsonpatch = None
    if jsonpatch:
        with open(jsonpatch, 'r', encoding='utf-8') as jsonpatch_f:
            jsonpatch = JsonPatch.from_string(jsonpatch_f.read())

    if source['kind'] != 'CustomResourceDefinition':
        raise TypeError('Input file is not a CustomResourceDefinition.')

    if source['apiVersion'] == 'apiextensions.k8s.io/v1beta1':
        resolved_schema = parse_and_resolve(source['spec']['validation']['openAPIV3Schema'],
                                            remove_desciptions=remove_descriptions)
        source['spec']['validation']['openAPIV3Schema'] = resolved_schema
    elif source['apiVersion'] == 'apiextensions.k8s.io/v1':
        for version in source['spec']['versions']:
            resolved_schema = parse_and_resolve(version['schema']['openAPIV3Schema'],
                                                remove_desciptions=remove_descriptions)
            version['schema']['openAPIV3Schema'] = resolved_schema
    else:
        raise TypeError('Unsupported CRD version {}'.format(source['version']))

    if jsonpatch:
        jsonpatch.apply(source, in_place=True)

    if destination != '-':
        with open(destination, 'w', encoding='utf-8') as destination_f:
            ruamel.yaml.dump(source, destination_f, default_flow_style=False)
    else:
        ruamel.yaml.dump(source, sys.stdout, default_flow_style=False)
