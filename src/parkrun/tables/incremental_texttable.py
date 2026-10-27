from texttable import Texttable
from typing import Any, Sequence

class IncrementalTexttable:
    """
    A wrapper around texttable to print a row at a time rather than all at once
    at the end. This means results can be printed as they are calculated, e.g.
    from a generator so the user can start seeing results before they have all
    been calculated.

    Typical usage with time.sleep to emphasise incremental nature:

    ```python
    from incremental_texttable import IncrementalTexttable
    import time

    table = IncrementalTexttable.default_with_col_widths([2, 2])
    print(table.draw_header(["x", "2x"]))

    for x in range(10):
        print(table.draw_row([x, 2 * x]))
        time.sleep(0.1)
    ```
    """

    def __init__(self, table: Texttable) -> None:
        """
        Use the given table, which allows full configuration (although its
        header and rows will be ignored). It is recommended to set its column
        widths otherwise different rows will have different column widths so
        they may not line up.
        """

        self._table: Texttable = table
        self._has_printed_something: bool = False

    @classmethod
    def default_with_col_widths(cls, col_widths: Sequence[int]) -> "IncrementalTexttable":
        """
        Return an instance whose table has the given column widths and
        everything else default.
        """

        return cls(Texttable().set_cols_width(col_widths))

    def _remove_top_border_if_required(self, text: str) -> str:

        if self._has_printed_something:
            return text.split("\n", 1)[1]

        self._has_printed_something = True
        return text

    def draw_header(self, headers: Sequence[Any]) -> str:
        """
        Return a string of just the headers to be printed. Must be called before
        anything else is drawn.
        """

        if self._has_printed_something:
            raise RuntimeError("The header must be drawn before anything else")

        header_text: str = self._table.reset().header(headers).draw()
        self._has_printed_something = True

        # Print the header row without the bottom line (it adds a bottom border
        # in addition to the header border despite there being no non-header rows)
        return header_text.rsplit("\n", 1)[0]

    def draw_row(self, row: Sequence[Any]) -> str:
        """
        Return a string of just this row to be printed
        """

        row_text: str = self._table.reset().add_row(row).draw()

        row_text = self._remove_top_border_if_required(row_text)

        return row_text


if __name__ == "__main__":
    import time

    table = IncrementalTexttable.default_with_col_widths([2, 2])
    print(table.draw_header(["x", "2x"]))

    for x in range(10):
        print(table.draw_row([x, 2 * x]))
        time.sleep(0.1)
