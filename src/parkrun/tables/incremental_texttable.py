import math
from texttable import Texttable
from typing import Any, Sequence, Union

class IncrementalTexttable:
    """
    A wrapper around texttable to print a row at a time rather than all at once
    at the end. This means results can be printed as they are calculated, e.g.
    from a generator so the user can start seeing results before they have all
    been calculated.

    Typical usage with time.sleep to emphasise incremental nature:

    ```python
    from parkrun.tables.incremental_texttable import IncrementalTexttable
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

    @staticmethod
    def calc_col_widths(max_width: int, widths: Sequence[Union[int, str]]) -> list[int]:
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
