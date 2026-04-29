# Publishing

This package is intended for educational integer factorization experiments,
benchmarks, and command-line use. It is not a production cryptography tool and
is not expected to factor RSA challenge numbers quickly.

## Before Publishing

1. Confirm the intended release tag. Package versions are derived from Git tags
   with `setuptools-scm`; there is no static version in `pyproject.toml`.
2. Run the test suite:

   ```bash
   python -m unittest -v
   ```

3. Build source and wheel distributions:

   ```bash
   python -m build
   ```

   Use `python -m build --no-isolation` only for local troubleshooting when the
   isolated build environment is not needed.

4. Check the distributions:

   ```bash
   python -m twine check dist/*
   ```

5. Install the wheel into a clean virtual environment and smoke-test the CLI:

   ```bash
   python -m venv /tmp/fast-factorization-publish-test
   /tmp/fast-factorization-publish-test/bin/python -m pip install dist/fast_factorization-<version>-py3-none-any.whl
   /tmp/fast-factorization-publish-test/bin/fast-factorization 100
   ```

## TestPyPI

This project publishes with PyPI Trusted Publishing from GitHub Actions. Create
a pending trusted publisher in TestPyPI before the first upload:

- URL: https://test.pypi.org/manage/account/publishing/
- Project name: `fast-factorization`
- Owner: `nikiigo`
- Repository: `fast-factorization`
- Workflow name: `publish.yml`
- Environment name: `testpypi`

After the trusted publisher is registered, run the `Publish Python package`
workflow manually in GitHub Actions with `target=testpypi`.

Then install from TestPyPI in a clean environment:

```bash
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps fast-factorization
```

## PyPI

After TestPyPI verification, create a pending trusted publisher in PyPI:

- URL: https://pypi.org/manage/account/publishing/
- Project name: `fast-factorization`
- Owner: `nikiigo`
- Repository: `fast-factorization`
- Workflow name: `publish.yml`
- Environment name: `pypi`

In GitHub repository settings, create the `pypi` environment and require manual
approval before deployment. This prevents an accidental tag push from publishing
without review.

Then publish by pushing a version tag, for example:

```bash
git tag v<version>
git push origin v<version>
```

For example, `v0.1.2` builds and publishes package version `0.1.2`. Builds made
after the latest tag and before the next release tag produce development
versions such as `0.1.2.dev3`.

The workflow also supports manual PyPI publishing with `target=pypi`, but the
tag flow is preferred because it leaves a clear release marker in Git.

## Token Fallback

Trusted Publishing is preferred. If it is unavailable, use API tokens with
`twine`:

```bash
TWINE_USERNAME=__token__ TWINE_PASSWORD=<token> python -m twine upload dist/*
```

Use separate tokens for TestPyPI and PyPI, and prefer project-scoped tokens once
the project exists.
