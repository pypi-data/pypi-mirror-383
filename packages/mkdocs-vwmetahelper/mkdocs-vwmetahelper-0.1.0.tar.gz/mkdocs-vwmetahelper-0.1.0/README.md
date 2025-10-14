# mkdocs-vwmetahelper (classic setup.py)

A tiny MkDocs plugin that exposes:

- `get_meta(id)` — fetch another page's front matter (and computed URL) by `id`
- `call_macro(file, name, **kwargs)` — call a macro defined in a `*.j2` include file

## Build & publish
```bash
python -m pip install --upgrade build twine wheel setuptools
python setup.py sdist bdist_wheel
twine upload dist/*
```

## Usage
```yaml
plugins:
  - search
  - vwmetahelper:
      include_dir: docs/_includes
```
