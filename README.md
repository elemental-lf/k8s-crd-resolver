# Kubernetes CRD Resolver

Since version 1.11 Kubernetes supports validation of custom resource definitions against an OpenAPI version 3 
schema. To make these schemata self-contained Kubernetes does not support referencing other components via 
the reference  object `$ref`. But this is often desirable, for example to reference components from the
Kubernetes schema or to consolidate repeated parts inside the schema  itself.

To overcome this limitation one solution is to resolve these references before installing the CRD. So this little
script will take a custom resource definition (both `v1beta1` and `v1` are supported) and will resolve any references.
It uses resolving validator of [Prance](https://pypi.org/project/prance/) to do the actual work. Several kinds of
references are supported:

* Local files: `foo/bar/example.json` (relative) and `/foo/bar/example.json` (absolute)
* URLs: `http://example.com/example.json#/foo/bar`
* Python resources: `python://k8s_crd_resolver/schemata/k8s-1.13.4.json#/definitions/io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta`

Examples are included in the `examples` directory. These are taken from the
[Ceph OSD Operator](https://github.com/elemental-lf/ceph-osd-operator/) project.

## Installation

To install `k8s-crd-resolver`:

```bash
pip install git+http://github.com/elemental-lf/k8s-crd-resolver
```

It is recommended to install `k8s-crd-resolver` into a virtual environment. It has only 
been tested with Python 3.

## Calling `k8s-crd-resolver`

To invoke `k8s-crd-resolver` simply supply it with a source and destination file:

```bash
k8s-crd-resolver $SOURCE_FILE $DESTINATION_FILE
```

`k8s-crd-resolver` is able to read JSON and YAML formatted files and will write a YAML formatted file. Each CRD must 
be in its own file. To facilitate the use in pipelines `k8s-crd-resolver` will read from standard input if the source
filename is `-`. And it will write to standard output if the destination filename is `-`.

Kubernetes has a size limit on objects of one megabyte which also affects CRDs. It can easily be reached if the CRD
contains references to other large Kubernetes objects as all attributes in the official schemata are well documented.
`k8s-crd-resolver` has a command line option to remove these descriptions to reduce the size of the resulting CRD:
`--remove-descriptions` or `-r`.

## Patching the resolved CRD

For dealing with validation errors when loading the generated CRDs into certain Kubernetes versions `k8s-crd-resolver`
supports applying a JSON patch on top of the resolved CRD to fix up these problems. See
https://github.com/kubernetes/kubernetes/issues/91395 and related issues for a discussion of the details.

Example patches for fixing up a CRD containing a reference to the Kubernetes `Pod` object:

* This is for a `v1beta1` CRD which references a`Pod` at `spec.podTemplate`:

```json
[
  {"op": "remove", "path": "/spec/validation/openAPIV3Schema/properties/spec/properties/podTemplate/properties/spec/properties/initContainers/items/properties/ports/x-kubernetes-list-map-keys"},
  {"op": "remove", "path": "/spec/validation/openAPIV3Schema/properties/spec/properties/podTemplate/properties/spec/properties/initContainers/items/properties/ports/x-kubernetes-list-type"},
  {"op": "remove", "path": "/spec/validation/openAPIV3Schema/properties/spec/properties/podTemplate/properties/spec/properties/containers/items/properties/ports/x-kubernetes-list-map-keys"},
  {"op": "remove", "path": "/spec/validation/openAPIV3Schema/properties/spec/properties/podTemplate/properties/spec/properties/containers/items/properties/ports/x-kubernetes-list-type"}
]
```

* And this is the same patch for the `v1` version of the same CRD:

```json
[
  {"op": "add", "path": "/spec/versions/0/schema/openAPIV3Schema/properties/spec/properties/podTemplate/properties/spec/properties/initContainers/items/properties/ports/items/properties/protocol/default", "value": "TCP"},
  {"op": "add", "path": "/spec/versions/0/schema/openAPIV3Schema/properties/spec/properties/podTemplate/properties/spec/properties/containers/items/properties/ports/items/properties/protocol/default", "value": "TCP"}
]
```

See the `examples` directory for the complete examples.

## Referencing Kubernetes schemata

`k8s-crd-resolver` includes schemata for a range of Kubernetes versions which can directly by used in CRDs
without incurring additional external dependencies:

* Kubernetes 1.12.3 schema : `python://k8s_crd_resolver/schemata/k8s-1.12.3.json`
* Kubernetes 1.12.10 schema: `python://k8s_crd_resolver/schemata/k8s-1.12.10.json`
* Kubernetes 1.13.4 schema : `python://k8s_crd_resolver/schemata/k8s-1.13.4.json`
* Kubernetes 1.13.8 schema : `python://k8s_crd_resolver/schemata/k8s-1.13.8.json`
* Kubernetes 1.14.4 schema : `python://k8s_crd_resolver/schemata/k8s-1.14.4.json`
* Kubernetes 1.15.3 schema : `python://k8s_crd_resolver/schemata/k8s-1.15.3.json`
* Kubernetes 1.16.7 schema : `python://k8s_crd_resolver/schemata/k8s-1.16.7.json`
* Kubernetes 1.17.3 schema : `python://k8s_crd_resolver/schemata/k8s-1.17.3.json`
* Kubernetes 1.20.7 schema : `python://k8s_crd_resolver/schemata/k8s-1.20.7.json`
* Kubernetes 1.21.1 schema : `python://k8s_crd_resolver/schemata/k8s-1.21.1.json`
* Kubernetes 1.22.8 schema : `python://k8s_crd_resolver/schemata/k8s-1.22.8.json`
* Kubernetes 1.23.5 schema : `python://k8s_crd_resolver/schemata/k8s-1.23.5.json`
* Kubernetes 1.24.6 schema : `python://k8s_crd_resolver/schemata/k8s-1.24.6.json`
* Kubernetes 1.25.2 schema : `python://k8s_crd_resolver/schemata/k8s-1.25.2.json`

But it is also possible to reference external schemata of course. This example directly references 
a schema in the official Kubernetes repository: 

`https://raw.githubusercontent.com/kubernetes/kubernetes/v1.15.1/api/openapi-spec/swagger.json`

## Other projects

I've found some other projects which do something similar.  All of them are
written in Go and work directly with the Go data structures.

* https://github.com/kubeflow/crd-validation
* https://github.com/ant31/crd-validation
* https://github.com/kubernetes-sigs/controller-tools
