"""Testing accessing ods files."""

import pytest

from berhoel.odf.ods import LINKED_CELL, IMDB_HYPERLINK, Ods

__date__ = "2024/08/03 16:45:57 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2020 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


@pytest.fixture()
def ods_sample1(data1):
    return Ods(data1)


def test_tables(ods_sample1):
    assert ods_sample1.tables is not None
    assert len(ods_sample1.tables) == 2


@pytest.fixture()
def tables(ods_sample1):
    return ods_sample1.tables


def test_table_names(tables):
    assert tables[0].name == "Tabelle1"
    assert tables[1].name == "Tabelle2"


def test_table_rows(tables):
    assert len(tables[0].rows) == 9
    assert len(tables[1].rows) == 4


def test_table_hidden(tables):
    assert not tables[0].hidden
    assert tables[1].hidden


@pytest.fixture()
def rows0(tables):
    return tables[0].rows


@pytest.fixture()
def rows1(tables):
    return tables[1].rows


def test_rows0_1(rows0):
    for i, row in enumerate(rows0):
        assert len(row.cells) == 4, f"row: {i}"


def test_rows1_1(rows1):
    for i, row in enumerate(rows1):
        assert len(row.cells) == 3, f"row: {i}"


@pytest.mark.parametrize(
    "test_input, url_ref, title_ref",
    [
        [
            'of:=HYPERLINK("http://www.imdb.com/title/tt0094612/";"Action Jackson")',
            "http://www.imdb.com/title/tt0094612",
            "Action Jackson",
        ],
        [
            'of:=HYPERLINK( "http://www.imdb.com/title/tt0094612/" ; "Action Jackson")',
            "http://www.imdb.com/title/tt0094612",
            "Action Jackson",
        ],
        [
            'of:=HYPERLINK("http://www.imdb.com/title/tt3375370";"The Gunfighter (2014)" )',
            "http://www.imdb.com/title/tt3375370",
            "The Gunfighter (2014)",
        ],
        [
            'of:=HYPERLINK("https://www.imdb.com/title/tt0055205/?ref_=nv_sr_1";"16 Uhr 50 ab Paddington (1961)")',
            "https://www.imdb.com/title/tt0055205",
            "16 Uhr 50 ab Paddington (1961)",
        ],
        [
            'of:=HYPERLINK("https://www.imdb.com/title/tt0043265/?ref_=fn_al_tt_2";"African Queen (1951)")',
            "https://www.imdb.com/title/tt0043265",
            "African Queen (1951)",
        ],
        [
            'of:=HYPERLINK("https://www.imdb.com/title/tt1299368/?ref_=tt_ov_inf";"Southland")',
            "https://www.imdb.com/title/tt1299368",
            "Southland",
        ],
        [
            'of:=HYPERLINK("http://www.imdb.com/title/tt2621446?ref_=tt_ov_inf";"Star Trek: Renegades")',
            "http://www.imdb.com/title/tt2621446",
            "Star Trek: Renegades",
        ],
        [
            'of:=HYPERLINK("http://www.imdb.com/title/tt0284718/episodes";"Crossing Jordan")',
            "http://www.imdb.com/title/tt0284718",
            "Crossing Jordan",
        ],
    ],
)
def test_indb_hyperlink(test_input, url_ref, title_ref):
    match = IMDB_HYPERLINK.match(test_input)
    title, url = match.group("name"), match.group("url")
    assert url == url_ref
    assert title == title_ref


@pytest.mark.parametrize(
    "test_input, val_ref",
    [
        ["of:=-['k&v'.F207]", "207"],
        ["of:=-[$'k&v'.F207]", "207"],
        ["of:=-0.5*['k&v'.F818]", "818"],
    ],
)
def test_dvd_link(test_input, val_ref):
    match = LINKED_CELL.match(test_input)
    val = match.group("line")
    assert val == val_ref
