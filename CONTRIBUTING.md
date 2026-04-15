# Contributing to JinjaReportPy

Thank you for your interest in contributing! This guide will help you get started.

## How to Contribute

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Commit** your changes: `git commit -m "feat: add your feature"`
4. **Push** to your fork: `git push origin feature/your-feature`
5. **Open** a Pull Request against `main`

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/JinjaReportPy.git
cd JinjaReportPy

# Install dependencies (using uv)
pip install uv
uv sync --all-extras

# Or with pip
pip install -e ".[dev,all]"
```

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) conventions
- Use type hints for function signatures
- Line length: 100 characters max
- See [python-development.instructions.md](.github/instructions/python-development.instructions.md) for detailed conventions

### Linting

```bash
ruff check .
```

### Testing

Run the test suite before submitting a PR:

```bash
uv run pytest -v --tb=short
```

## Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation changes
- `refactor:` — Code refactoring (no feature or fix)
- `test:` — Adding or updating tests
- `chore:` — Maintenance tasks

Examples:
- `feat: add CSV export support`
- `fix: correct page numbering in multi-page reports`
- `docs: update installation instructions`

## Reporting Issues

- **Bug reports**: Use the [Bug Report](https://github.com/jrodriguezgar/JinjaReportPy/issues/new?template=bug_report.yml) template
- **Feature requests**: Use the [Feature Request](https://github.com/jrodriguezgar/JinjaReportPy/issues/new?template=feature_request.yml) template

## Pull Request Guidelines

- Fill out the PR template completely
- Reference related issues (`Closes #123`)
- Add tests for new features
- Update documentation if needed
- Ensure all CI checks pass

## Code of Conduct

By participating, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Contact

- **Author**: [DatamanEdge](https://github.com/DatamanEdge)
- **Email**: [jrodriguezga@outlook.com](mailto:jrodriguezga@outlook.com)
- **LinkedIn**: [Javier Rodriguez](https://es.linkedin.com/in/javier-rodriguez-ga)