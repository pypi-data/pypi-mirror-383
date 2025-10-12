class InterWikiPlugin(BasePlugin):
    config_scheme = (
        ('maps',  config_options.Type(dict, default={})),
        ('extra', config_options.Type(dict, default={})),
        ('preprocess', config_options.Type(bool, default=True)),
        ('emoji_default', config_options.Type(str, default="")),
        ('emoji_map', config_options.Type(dict, default={})),
        ('emoji_position', config_options.Choice(['before','after','none'], default='before')),
    )

    def on_config(self, config, **kwargs):
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

    def on_page_markdown(self, markdown, page, config, files):
        per_page_extra = {}
        if isinstance(page.meta or {}, dict):
            per_page_extra = (page.meta or {}).get('interwiki_extra', {}) or {}
        merged = dict(self.config.get('extra', {}))
        if isinstance(per_page_extra, dict):
            merged.update(per_page_extra)
        self._ext.set_extra(merged)
        return markdown
