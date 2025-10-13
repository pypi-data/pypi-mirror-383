"""Testing base functionalities of berhoel.odf library."""

from berhoel.odf import Odf

__date__ = "2024/08/03 17:18:10 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2020 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


def test_init(data1):
    _ = Odf(data1)
