# Kubernetes CRD Resolver

Since version 1.11 Kubernetes supports validation of custom resource definitions 
against an OpenAPI version 3 schema. To make these schemata self-contained 
Kubernetes does not support referencing other components via the reference 
object `$ref`. But this is often desirable, for example to reference components 
from  the Kubernetes schema or to consolidate repeated parts inside the schema 
itself.

To overcome this limitation one workaround is to resolve these references before
installing the CRD. So this little script will take a custom resource definition 
and will resolve any references. It uses [Prance](https://pypi.org/project/prance/)'s
resolving validator to do the work. Several kinds of references are support:

* Local files: `foo/bar/example.json` (relative) and `/foo/bar/example.json` (absolute)
* URLs: `http://example.com/example.json#/foo/bar`
* Python resources: `python://k8s_crd_resolver/schemata/k8s-1.13.4.json#/definitions/io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta`

More information can be found in this section of the Prance documentation [A Note on JSON References](https://github.com/jfinkhaeuser/prance#a-note-on-json-references)
and in the following section on [Extensions](https://github.com/jfinkhaeuser/prance#extensions). And there is also the [JSON reference specification](https://tools.ietf.org/html/draft-pbryan-zyp-json-ref-03) itself.

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

`k8s-crd-resolver` can read JSON and YAML formatted files and will write a YAML formatted file.
To facilitate the use in pipelines `k8s-crd-resolver` will read from standard input if
the source filename is `-`. And will write to standard output if the destination filename is `-`.

An example CRD is included in the `example` subdirectory.

## Referencing Kubernetes schemata

`k8s-crd-resolver` comes with included schemata which you can directly reference from your CRD:

* Kubernetes 1.12.3 schema : `python://k8s_crd_resolver/schemata/k8s-1.12.3.json`
* Kubernetes 1.12.10 schema: `python://k8s_crd_resolver/schemata/k8s-1.12.10.json`
* Kubernetes 1.13.4 schema : `python://k8s_crd_resolver/schemata/k8s-1.13.4.json`
* Kubernetes 1.13.8 schema : `python://k8s_crd_resolver/schemata/k8s-1.13.8.json`
* Kubernetes 1.14.4 schema : `python://k8s_crd_resolver/schemata/k8s-1.14.4.json`

It is also possible to directly reference a schema in the Kubernetes source
repository:

`https://raw.githubusercontent.com/kubernetes/kubernetes/v1.15.1/api/openapi-spec/swagger.json`

## Other projects

I've found two other project which do something similar. Both are written in Go and work directly with the
Go data structures.

* https://github.com/kubeflow/crd-validation
* https://github.com/ant31/crd-validation
