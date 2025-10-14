## Nginx Config Lint

CLI tool for linting nginx jinja2 templates from `nginx/dev.conf` and `nginx/pr.conf`

## How to upload to pip

Install `twine`

`python3 -m pip install --upgrade twine`

- Bump version in `pyproject.toml`
- Build Package (`python3 -m build`)
- Upload Package (`python3 -m twine upload dist/*`)
