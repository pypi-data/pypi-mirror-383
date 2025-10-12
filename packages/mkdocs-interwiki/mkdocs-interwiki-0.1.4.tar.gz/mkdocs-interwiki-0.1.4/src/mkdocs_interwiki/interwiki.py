from __future__ import annotations
import re
import uuid
from typing import Dict, Any, Tuple, List
from urllib.parse import quote
from markdown import Extension
from markdown.preprocessors import Preprocessor
from markdown.inlinepatterns import InlineProcessor
from markdown.postprocessors import Postprocessor
from xml.etree.ElementTree import Element

# Preprocessor regex: fast, non-verbose
PRE_IW_RE = re.compile(r"\[\[([A-Za-z0-9_\-]+)>([^\]|]+?)(?:\|([^\]]+))?\]\]")

class InterWikiPreprocessor(Preprocessor):
    """
    Replaces [[prefix>target|label]] with placeholders BEFORE block parsing (e.g., tables),
    so '|' won't be treated as a column separator.
    """
    def __init__(self, md, store: Dict[str, Tuple[str, str, str]]):
        super().__init__(md)
        self.store = store

    def run(self, lines: List[str]) -> List[str]:
        out = []
        for line in lines:
            def repl(m):
                prefix = (m.group(1) or "").strip()
                target = (m.group(2) or "").strip()
                label  = (m.group(3) or "").strip()
                key = f"IW-{uuid.uuid4().hex}"
                self.store[key] = (prefix, target, label)
                return key
            out.append(PRE_IW_RE.sub(repl, line))
        return out


class InterWikiPattern(InlineProcessor):
    """
    Converts placeholders to <a> elements, optionally prefixed with an emoji span.
    """
    def __init__(
        self,
        pattern: str,
        maps: Dict[str, str],
        extra: Dict[str, Any],
        store: Dict[str, Tuple[str, str, str]],
        emoji_default: str | None = None,
        emoji_map: Dict[str, str] | None = None,
        emoji_position: str = "before"  # "before" | "after" | "none"
    ):
        super().__init__(pattern)
        self.maps = maps or {}
        self.extra = extra or {}
        self.store = store
        self.emoji_default = emoji_default or ""
        self.emoji_map = emoji_map or {}
        self.emoji_position = emoji_position

    def _resolve_emoji(self, prefix: str) -> str:
        return self.emoji_map.get(prefix, self.emoji_default)

    def handleMatch(self, m, data):
        key = m.group('key')
        if key not in self.store:
            return None, m.start(0), m.end(0)

        prefix, target_raw, label = self.store.pop(key)

        if prefix not in self.maps:
            return None, m.start(0), m.end(0)

        template = self.maps[prefix]
        target_encoded = quote(target_raw, safe="/:@()!$*,;=+-._~")

        fmt_vars = dict(self.extra)
        fmt_vars["target"] = target_encoded

        try:
            href = template.format(**fmt_vars)
        except KeyError:
            return None, m.start(0), m.end(0)

        # Build the anchor
        a = Element('a')
        a.set('href', href)
        a.text = label if label else target_raw

        # Optionally add an emoji wrapper
        emoji = self._resolve_emoji(prefix).strip()
        if self.emoji_position == "none" or not emoji:
            return a, m.start(0), m.end(0)

        # Wrap in a span so we can put emoji before/after
        wrapper = Element('span')
        wrapper.set('class', 'interwiki-link')

        if self.emoji_position == "before":
            em = Element('span')
            em.set('class', 'interwiki-emoji')
            em.text = emoji + " "
            wrapper.append(em)
            wrapper.append(a)
        elif self.emoji_position == "after":
            wrapper.append(a)
            em = Element('span')
            em.set('class', 'interwiki-emoji')
            em.text = " " + emoji
            wrapper.append(em)
        else:
            # Fallback: no wrapper decoration
            return a, m.start(0), m.end(0)

        return wrapper, m.start(0), m.end(0)


class InterWikiCleanup(Postprocessor):
    """
    If any placeholders survive (e.g., unknown prefix), revert them to original [[...]] text.
    """
    def __init__(self, md, store: Dict[str, Tuple[str, str, str]]):
        super().__init__(md)
        self.store = store

    def run(self, text: str) -> str:
        for key, (prefix, target, label) in list(self.store.items()):
            pretty = f"[[{prefix}>{target}" + (f"|{label}]]" if label else "]]")
            text = text.replace(key, pretty)
            self.store.pop(key, None)
        return text


class InterWikiExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            'maps':  [{}, 'Map of prefixes to URL templates'],
            'extra': [{}, 'Extra template variables'],
            'preprocess': [True, 'Replace interwiki with placeholders before block parsing'],
            # NEW: emoji configuration
            'emoji_default': ["", 'Default emoji for all interwiki links (Unicode or shortcode)'],
            'emoji_map':     [{}, 'Per-prefix emoji mapping, e.g. {"gh": "🔗"}'],
            'emoji_position': ["before", 'Position of emoji: "before", "after", or "none"'],
        }
        super().__init__(**kwargs)
        self._maps  = self.getConfig('maps') or {}
        self._extra = self.getConfig('extra') or {}
        self._store: Dict[str, Tuple[str, str, str]] = {}

        self._emoji_default = self.getConfig('emoji_default') or ""
        self._emoji_map     = self.getConfig('emoji_map') or {}
        self._emoji_position= self.getConfig('emoji_position') or "before"

        self._pattern: InterWikiPattern | None = None
        self._pre: InterWikiPreprocessor | None = None

    def set_extra(self, extra: Dict[str, Any] | None):
        self._extra = extra or {}
        if self._pattern is not None:
            self._pattern.extra = self._extra

    def extendMarkdown(self, md):
        if self.getConfig('preprocess'):
            self._pre = InterWikiPreprocessor(md, self._store)
            md.preprocessors.register(self._pre, 'interwiki_pre', 18)

        placeholder_re = r"(?P<key>IW\-[0-9a-f]{32})"
        self._pattern = InterWikiPattern(
            placeholder_re,
            maps=self._maps,
            extra=self._extra,
            store=self._store,
            emoji_default=self._emoji_default,
            emoji_map=self._emoji_map,
            emoji_position=self._emoji_position,
        )
        md.inlinePatterns.register(self._pattern, 'interwiki', 175)
        md.postprocessors.register(InterWikiCleanup(md, self._store), 'interwiki_cleanup', 5)
