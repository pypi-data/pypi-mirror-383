# Bowerbirds 🐦

**Bowerbirds** is a Python library that helps you **organize messy AI/ML projects** so they are easier to manage and use with different AI models. Even if you don’t have a model api, it can generate a **ready-to-use JSON file** that works with external AI/ML tools. You can also plug in your favorite model providers like **LiteLLM**.


---

## Features ✨

- Automatically structure your **unstructured AI/ML project**.
- Generate a **ready-to-use JSON file** for external models.
- Optionally integrate with **LiteLLM** or any model provider.
- Simple **CLI** and **Python API** for easy usage.
- Lightweight, modular, and beginner-friendly.

---

## Installation 💻

```bash

pip install bowerbirds
```

---

## Usage

### Python API

```python
from bowerbirds import Bower

# Without a model
revamp = Bower("/path/to/project")
metadata_file = revamp.run()  # Creates metadata.json

# With a LiteLLM model
revamp = Bower("/path/to/project", model_name="gpt-4o-mini")
output = revamp.run()  # Revamped project output from model
```

### CLI

```bash
# Without a model
python -m bowerbirds.cli /path/to/project

# With a model
python -m bowerbirds.cli /path/to/project --model gpt-4o-mini
```

---

## Contributing 🤝

Contributions are welcome! Please open an issue or submit a pull request.

---

## License 📄

MIT
