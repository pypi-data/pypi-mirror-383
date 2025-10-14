# misc_tooling

A collection of simple, reusable Python utilities for file and string manipulation. This package provides convenient wrappers around common filesystem operations and a Java-like StringBuilder for efficient string construction and editing.

## Features

### File Tools (`file_tools.py`)
- **File existence check**: Quickly check if a file exists.
- **Get full path**: Resolve relative paths to absolute paths.
- **Read file**: Read file contents safely, with error handling.
- **Write file**: Write data to files, with directory creation if needed.
- **Delete file/folder**: Remove files or folders, with success indication.
- **Make file/folder**: Create files or folders, including parent directories.

### String Builder (`string_builder.py`)
- **Efficient string construction**: Append, replace, drop, and render strings incrementally.
- **Drop/replace by value or index**: Remove or replace strings by value or position.
- **Scrub all instances**: Remove all occurrences of a substring.
- **Consistent formatting**: Handles spaces and punctuation for clean output.

## Installation

Clone the repository and install dependencies (if any):

```bash
# Clone the repo
$ git clone <your-repo-url>
$ cd misc_tooling

# (Optional) Set up a virtual environment
$ python -m venv venv
$ source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with Poetry (recommended)
$ poetry install
```

## Usage

### File Tools Example
```python
from src.misc_tooling.file_tools import (
    file_exists, get_full_path, read_file, write_file, write_file_all,
    delete_file, delete_folder, make_file, make_folder
)

# Check if a file exists
print(file_exists('test.txt'))

# Get absolute path
print(get_full_path('test.txt'))

# Read and write files
write_file('test.txt', 'Hello, world!')
print(read_file('test.txt'))

# Create all parent folders and write
write_file_all('folder/subfolder/test.txt', 'Data')

# Delete file and folder
delete_file('test.txt')
delete_folder('folder/subfolder')

# Make file/folder
make_file('newfile.txt')
make_folder('newfolder')
```

### StringBuilder Example
```python
from src.misc_tooling.string_builder import StringBuilder

sb = StringBuilder("Hello", "world")
sb.push("from", "Python")
print(sb.render())  # Output: Hello world from Python

sb.replace("world", "there")
print(sb.render())  # Output: Hello there from Python

sb.drop_string("Hello")
print(sb.render())  # Output: there from Python

sb.replace_at_index(1, "everyone")
print(sb.render())  # Output: there everyone Python

sb.reset()
print(sb.render())  # Output: (empty string)
```

## API Reference

### File Tools
- `file_exists(file_path) -> bool`: Returns whether the file exists.
- `get_full_path(file_path: str) -> str`: Returns the absolute path.
- `read_file(file_path: str) -> str`: Reads file contents as a string.
- `write_file(file_path, file_data) -> bool`: Writes data to a file.
- `write_file_all(file_path, file_data)`: Creates parent directories and writes data.
- `delete_file(file_path) -> bool`: Deletes a file.
- `delete_folder(folder_path) -> bool`: Deletes a folder.
- `make_folder(folder_path) -> bool`: Creates a folder.
- `make_file(file_path: str) -> bool`: Creates an empty file.

### StringBuilder
- `StringBuilder(*inputs)`: Initialize with any number of strings.
- `push(*inputs)`: Add strings to the builder.
- `render() -> str`: Get the built string.
- `reset()`: Clear the builder.
- `drop_string(dropped)`: Remove a string from memory.
- `scrub_string(value)`: Remove all instances of a string.
- `replace(value_replaced, replacement)`: Replace all matching strings.
- `replace_at_index(index, value)`: Replace string at a specific index.

## Testing

Unit tests are provided in the `tests/` directory. Run them with:

```bash
$ poetry run pytest
```

## License

MIT License

## Contributing

Pull requests and suggestions are welcome! Please open an issue or submit a PR.

## Contact

For questions or feedback, open an issue on GitHub.
