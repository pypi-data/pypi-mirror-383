"""Give access to ods files."""

from __future__ import annotations

from typing import TYPE_CHECKING
from zipfile import ZipFile

from lxml import etree

if TYPE_CHECKING:
    from pathlib import Path

__date__ = "2024/08/03 17:02:21 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2020 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


class OdfXml:
    """Base XML handling class for ODF processing."""

    def __init__(self, elem: etree._Element) -> None:
        """Intialize instance.

        Args:
        elem (etree._Element): XML Element
        """
        self.root = elem
        self.nsmap = (
            self.root.nsmap if hasattr(elem, "nsmap") else self.root.getroot().nsmap
        )

    def find(self, tag: str) -> etree._Element:
        """Find ``tag`` in this element.

        Args:
            tag (str): XML tag to serarch for.

        Returns:
        etree._Element: Element acc. to ``tag``.
        """
        return self.root.find(tag, namespaces=self.nsmap)

    def findall(self, tag: str) -> list[etree._Element]:
        """Find all of ``tag``.

        Args:
           tag (str): XML tag to find.

        Returns:
        list[etree._Element]: Element acc. to ``tag``.
        """
        return self.root.findall(tag, namespaces=self.nsmap)

    def _attrib_map(self, attrib: str) -> str:
        """Helper for ``get``: provide namespace.

        Args:
           attrib (str): attribute name in the form of <namespace name>:<attr name>.

        Returns:
        str: attribute name with extended namespace.
        """
        ns, tag = attrib.split(":")
        return f"{{{self.nsmap[ns]}}}{tag}"

    def get(self, attrib: str) -> str:
        """Get atribute of this element, honors namespace.

        Args:
           attrib(str): Attrribute name.

        Returns:
        str: Attribute value.
        """
        return self.root.get(self._attrib_map(attrib))


class Odf(OdfXml):
    """Base class for OpenDocument Format files."""

    def __init__(self, path: str | Path):
        """Open ODF file from ``path``.

        Args:
           path (str | Path): Location of OpenOffice file.
        """
        with ZipFile(path) as odf_zip, odf_zip.open("content.xml") as content:
            doc = etree.parse(content)
        super().__init__(doc)
