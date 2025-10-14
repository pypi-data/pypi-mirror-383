# Corebrum

A basic Python package for demonstration purposes.

## Installation

You can install Corebrum using pip:

```bash
pip install corebrum
```

## Usage

Here's a simple example of how to use Corebrum:

```python
import corebrum

# Get a greeting message
message = corebrum.hello_world()
print(message)  # Output: Hello from Corebrum!

# Add two numbers
result = corebrum.add_numbers(5, 3)
print(result)  # Output: 8

# Get the package version
version = corebrum.get_version()
print(version)  # Output: 0.1.0
```

## Features

- Simple greeting function
- Basic math operations
- Version information

## Development

To set up a development environment:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/corebrum.git
   cd corebrum
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Testing

Run the tests with pytest:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Your Name - your.email@example.com

Project Link: [https://github.com/yourusername/corebrum](https://github.com/yourusername/corebrum)
