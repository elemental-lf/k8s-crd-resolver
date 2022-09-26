#!/usr/bin/env python3
import argparse

from k8s_crd_resolver import resolve_crd


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, allow_abbrev=False)
    parser.add_argument('--remove-descriptions',
                        '-r',
                        action='store_true',
                        default=False,
                        help='Remove object descriptions from referenced resources to reduce size')
    parser.add_argument('--jsonpatch', '-j', nargs='?', default=None, help='JSON patch to apply on the resolved CRD')
    parser.add_argument('source', help='Source ("-" for stdin)')
    parser.add_argument('destination', help='Destination ("-" for stdout)')
    args = parser.parse_args()

    resolve_crd(
        args.source,
        args.destination,
        jsonpatch=args.jsonpatch,
        remove_descriptions=args.remove_descriptions,
    )
