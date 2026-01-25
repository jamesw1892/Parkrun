from __future__ import annotations
import datetime

# TODO: Extend timedelta to inherit all its operations?
class Time:
    """
    timedelta is a datetime.timedelta.
    string is formatted H:MM:SS or MM:SS or 'x day[s], H:MM:SS' (only if not
    from a single run, e.g. total run time).
    """
    def __init__(self, string: str, timedelta: datetime.timedelta):
        self.string: str = string
        self.timedelta: datetime.timedelta = timedelta

    @staticmethod
    def from_string(string: str) -> Time:
        splat_time: list[str] = string.split(":")
        timedelta: datetime.timedelta = datetime.timedelta(
            hours = 0 if len(splat_time) == 2 else int(splat_time[0]),
            minutes = int(splat_time[-2]),
            seconds = int(splat_time[-1])
        )
        return Time(string, timedelta)

    @staticmethod
    def from_timedelta(timedelta: datetime.timedelta) -> Time:
        # Take the timedelta string format which is
        # [x day[s], ]H:MM:SS.ffffff
        # but remove the fractional part and if the hours is 0 then also
        # remove that.
        string: str = str(timedelta).split(".")[0].removeprefix("0:")
        return Time(string, timedelta)

    def __str__(self) -> str:
        return self.string
