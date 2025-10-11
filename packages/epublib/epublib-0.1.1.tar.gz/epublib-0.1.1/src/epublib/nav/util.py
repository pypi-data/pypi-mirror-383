from dataclasses import dataclass, field

import bs4
from bs4.element import NamespacedAttribute

from epublib.exceptions import warn
from epublib.util import attr_to_str, parse_int

epub_type = NamespacedAttribute(
    prefix="epub",
    name="type",
    namespace="http://www.idpf.org/2007/ops",
)


def detect_page(tag: bs4.Tag) -> int | None:
    page = None
    if tag.string:
        page = parse_int(tag.string)
        if page is not None:
            return page

    for attr in "title", "aria-label", "id", "class":
        if tag.get(attr):
            page = parse_int(attr_to_str(tag[attr]))

            if page is not None:
                return page

    warn(f"Can't determine page number of pagebreak element: {tag}")
    return None


@dataclass
class PageBreakData:
    """
    Data for a page break.

    Args:
        filename: The filename (and optional fragment) of the page break.
        page: The page number.
        label: The label to use for the page in the page list. If not given,
            the page number will be used as label.
    """

    filename: str
    page: int
    label: str = ""

    def __post_init__(self) -> None:
        if not self.label:
            self.label = str(self.page)


@dataclass
class TOCEntryData:
    """
    Data for a table of contents entry.

    Args:
        filename: The filename (and optional fragment) of the entry.
        label: The label to use for the entry in the table of contents.
        id: An optional identifier for the entry.
        children: A list of child entries. Defaults to an empty list.
    """

    filename: str
    label: str
    id: str | None = None
    children: list["TOCEntryData"] = field(default_factory=list)


@dataclass
class LandmarkEntryData:
    """
    Represents a landmark, a special navigation point in an EPUB file.

    Args:
        filename: The filename (and optional fragment) of the landmark.
        label: The label to use for the landmark.
        epub_type: The EPUB type of the landmark, e.g. "toc" or "cover".
    """

    filename: str
    label: str
    epub_type: str
