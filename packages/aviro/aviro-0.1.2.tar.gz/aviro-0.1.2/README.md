# Aviro

A Python package for LLM execution tracking and flow analysis.

## Installation

You can install aviro using pip:

```bash
pip install aviro
```

## Usage

```python
import aviro

# Create a Tropir instance for tracking
tropir = aviro.Tropir(api_key="your-api-key", base_url="https://api.tropir.com")

# Use as a context manager to track LLM calls
with tropir.span("my_llm_workflow"):
    # Your LLM calls will be automatically tracked
    pass

# Or use the Span class directly
span = aviro.Span("my_span", api_key="your-api-key")
with span.track_calls("my_case"):
    # LLM calls tracked here
    pass
```

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/yourusername/aviro.git
cd aviro

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black aviro tests

# Lint code
flake8 aviro tests
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
