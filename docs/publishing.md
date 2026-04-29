# Publishing

This package is intended for educational integer factorization experiments,
benchmarks, and command-line use. It is not a production cryptography tool and
is not expected to factor RSA challenge numbers quickly.

## Before Publishing

1. Confirm the package version in `pyproject.toml`.
2. Run the test suite:

   ```bash
   python -m unittest -v
   ```

3. Build source and wheel distributions:

   ```bash
   python -m build --no-isolation
   ```

4. Check the distributions:

   ```bash
   python -m twine check dist/*
   ```

5. Install the wheel into a clean virtual environment and smoke-test the CLI:

   ```bash
   python -m venv /tmp/fast-factorization-publish-test
   /tmp/fast-factorization-publish-test/bin/python -m pip install dist/fast_factorization-0.1.0-py3-none-any.whl
   /tmp/fast-factorization-publish-test/bin/fast-factorization 100
   ```

## TestPyPI

Publish to TestPyPI first:

```bash
python -m twine upload --repository testpypi dist/*
```

Then install from TestPyPI in a clean environment:

```bash
python -m pip install --index-url https://test.pypi.org/simple/ fast-factorization
```

## PyPI

After TestPyPI verification, publish to PyPI:

```bash
python -m twine upload dist/*
```

Use a PyPI API token rather than an account password.
