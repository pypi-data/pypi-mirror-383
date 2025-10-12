from dj_iconify.util import icon_choices

# Materialize colors (without accent, darken and lighten classes)
COLOURS = [
    ("red", "red"),
    ("pink", "pink"),
    ("purple", "purple"),
    ("deep-purple", "deep-purple"),
    ("indigo", "indigo"),
    ("blue", "blue"),
    ("light-blue", "light-blue"),
    ("cyan", "cyan"),
    ("teal", "teal"),
    ("green", "green"),
    ("light-green", "light-green"),
    ("lime", "lime"),
    ("yellow", "yellow"),
    ("amber", "amber"),
    ("orange", "orange"),
    ("deep-orange", "deep-orange"),
    ("brown", "brown"),
    ("grey", "grey"),
    ("blue-grey", "blue-grey"),
    ("black", "black"),
    ("white", "white"),
    ("transparent", "transparent"),
]

try:
    ICONS = icon_choices("mdi")
except FileNotFoundError:
    # If icons aren't installed yet, set choices to empty list
    ICONS = []


def get_icon_choices():
    """Get icon choices as callable for model fields."""
    return ICONS
