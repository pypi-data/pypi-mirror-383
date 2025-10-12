# mkdocs-interwiki 🧭

DokuWiki-style **InterWiki** links for MkDocs — now with emoji icons!  
Create shorthand cross-site links such as `[[wp>Python|Wikipedia: Python]]` or `[[gh>mkdocs/mkdocs]]`, with configurable emojis like 🔗 or `:interwiki-github:`.

---

## ✨ Features

- ✅ DokuWiki-style syntax: `[[prefix>target|Label]]`
- ✅ Configurable link templates per prefix
- ✅ Optional emoji icons before or after each link
- ✅ Safe to use in Markdown tables (no `|` parsing conflicts)
- ✅ Per-page override of extra variables (via front matter)
- ✅ Works perfectly with **MkDocs Material** and **pymdownx.emoji**

---

## 🚀 Installation

```bash
pip install mkdocs-interwiki
````

Or from source:

```bash
git clone https://github.com/yourname/mkdocs-interwiki.git
cd mkdocs-interwiki
pip install -e .
```

---

## ⚙️ Configuration

In your **`mkdocs.yml`**:

```yaml
plugins:
  - search
  - interwiki:
      maps:
        wp: "https://en.wikipedia.org/wiki/{target}"
        gh: "https://github.com/{target}"
        issue: "https://github.com/{repo}/issues/{target}"
      extra:
        repo: "myorg/myrepo"
      preprocess: true          # (default) prevent '|' from breaking tables
      emoji_default: "🔗"       # shown before every link unless overridden
      emoji_map:
        wp: "📘"
        gh: ":interwiki-github:"
        issue: "🐞"
      emoji_position: before    # before | after | none
```

---

## 🧩 Writing Links

### Basic examples

```markdown
See [[wp>Python|Wikipedia: Python]] and [[gh>mkdocs/mkdocs]].

Open issue [[issue>1234|Bug #1234]].
```

These render as:

> 📘 [Wikipedia: Python](https://en.wikipedia.org/wiki/Python)
> :interwiki-github: [mkdocs/mkdocs](https://github.com/mkdocs/mkdocs)
> 🐞 [Bug #1234](https://github.com/myorg/myrepo/issues/1234)

*(Emoji rendering depends on configuration — see below.)*

---

## 🎨 Emoji options

### 🔹 1. Default emoji

Set a single `emoji_default` to appear before every link.

```yaml
emoji_default: "🔗"
emoji_position: before
```

### 🔹 2. Per-prefix emoji

Use `emoji_map` to assign emojis for specific prefixes.

```yaml
emoji_map:
  wp: "📘"
  gh: ":interwiki-github:"    # uses pymdownx.emoji shortcode
```

### 🔹 3. Emoji position

Place the emoji **before** or **after** the link text:

```yaml
emoji_position: after
```

Result:
`[Wikipedia: Python](...)` 🔗

---

## 🧱 Using in tables

InterWiki links are automatically protected from Markdown’s table parser,
so you can safely use them without escaping the `|` character:

```markdown
| Name | Source |
|------|---------|
| Python | [[wp>Python|Wikipedia]] |
| MkDocs | [[gh>mkdocs/mkdocs|GitHub]] |
```

---

## 🧭 Per-page overrides

You can override variables (like `{repo}`) per page using front matter:

```yaml
---
title: Custom Repo Page
interwiki_extra:
  repo: "other-org/other-repo"
---
```

Then `[[issue>42]]` → `https://github.com/other-org/other-repo/issues/42`.

---

## 💡 Tips for MkDocs Material users

If you want emoji shortcodes like `:interwiki-github:` to render as icons,
enable `pymdownx.emoji` in your `markdown_extensions`:

```yaml
markdown_extensions:
  - pymdownx.emoji:
      emoji_index: !!python/name:materialx.emoji.twemoji
      emoji_generator: !!python/name:materialx.emoji.to_svg
```

Otherwise, use Unicode emojis (`🐙`, `📘`, etc.) which always display.

---

## 🧰 Developer notes

* `maps` defines `{prefix}: {url-template}` pairs; `{target}` is required.
* `extra` provides custom template variables (`{repo}`, `{lang}`, etc.).
* `preprocess` is enabled by default to protect against table parsing.
* The extension runs safely alongside other Markdown extensions.

---

## 🧪 Example preview

```yaml
plugins:
  - interwiki:
      maps:
        gh: "https://github.com/{target}"
        wp: "https://en.wikipedia.org/wiki/{target}"
      emoji_default: "🔗"
      emoji_map:
        gh: ":interwiki-github:"
        wp: "📘"
      emoji_position: before
```

```markdown
- [[gh>mkdocs/mkdocs|MkDocs repo]]
- [[wp>Python|Wikipedia: Python]]
```

Output (Material theme):

> :interwiki-github: [MkDocs repo](https://github.com/mkdocs/mkdocs)
> 📘 [Wikipedia: Python](https://en.wikipedia.org/wiki/Python)

---

## 🧾 License

MIT License © 2025 Your Name

---

## 🗓️ Changelog

### 0.1.3

* Added emoji support (default + per-prefix + position)
* Works with `pymdownx.emoji` or plain Unicode
* Improved safety inside Markdown tables

### 0.1.1

* Fixed “unbalanced parenthesis” regex issue
* Safer per-page variable overrides

### 0.1.0

* Initial release — DokuWiki-style InterWiki links
