"""Processing ods (OpenDocument spreadsheets)."""

from __future__ import annotations

import datetime
import functools
import re
from typing import TYPE_CHECKING

from . import Odf, OdfXml

if TYPE_CHECKING:
    from pathlib import Path

    from lxml import etree

__date__ = "2024/08/03 17:16:01 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2020 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"

# Identify hyperlink in formula.
IMDB_HYPERLINK = re.compile(
    r"of:=HYPERLINK\(\s*"
    r'"(?P<url>https?://www.imdb.com/title/tt[0-9]+)'
    r'(?:/?(?:[?]ref_=(?:[a-z]{2}_)+(?:[0-9]{1,3}|[a-z]{1,3})|(?:episodes))?)?"\s*;\s*'
    r'"(?P<name>.+)"\s*\)'
)

# Identify relations to other cells in formulas.
LINKED_CELL = re.compile(
    r"of:=-(:?[-+]?[0-9]*\.?[0-9]*[-+*/])*\[\$?(?P<sheet>'k\&v')"
    r"\.(?P<row>F)(?P<line>[0-9]+)]"
)


class P(OdfXml):
    """Representing a paragraph in a cell."""

    @property
    def text(self) -> str | None:
        """Get text from paragraph.

        Returns:
        str: Whole paragraph text if available.
        """
        res = " ".join(list(self.root.itertext()))
        return res if res.strip() else None


class Cell(OdfXml):
    """Representing a cell in a table row."""

    @property
    def text(self) -> str | None:
        """Return text associated with cell.

        Returns:
        str: Cell text if avaliable.
        """
        if self.root is None:
            return None
        res = self.find("text:p")
        return None if res is None else P(res).text

    @property
    def date(self) -> datetime.date | None:
        """Return date value of cell if available.

        Returns:
        datetime.date: Date value of cell if available.
        """
        val = self.get("office:date-value")
        return (
            None if val is None else datetime.datetime.strptime(val, "%Y-%m-%d").date()  # noqa:DTZ007
        )

    @property
    def value(self) -> str | None:
        """Return value of cell.

        Returns:
        str: Value of cell if available.
        """
        return self.get("office:value")

    @property
    def float(self) -> float | None:
        """Return float value of cell.

        Returns:
        float: ``float`` falue of cell if available.
        """
        return None if self.value is None else float(self.value)

    @property
    def int(self) -> int | None:
        """Return integer value of cell.

        Returns:
        int: ``int`` value if cell if available.
        """
        return None if self.value is None else int(self.value)

    @property
    def url(self) -> str | None:
        """Return URL associated with cell from hyperlink function.

        Returns:
        str: url from ``HYPERLINK`` formula or cell hyperlink.
        """
        s_val: str = self.get("table:formula")
        val = None if s_val is None else IMDB_HYPERLINK.match(s_val)
        return None if val is None else val.group("url")

    @property
    def link(self) -> dict[str, str] | None:
        """Provide Link information.

        This link information is information of values referenced from diffrent tables
        in formula.

        Returns:
           dict: Result of ``re.match.groupdict``. Provided keys are ``sheet``, ``row``,
                 and ``line.``
        """
        dvd_link: str = self.get("table:formula")
        if dvd_link is not None:
            match = LINKED_CELL.match(dvd_link)
            if match is not None:
                return match.groupdict()
        return None


class Row(OdfXml):
    """Representing table row."""

    def __init__(self, elem: etree._Element) -> None:
        """Initalize instance."""
        super().__init__(elem)
        self.content_cell: str = self._attrib_map("table:table-cell")
        self.covered_cell: str = self._attrib_map("table:covered-table-cell")
        self.columns_repeated: str = self._attrib_map("table:number-columns-repeated")

    @functools.cached_property
    def cells(self) -> list[Cell | None]:
        """Provide list of cells in row.

        Empty cells are replaced by ``None``, as are cells covered by merged cells.

        Returns:
        List[Cell]: The cells making up the current row.
        """
        res: list[Cell | None] = []
        for cell in self.root:
            if cell.tag == self.content_cell:
                elem = Cell(cell)
                res.extend(
                    [elem]
                    * (
                        int(elem.get("table:number-columns-repeated"))
                        if self.columns_repeated in cell.attrib
                        else 1
                    )
                )
            elif cell.tag == self.covered_cell:
                elem = Cell(cell)
                res.extend(
                    [None]
                    * (
                        int(elem.get("table:number-columns-repeated"))
                        if self.columns_repeated in cell.attrib
                        else 1
                    )
                )
            else:
                msg = f"Unknown tag {cell.tag}"
                raise NotImplementedError(msg)
        return res


class Table(OdfXml):
    """Representation of spreadsheet table."""

    @functools.cached_property
    def name(self) -> str:
        """Return name attriute of table.

        Returns:
        str: table name.
        """
        return self.get("table:name")

    @functools.cached_property
    def rows(self) -> list[Row]:
        """Return rows in table.

        Returns:
        List[Row]: list of ``Row`` intances.
        """
        return [Row(e) for e in self.findall("table:table-row")]

    @functools.cached_property
    def style_name(self) -> str:
        """Return table style-name.

        I Know of ``ta1`` for ordinary tables, and ``ta2`` for hidden tables.

        Returns:
        str: style name of table.
        """
        return self.get("table:style-name")

    @property
    def hidden(self) -> bool:
        """Return whether table is hidden.

        Returns:
        bool: ``True`` if table is hidden.
        """
        return self.style_name == "ta2"


class Ods(Odf):
    """Processing ODS files."""

    def __init__(self, path: str | Path) -> None:
        """Open ODF spreadsheet file."""
        super().__init__(path)

        self.root = self.find("office:body/office:spreadsheet")

    @functools.cached_property
    def tables(self) -> list[Table]:
        """Return all tables in spreadsheet.

        Returns:
        List[Table]: Tables in OpenOffice spreadsheet.
        """
        return [Table(e) for e in self.findall("table:table")]
