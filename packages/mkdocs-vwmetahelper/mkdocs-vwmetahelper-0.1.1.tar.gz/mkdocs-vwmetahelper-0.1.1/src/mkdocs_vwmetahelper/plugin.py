# plugin.py
import os, io, re, yaml
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options as c          # ✅ add this
from jinja2 import Environment, FileSystemLoader
import re as _re

_FRONT_RE = _re.compile(r"^\s*---\s*\n(.*?)\n---\s*(?:\n|$)", _re.S)

class VWMetaHelperPlugin(BasePlugin):
    # ✅ use MkDocs config options, not raw types
    config_scheme = (
        ("include_dir", c.Type(str, default="docs/_includes")),
    )

    def on_config(self, config):
        self.docs_dir = config.get("docs_dir", "docs")
        self.include_dir = self.config.get("include_dir")  # already defaulted above
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

    # ✅ match MkDocs event signature (works on 1.5+)
    def on_env(self, env, config, files):
        env.globals["get_meta"] = self.get_meta
        env.globals["call_macro"] = self.call_macro
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
                if not fn.lower().endswith(".md"):
                    continue
                path = os.path.join(root, fn)
                rel = os.path.relpath(path, self.docs_dir)
                try:
                    with io.open(path, "r", encoding="utf-8") as f:
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
                pid = meta.get("id")
                if not pid:
                    continue
                url = rel.replace(os.sep, "/")
                if url.endswith("index.md"):
                    url = url[:-8]
                elif url.endswith(".md"):
                    url = url[:-3] + "/"
                self._index[pid] = {**meta, "url": url, "path": rel}
        self._jenv.globals.update({
            "get_meta": self.get_meta,
            "call_macro": self.call_macro,
        })
        self._built = True
