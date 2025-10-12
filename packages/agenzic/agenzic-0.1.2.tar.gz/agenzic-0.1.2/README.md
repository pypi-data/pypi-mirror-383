# Agenzic

**Agenzic** is a terminal-based AI assistant for developers. It streamlines developer workflows by providing AI-powered commit messages, code/file summarization, pull request reviews, documentation generation, and unit test suggestions — all from the command line.

---

## Features

* **AI Commit Assistant**
  Generate clean, conventional commit messages from staged Git changes. Supports multiple options and allows editing before committing.

* **Code/File Summarizer**
  Summarize files or entire codebases to quickly understand legacy code or onboard new developers.

* **AI PR / Code Reviewer**
  Review staged Git changes or specific code files. Provides suggestions for security, style, and possible bugs.

* **Documentation Generator**
  Generate docstrings or README drafts for individual files or entire projects.

* **Test Case Generator**
  Suggest unit tests for your functions based on code content.

* **Version & Environment Info**
  Quickly display the current version of Agenzic along with relevant environment information.

* **Help & Usage Guidance**
  Built-in help command provides a concise overview of commands and usage examples.

---

## Installation

```bash
pip install agenzic
```

> **Note:** Agenzic requires an OpenAI API key. Set it as an environment variable:

```
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=openai_model_name_here
```

---

## Usage

```bash
# Generate AI commit messages for staged changes
agenzic commit

# Summarize a file
agenzic summarize -f myscript.py

# Code Review of a specific file
agenzic review -f myscript.py

# Generate documentation
agenzic docgen -f myscript.py
agenzic docgen -d folder/

# Generate code file
agenzic codegen 'write a python code' -f abc.py

# Generate unit tests for a file
agenzic tests -f myscript.py

# Ask AI a question about file or dir
agenzic ask "Your Question"
agenzic ask "Your Question" -f app.py
agenzic ask "Your Question" -d folder/

# Generate project tree with custom depth (1=top-level only, 2=one level deep, etc.) (default=2)
agenzic projtree
agenzic projtree -d folder/
agenzic projtree -d folder/ -l 3

# Debug inspector: show environment, config, PATH, plugins, Python version.
agenzic inspect

# Show version and environment info
agenzic version

# Show project information
agenzic about

# Display help
agenzic help
```

---

## Project Structure

```
agenzic/
├── agenzic/                # Python package
│   ├── __init__.py
│   ├── __main__.py         # CLI entrypoint
│   ├── commands/           # Individual commands (commit, summarize, review, etc.)
│   └── utils/              # Utility functions (API key, helpers)
├── pyproject.toml           # Project configuration
├── README.md               # This file
└── LICENSE                 # License file
```

---

## License

Agenzic is licensed under the [MIT License](LICENSE).

---

## Contributing

Contributions are welcome!

* Fork the repository
* Create a feature branch (`git checkout -b feature/my-feature`)
* Commit your changes (`git commit -am 'Add feature'`)
* Push to the branch (`git push origin feature/my-feature`)
* Open a Pull Request

---
