# DEXPI Specificator

**dexpi.specificator** is a Python library and CLI tool that lets you generate DEXPI specifications in Python.  
It can be installed via [PyPI](https://pypi.org/) or [TestPyPI](https://test.pypi.org/) and used either as a library or a command-line tool to convert specification inputs into specification outputs.

---

## Features

- Parse input specification files in the DEXPI format
- Generate DEXPI outputs (XML, JSON, etc.) from those inputs
- Validate specifications against DEXPI schemas
- Tested with automated unit tests to ensure correctness
- Published on PyPI/TestPyPI for easy installation via `pip`

---

## Installation

Install the stable release from **PyPI**:

```bash
pip install dexpi.specificator
```

Install the latest development version from **TestPyPI**:

```bash
pip install --index-url https://test.pypi.org/simple/ dexpi.specificator
```

---

## Usage

### Used in Specification Projects
The Specificator is used to generate the DEXPI Specification in CI/CD Pipelines of GitLab Repositories. 
see https://gitlab.com/dexpi/Specification as the main used Repository 


### CI/CD & Release Process

The project uses GitLab CI/CD for testing and publishing:

1. **Testing**  
   Unit tests run automatically on every commit and merge request. Builds must pass before deployment.

2. **Publish to TestPyPI**  
   Development builds are uploaded to TestPyPI for pre-release testing.

3. **Publish to PyPI**  
   Tagged releases or main branch builds are uploaded to PyPI.  
   API tokens are securely stored in GitLab CI/CD variables.

4. **Versioning**  
   Follows [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH).

---

## Contributing

- Open a merge request with your changes
- Include tests for new functionality or bug fixes
- Follow code review feedback before merging

---

## Issues

Report issues and feature requests in the [GitLab issue tracker](../../issues).

---

## License

This project is licensed under the [LICENSE](LICENSE) file included in the repository.

