import unittest
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from rowstoheader import render
from cjwmodule.testing.i18n import i18n_message, cjwmodule_i18n_message


class TestRowsToHeader(unittest.TestCase):
    def test_first_row(self):
        out = render(
            pd.DataFrame({"A": [1, 2, 3], "B": ["foo", "bar", None]}),
            {"rows": "1", "deleteabove": True},
        )
        assert_frame_equal(out, pd.DataFrame({"1": [2, 3], "foo": ["bar", None]}))

    def test_multiple_rows(self):
        out = render(
            pd.DataFrame(
                {
                    "A": [1, 2, 3, 4],
                    "B": ["foo", None, "", "moo"],
                    "C": [None, None, "Column 3", None],
                }
            ),
            {"rows": "1-3", "deleteabove": True},
        )
        assert_frame_equal(
            out, pd.DataFrame({"1 – 2 – 3": [4], "foo": ["moo"], "Column 3": [None]})
        )

    def test_keep_middle_rows(self):
        out = render(
            pd.DataFrame({"A": [1, 2, 3, 4], "B": ["foo", None, "", "moo"]}),
            {"rows": "1,3", "deleteabove": False},
        )
        assert_frame_equal(out, pd.DataFrame({"1 – 3": [2, 4], "foo": [None, "moo"]}))

    def test_drop_middle_rows(self):
        out = render(
            pd.DataFrame(
                {
                    "A": [1, 2, 3, 4],
                    "B": ["foo", None, "", "moo"],
                    "C": [None, None, "Column 3", None],
                }
            ),
            {"rows": "1,3", "deleteabove": True},
        )
        assert_frame_equal(
            out, pd.DataFrame({"1 – 3": [4], "foo": ["moo"], "Column 3": [None]})
        )

    def test_avoid_duplicate_columns(self):
        out = render(
            pd.DataFrame(
                {
                    "A": [1, 2, 3, 4],
                    "B": [1, 2, 3, 4],
                    "C": [1, 2, 3, 4],
                    "D": ["1", "2_1", "3", "4"],
                }
            ),
            {"rows": "1-2", "deleteabove": False},
        )
        assert_frame_equal(
            out[0],
            pd.DataFrame(
                {
                    "1 – 2": [3, 4],
                    "1 – 3": [3, 4],
                    "1 – 4": [3, 4],
                    "1 – 2_1": ["3", "4"],
                }
            ),
        )
        self.assertEqual(
            out[1],
            [
                cjwmodule_i18n_message(
                    "util.colnames.warnings.numbered",
                    {"n_columns": 2, "first_colname": "1 – 3"},
                )
            ],
        )

    def test_avoid_empty_columns(self):
        out = render(
            pd.DataFrame(
                {
                    "A": ["", "x"],
                    "B": [np.nan, "y"],
                    "C": [None, "z"],
                    "D": ["Column 1", "a"],  # curve-ball: prevent rename
                }
            ),
            {"rows": "1", "deleteabove": False},
        )
        assert_frame_equal(
            out[0],
            pd.DataFrame(
                {
                    "Column 4": ["x"],
                    "Column 2": ["y"],
                    "Column 3": ["z"],
                    "Column 1": ["a"],
                }
            ),
        )
        self.assertEqual(
            out[1],
            [
                cjwmodule_i18n_message(
                    "util.colnames.warnings.default",
                    {"n_columns": 3, "first_colname": "Column 4"},
                ),
                cjwmodule_i18n_message(
                    "util.colnames.warnings.numbered",
                    {"n_columns": 1, "first_colname": "Column 4"},
                ),
            ],
        )

    def test_no_rows_no_op(self):
        out = render(
            pd.DataFrame(
                {"A": [1, 2, 3], "B": ["foo", "bar", None], "C": [None, None, None]}
            ),
            {"rows": "", "deleteabove": True},
        )
        assert_frame_equal(
            out,
            pd.DataFrame(
                {"A": [1, 2, 3], "B": ["foo", "bar", None], "C": [None, None, None]}
            ),
        )

    def test_remove_unused_categories(self):
        result = render(
            pd.DataFrame({"A": ["a", "b", "c"]}, dtype="category"),
            {"rows": "2", "deleteabove": True},
        )
        assert_frame_equal(result, pd.DataFrame({"b": ["c"]}, dtype="category"))

    def test_zero_gives_error(self):
        out = render(
            pd.DataFrame({"A": ["a", "b", "c"]}, dtype="category"), {"rows": "0-1"}
        )
        self.assertEqual(
            out, i18n_message("badParam.rows.invalidRange", {"value": "0-1"})
        )
