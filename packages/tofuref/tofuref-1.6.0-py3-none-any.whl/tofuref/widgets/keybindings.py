from textual.binding import Binding

VIM_OPTION_LIST_NAVIGATE = [
    Binding("j", "cursor_down", "Down", show=False),
    Binding("k", "cursor_up", "Up", show=False),
    Binding("G", "last", "Last", show=False),
    Binding("ctrl+b", "page_down", "Page Down", show=False),
    Binding("ctrl+f", "page_up", "Page Up", show=False),
]
BOOKMARK = Binding("b", "bookmark", "Bookmark")
CLEAR_CACHE = Binding("ctrl+d", "purge_from_cache", "Purge from cache")
OPEN_GITHUB = Binding("ctrl+g", "open_github", "Open GitHub")
GITHUB_STATS = Binding("ctrl+s", "github_stats", "GitHub Stats")
BACK = Binding("backspace", "back", "Back", show=False)
LEFT_BACK = Binding("left", "back", "Back", show=False)
