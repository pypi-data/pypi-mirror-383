from __future__ import annotations
from typing import Dict, Any

# ✅ These imports were missing
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page

from .interwiki import InterWikiExtension


class InterWikiPlugin(BasePlugin):
    """
    MkDocs plugin wrapper for the InterWikiExtension.
    """

    config_scheme = (
        ('maps', config_options.Type(dict, default={})),
        ('extra', config_options.Type(dict, default={})),
        ('preprocess', config_options.Type(bool, default=True)),
        ('emoji_default', config_options.Type(str, default="")),
        ('emoji_map', config_options.Type(dict, default={})),
        ('emoji_position', config_options.Choice(['before', 'after', 'none'], default='before')),
    )

    def on_config(self, config: MkDocsConfig, **kwargs):
        """
        Register our Markdown extension with MkDocs.
        """
        self._ext = InterWikiExtension(
            maps=self.config.get('maps', {}),
            extra=self.config.get('extra', {}),
            preprocess=self.config.get('preprocess', True),
            emoji_default=self.config.get('emoji_default', ""),
            emoji_map=self.config.get('emoji_map', {}),
            emoji_position=self.config.get('emoji_position', 'before'),
        )
        config.markdown_extensions.append(self._ext)
        return config

    def on_page_markdown(self, markdown: str, page: Page, config: MkDocsConfig, files):
        """
        Allow per-page overrides via front matter:
          interwiki_extra:
            repo: "custom/repo"
        """
        per_page_extra: Dict[str, Any] = {}
        if isinstance(page.meta, dict):
            per_page_extra = page.meta.get('interwiki_extra', {}) or {}

        merged = dict(self.config.get('extra', {}))
        if isinstance(per_page_extra, dict):
            merged.update(per_page_extra)

        # Update active extension variables before this page renders
        self._ext.set_extra(merged)
        return markdown
