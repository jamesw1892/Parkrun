import math
from texttable import Texttable
from types import TracebackType
from typing import Any, Optional, Sequence, TextIO, Union

# A fixed width as an int or a percentage of the remaining width like "50%"
Width = Union[int, str]

class IncrementalTexttable:
    """
    A wrapper around texttable to print a table a row at a time rather than all
    at once at the end. This means results can be printed as they are
    calculated, e.g. from a generator so the user can start seeing results
    before they have all been calculated. It can also print all at once so the
    caller can choose either with the same code.

    Typical usage with time.sleep to emphasise incremental nature:

    ```python
    from parkrun.tables.incremental_texttable import IncrementalTexttable
    import time

    with IncrementalTexttable([("x", 2), ("2x", "100%")], 20) as table:
        for x in range(10):
            table.add_row([x, 2 * x])
            time.sleep(0.1)
    ```
    """

    def __init__(
        self,
        columns: Sequence[tuple[str, Width]],
        max_width: Optional[int],
        incremental: bool = True,
        file: Optional[TextIO] = None,
    ) -> None:
        """
        Each column is a pair of its header and its width, which is either a
        fixed width or a percentage of the remaining width (see
        calc_col_widths). The whole table is at most max_width characters wide,
        or texttable's default if None.

        If incremental then the header is printed immediately and each row as
        it is added, using the widths so the columns line up, and max_width
        must be given if any are percentages. Otherwise everything is printed
        by finish() and the widths are ignored so texttable can fit the columns
        to their contents.

        Print to file if given, otherwise stdout.
        """

        self._incremental: bool = incremental
        self._file: Optional[TextIO] = file
        self._rows: list[Sequence[Any]] = []
        self._has_printed_row: bool = False
        self._finished: bool = False

        self._table: Texttable = Texttable()
        if max_width is not None:
            self._table.set_max_width(max_width)

        self._headers: list[str] = []
        widths: list[Width] = []
        for header, width in columns:
            if not isinstance(header, str):
                raise TypeError(f"Header {header!r} is not a string")
            if not isinstance(width, (int, str)):
                raise TypeError(f"Width {width!r} is not an int or a string")
            self._headers.append(header)
            widths.append(width)

        if not incremental:
            return

        if max_width is None:
            if not all(isinstance(width, int) for width in widths):
                raise ValueError("Percentage widths need a max width")
            self._table.set_cols_width(widths)
        else:
            self._table.set_cols_width(self.calc_col_widths(max_width, widths))

        # Print the header row without the bottom line (it adds a bottom border
        # in addition to the header border despite there being no non-header
        # rows), keeping the bottom line in case there are no rows
        header_text, self._header_bottom_border = self._table.reset().header(self._headers).draw().rsplit("\n", 1)
        self._print(header_text)

    def __enter__(self) -> "IncrementalTexttable":
        return self

    def __exit__(self, exc_type: Optional[type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]) -> None:

        # Don't print anything more if something went wrong
        if exc_type is None:
            self.finish()

    @staticmethod
    def calc_col_widths(max_width: int, widths: Sequence[Width]) -> list[int]:
        """
        Return column widths such that the whole table is max_width characters
        wide, including padding and vertical lines. Each column in widths that
        is an int has that fixed width. The remaining width is shared between
        the other columns, which must be percentages of the form "50%" that
        add up to 100.

        For example, `calc_col_widths(60, ["50%", 7, "50%", 7])`
        returns `[17, 7, 16, 7]`.
        """

        fixed_widths: list[int] = []
        percentages: list[float] = []
        for width in widths:
            if isinstance(width, int):
                fixed_widths.append(width)
            elif width.endswith("%"):
                try:
                    percentages.append(float(width[:-1]))
                except ValueError:
                    raise ValueError(f"Invalid percentage {width!r}") from None
            else:
                raise ValueError(f"Width {width!r} is not an int or a percentage like '50%'")

        num_flexible: int = len(percentages)
        if num_flexible > 0 and not math.isclose(sum(percentages), 100):
            raise ValueError(f"Percentages add up to {sum(percentages)} not 100")

        # Subtract the padding and vertical line to the right of each column as
        # well as the vertical line on the far left
        remaining: int = max_width - sum(fixed_widths) - 3 * len(widths) - 1
        if remaining < num_flexible:
            raise ValueError(f"Max width {max_width} is too small to fit the fixed width columns")

        # Round each share down and give the characters left over to the
        # columns that lost the most by rounding so the total is exact
        exact: list[float] = [remaining * p / 100 for p in percentages]
        flexible_widths: list[int] = [math.floor(e) for e in exact]
        by_largest_remainder: list[int] = sorted(range(num_flexible), key=lambda i: exact[i] - flexible_widths[i], reverse=True)
        for i in by_largest_remainder[:remaining - sum(flexible_widths)]:
            flexible_widths[i] += 1

        # Every column needs to be at least 1 wide
        if 0 in flexible_widths:
            raise ValueError(f"Max width {max_width} is too small to give every column a width")

        flexible_iter = iter(flexible_widths)
        return [w if isinstance(w, int) else next(flexible_iter) for w in widths]

    def _print(self, text: str) -> None:
        print(text, file=self._file, flush=True)

    def add_row(self, row: Sequence[Any]) -> None:
        """
        Print the row now if incremental, otherwise store it to print in
        finish().
        """

        if self._finished:
            raise RuntimeError("Can't add a row after finishing")
        if len(row) != len(self._headers):
            raise ValueError(f"Row has {len(row)} cells but there are {len(self._headers)} columns")

        if not self._incremental:
            self._rows.append(row)
            return

        # Print the row without the top border since it is the same as the
        # bottom of the header or previous row
        self._print(self._table.reset().add_row(row).draw().split("\n", 1)[1])
        self._has_printed_row = True

    def finish(self) -> None:
        """
        Print the whole table if not incremental, otherwise the bottom border
        if there were no rows. Called automatically when used as a context
        manager and nothing goes wrong.
        """

        if self._finished:
            raise RuntimeError("Already finished")
        self._finished = True

        if not self._incremental:
            self._print(self._table.reset().header(self._headers).add_rows(self._rows, header=False).draw())
        elif not self._has_printed_row:
            self._print(self._header_bottom_border)


if __name__ == "__main__":
    import time

    with IncrementalTexttable([("x", 2), ("2x", "100%")], 20) as table:
        for x in range(10):
            table.add_row([x, 2 * x])
            time.sleep(0.1)
