# coding=utf-8
# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import mimetypes
import sys


if sys.version_info >= (3, 13):
    def guess_file_mime_type(file_path):
        # type: (str) -> str
        mime_type, _ = mimetypes.guess_file_type(file_path)
        return mime_type or 'application/octet-stream'
else:
    def guess_file_mime_type(file_path):
        # type: (str) -> str
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'