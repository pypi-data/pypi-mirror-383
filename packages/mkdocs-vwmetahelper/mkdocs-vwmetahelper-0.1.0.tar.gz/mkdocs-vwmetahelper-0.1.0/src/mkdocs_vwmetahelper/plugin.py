import os, io, re, yaml
from mkdocs.plugins import BasePlugin
from jinja2 import Environment, FileSystemLoader

_FRONT_RE = re.compile(r"^\s*---\s*\n(.*?)\n---\s*(?:\n|$)", re.S)

class VWMetaHelperPlugin(BasePlugin):
    """
    MkDocs plugin offering:
      - get_meta(id): fetch another page's front matter + url by id
      - call_macro(file, name, **kwargs): call a Jinja macro from include_dir
    Uses lazy indexing of docs_dir front matter to avoid hook ordering issues.
    """
    config_scheme = (
        ('include_dir', str),
    )

    def on_config(self, config):
        self.docs_dir = config.get('docs_dir', 'docs')
        self.include_dir = self.config.get('include_dir', 'docs/_includes')
        self._index = {}
        self._built = False
        self._jenv = Environment(loader=FileSystemLoader(self.include_dir))
        return config

    def get_meta(self, id_):
        self._ensure_index()
        return self._index.get(id_)

    def call_macro(self, file, name, *args, **kwargs):
        self._ensure_index()
        tpl = self._jenv.get_template(file)
        fn = getattr(tpl.module, name)
        return fn(*args, **kwargs)

    def on_env(self, env, **kwargs):
        env.globals['get_meta'] = self.get_meta
        env.globals['call_macro'] = self.call_macro
        return env

    def on_files(self, files, config):
        self._built = False
        return files

    def _ensure_index(self):
        if self._built:
            return
        self._index = {}
        for root, _, files in os.walk(self.docs_dir):
            for fn in files:
                if not fn.lower().endswith('.md'):
                    continue
                path = os.path.join(root, fn)
                rel = os.path.relpath(path, self.docs_dir)
                try:
                    with io.open(path, 'r', encoding='utf-8') as f:
                        text = f.read()
                except Exception:
                    continue
                m = _FRONT_RE.match(text)
                if not m:
                    continue
                try:
                    meta = yaml.safe_load(m.group(1)) or {}
                except Exception:
                    continue
                pid = meta.get('id')
                if not pid:
                    continue
                url = rel.replace(os.sep, '/')
                if url.endswith('index.md'):
                    url = url[:-8]
                elif url.endswith('.md'):
                    url = url[:-3] + '/'
                self._index[pid] = {**meta, 'url': url, 'path': rel}
        self._jenv.globals.update({
            'get_meta': self.get_meta,
            'call_macro': self.call_macro,
        })
        self._built = True
