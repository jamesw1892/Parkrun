from texttable import Texttable
from typing import Any, Optional, Sequence

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

    table = IncrementalTexttable(col_widths=[2, 2])
    print(table.draw_header(["x", "2x"]))

    for x in range(10):
        print(table.draw_row([x, 2 * x]))
        time.sleep(0.1)
    ```
    """

    def __init__(
        self,
        col_widths: Optional[Sequence[int]] = None,
        table: Optional[Texttable] = None,
    ) -> None:
        """
        If given table, ignore other arguments and use this directly (although
        header and other rows will be ignored). This allows full configuration.

        Otherwise, create a new table and configure it with the given column
        widths if provided and everything else default. It is recommended to
        provide widths otherwise different rows will have different column
        widths so they may not line up.
        """

        self._has_printed_something: bool = False

        if table is not None:
            self._table = table
            return

        self._table: Texttable = Texttable()

        if col_widths is not None:
            self._table.set_cols_width(col_widths)

    def _remove_top_border_if_required(self, text: str) -> str:

        if self._has_printed_something:
            return text.split("\n", 1)[1]

        self._has_printed_something = True
        return text

    def draw_header(self, headers: Sequence[Any]) -> str:
        """
        Return a string of just the headers to be printed
        """

        header_text: str = self._table.reset().header(headers).draw()

        # If for some reason a row has already been printed, remove the top
        # border from this
        header_text = self._remove_top_border_if_required(header_text)

        # Print the header row without the bottom line (it adds a bottom border
        # in addition to the header border despite there being no non-header rows)
        return header_text[::-1].split("\n", 1)[1][::-1]

    def draw_row(self, row: Sequence[Any]) -> str:
        """
        Return a string of just this row to be printed
        """

        row_text: str = self._table.reset().add_row(row).draw()

        row_text = self._remove_top_border_if_required(row_text)

        return row_text


if __name__ == "__main__":
    import time

    table = IncrementalTexttable(col_widths=[2, 2])
    print(table.draw_header(["x", "2x"]))

    for x in range(10):
        print(table.draw_row([x, 2 * x]))
        time.sleep(0.1)
