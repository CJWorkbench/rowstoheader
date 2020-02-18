import re
from typing import Any, Dict, Tuple, List
import pandas as pd
from pandas import IntervalIndex
from cjwmodule import i18n


commas = re.compile('\\s*,\\s*')
numbers = re.compile('(?P<first>[1-9]\d*)(?:-(?P<last>[1-9]\d*))?')

class RangeFormatError(ValueError):
    def __init__(self, value):
        self.value = value
        
    @property
    def i18n_message(self) -> i18n.I18nMessage:
        return i18n.trans(
            "badParam.rows.invalidRange",
            'Rows must look like "1-2", "5" or "1-2, 5"; got "{value}"',
            {"value": self.value}
        )

def parse_interval(s: str) -> Tuple[int, int]:
    """
    Parse a string 'interval' into a tuple

    >>> parse_interval('1')
    (0, 1)
    >>> parse_interval('1-3')
    (0, 2)
    >>> parse_interval('5')
    (4, 4)
    >>> parse_interval('hi')
    Traceback (most recent call last):
        ...
    RangeFormatError: Rows must look like "1-2", "5" or "1-2, 5"; got "hi"
    """
    match = numbers.fullmatch(s)
    if not match:
        raise RangeFormatError(s)

    first = int(match.group('first'))
    last = int(match.group('last') or first)
    return (first - 1, last - 1)


class Form:
    def __init__(self, index: IntervalIndex, delete_above: bool):
        self.index = index
        self.delete_above = delete_above

    @staticmethod
    def parse(d: Dict[str, Any]) -> 'Form':
        rows = d.get('rows', '')
        tuples = [parse_interval(s)
                  for s in commas.split(rows.strip()) if s.strip()]
        index = IntervalIndex.from_tuples(tuples, closed='both')

        delete_above = d.get('deleteabove', False)

        return Form(index, delete_above)


def _make_names_unique(names: List[str]) -> List[str]:
    """Append to each name if necessary, to make a list without duplicates."""
    counts = {}

    def unique_name(ideal_name: str) -> str:
        """
        Generate a guaranteed-unique column name, using `counts` as state.

        No-op if ideal_name is empty. (We'll rename empty columns later.)

        Strategy for making 'A' unique:
        * If 'A' has never been seen before, return it.
        * If 'A' has been seen before, try 'A_1' or 'A_2' (where 1 and 2 are
          the number of times 'A' has been seen).
        * If there is a conflict on 'A_1', recurse.
        """
        if ideal_name not in counts or not ideal_name:
            counts[ideal_name] = 1
            return ideal_name

        count = counts[ideal_name]
        counts[ideal_name] += 1
        backup_name = f'{ideal_name}_{count}'
        return unique_name(backup_name)

    def rename_empty(ideal_name: str, index: int) -> str:
        """
        Rename an empty column to "Column 1" ... or "Column 1_1" if the latter
        is taken.
        """
        if not ideal_name:
            ideal_name = 'Column %d' % (index + 1)
            return unique_name(ideal_name)
        else:
            return ideal_name

    names_including_empty = [unique_name(name) for name in names]
    return [rename_empty(name, i)
            for i, name in enumerate(names_including_empty)]


def process(table: pd.DataFrame, form: Form) -> pd.DataFrame:
    mask = form.index.get_indexer(table.index) >= 0

    # Find column names
    header_rows = table[mask]
    if header_rows.empty:
        # Usually, this is because rows='', which is valid input because it's
        # the default.
        return table
    header_rows_str = header_rows.astype(str)
    header_rows_str[header_rows.isna()] = ''
    names = list(header_rows_str.agg(lambda x: ' – '.join(s for s in x if s)))
    unique_names = _make_names_unique(names)

    if form.delete_above:
        max_header_index = max(t[1] for t in form.index.to_tuples())
        mask[0:max_header_index] = True

    table = table[~mask]
    table.reset_index(drop=True, inplace=True)
    table.columns = unique_names
    for column in unique_names:
        series = table[column]
        if hasattr(series, 'cat'):
            series.cat.remove_unused_categories(inplace=True)
    return table


def render(table, params):
    try:
        form = Form.parse(params)
    except RangeFormatError as err:
        return err.i18n_message

    return process(table, form)
