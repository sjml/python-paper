PAPER_STATE = {}

# fmt: off
_pandoc_features = [
    "+bracketed_spans",  # let us put attributes on individual spans
    "+raw_tex",          # allow raw TeX commands (like `\noindent{}`)
    "-auto_identifiers", # don't try to link section headings
]
# fmt: on
PANDOC_INPUT_FORMAT = f"markdown{''.join(_pandoc_features)}"
