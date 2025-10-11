"""
Main CLI entrypoint.

Copyright 2025 Vlad Emelianov
"""

import sys


def print_info() -> None:
    """
    Print package info to stdout.
    """
    sys.stdout.write(
        "Type annotations for aiobotocore TranscribeService 2.25.0\n"
        "Version:         2.25.0\n"
        "Builder version: 8.11.0\n"
        "Docs:            https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_transcribe//\n"
        "Boto3 docs:      https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/transcribe.html#transcribeservice\n"
        "Other services:  https://pypi.org/project/boto3-stubs/\n"
        "Changelog:       https://github.com/youtype/mypy_boto3_builder/releases\n"
    )


def print_version() -> None:
    """
    Print package version to stdout.
    """
    sys.stdout.write("2.25.0\n")


def main() -> None:
    """
    Main CLI entrypoint.
    """
    if "--version" in sys.argv:
        print_version()
        return
    print_info()


if __name__ == "__main__":
    main()
