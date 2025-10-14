# meow

**meow** is a terminal markdown viewer written in python and inspired by [glow](https://github.com/charmbracelet/glow). it's just a `cat` with [Rich](https://github.com/Textualize/rich), though, no file browsing! (yet?)

## features

- uses `LS_COLORS` — respects your terminal colorscheme for all you (us) ricers
- syntax highlighting in fenced codeblocks via Pygments
- styled lists, headers, blockquotes, and **bold** and *italics*
- `git log`-like, terminal height-aware paging

### gripes / future

- [ ] make the checkboxes cuter! glow-style `[ ]` / `[-]` / `[x]`
- [ ] tables...

## installation

install directly from [pypi](https://pypi.org/project/meow-md):

```bash
# run directly without installing
uvx --from meow-md meow

# or install globaly
uv tool install meow-md

# or more traditionally
pip install --user meow-md  # if you use pip
pipx install meow-md        # if you use pipx
```

or build from source:

```bash
git clone https://codeberg.org/sailorfe/meow.git
cd meow
uv run -m meow.__main__                 # run directly
# or
uv sync && uv run -m meow.__main__      # for development
```

## usage

```bash
meow README.md
```
