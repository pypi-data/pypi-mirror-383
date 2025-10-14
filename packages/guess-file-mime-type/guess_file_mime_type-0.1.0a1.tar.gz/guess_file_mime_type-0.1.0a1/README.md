# guess-file-mime-type

A minimal, cross-platform, and cross-version utility to safely guess a file's MIME type.

## Features

- ✅ **NT & POSIX** filesystem support
- ✅ **Uniform API** for different Python versions (2+ and 3.0 - 3.13+)
  - *Standard library* functions like `mimetypes.guess_type()` and `mimetypes.guess_file_type()` **change signature and location** in Python 3.13.
- ✅ Returns sensible default (`application/octet-stream`) for unknown types

## Why?

- Write portable code that works everywhere, forever.

## Installation

```bash
pip install guess-file-mime-type
```

## Usage

```python
# coding=utf-8
from __future__ import print_function
from guess_file_mime_type import guess_file_mime_type

mime_type = guess_file_mime_type('/path/to/image.png')
print(mime_type)  # 'image/png'
```

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).