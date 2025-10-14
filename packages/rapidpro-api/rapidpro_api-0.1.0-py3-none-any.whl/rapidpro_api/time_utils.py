"""
Module with datetime utility functions for RapidPro API calls.

@author: merlos
@date: 2023-10-02
@title: Time Utils
"""
from datetime import datetime, timedelta, UTC
import logging


def get_previous_half_month_date_range(date=None):
    """
    Calculate before and after dates for RapidPro API calls based on the given date
    For a given dat, it provides the previous half month date range. So, if you provide
    a date within the first half of the month, it will return the date range for the
    second half of the previous month. If you provide a date in the second half of the month,
    it will return the date range for the first half of the current month.

    It uses day 15 regardless of the length of the month as the cutoff point.

Args:
date (datetime): The date to calculate the range for.
                 If None, the current date is used.
    If date is None, the current date is used.

    Rules:
    - If day of date > 15:
            - after: 1st day of current month at 00:00:00
            - before: 14th day of current month at 23:59:59
    - If day of date<= 15:
            - after: 15th day of previous month at 00:00:00
            - before: last day of previous month at 23:59:59

    Returns:
            tuple: (after_date, before_date) as datetime objects

    Example:
>>> from datetime import datetime
>>> after_date, before_date = twice_a_month_date_range(datetime(2023, 10, 20))
>>> print(after_date)
2023-10-01 00:00:00
>>> print(before_date)
2023-10-14 23:59:59
    """
    if date is None:
        date = datetime.now()

    day = date.day

    if day > 15:
        # After date: 1st of current month
        after_date = datetime(date.year, date.month, 1, 0, 0, 0, 0)
        # Before date: 14th of current month (end of day)
        before_date = datetime(date.year, date.month, 14, 23, 59, 59, 999999)
    else:
        # After date: 15th of previous month
        # Get the first day of the current month and go back one day
        first_day_current = datetime(date.year, date.month, 1)
        last_day_prev_month = first_day_current - timedelta(days=1)
        # Get the previous month
        prev_month = last_day_prev_month.month
        prev_year = last_day_prev_month.year

        # After date: 15th of previous month
        after_date = datetime(prev_year, prev_month, 15, 0, 0, 0, 0)
        # Before date: last day of previous month
        before_date = datetime(prev_year, prev_month,
                               last_day_prev_month.day, 23, 59, 59, 999999)

    return after_date, before_date


def get_last_friday_date(date=None):
    """
    Calculate the date of the last Friday (end of day) before the given date.

    Args:
            date (datetime): The date to calculate the last Friday for.
                                             If None, the current date is used.
    Returns:
            datetime: The date of the last Friday before the given date.

    Example:
            >>> from datetime import datetime
            >>> last_friday = get_last_friday_date(datetime(2025, 5, 21))
            >>> print(last_friday)
            2025-05-16 23:59:59
    """
    if date is None:
        date = datetime.now()

    # Calculate days since last Friday (not including today if today is Friday)
    days_since_friday = (date.weekday() - 4) % 7 or 7
    last_friday = date - timedelta(days=days_since_friday)
    last_friday = last_friday.replace(
        hour=23, minute=59, second=59, microsecond=999999)

    return last_friday


def get_last_week_ending_on_friday_range(date=None):
    """
    Calculate a week range for the last Friday week before the given date.
    The range starts on Saturday 0:00:00 and ends on last Friday before the date at 23:59:59.
    Args:
            date (datetime): The date to calculate the range for.
                                             If None, the current date is used.
    Returns:
            tuple: (after_date, before_date) as datetime objects
    Example:
            >>> from datetime import datetime
            # Tuesday
            >>> after_date, before_date = get_last_friday_week_range(datetime(2025, 5, 20))
            >>> print(after_date)
            2025-05-10 00:00:00 # Saturday 10th, 00:00:00h]
            >>> print(before_date)
            2025-05-16 23:59:59 # End of last Friday before the Monday 20th]
    """
    if date is None:
        date = datetime.now()

    # Get the last Friday (23:59:59)
    last_friday = get_last_friday_date(date)

    # Calculate the after and before dates
    after_date = last_friday.replace(
        hour=0, minute=0, second=0, microsecond=0) - timedelta(days=6)
    before_date = last_friday

    return after_date, before_date


def yesterday_end_of_day():
    """
    Get the end of day for yesterday.

    Returns:
            datetime: The end of day for yesterday.

    Example:
            >>> from datetime import datetime
            >>> yesterday_end = yesterday_end_of_day()
            >>> print(yesterday_end)
            2023-10-01 23:59:59
    """
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)


def get_date_range(a_date: datetime=None, frequency: str = "D"):
    """
    Calculate the period for a given date based on the frequency.
    Args:
        a_date (datetime): The date to calculate the period for. If None, the current date is used.
        frequency (str): The frequency for the period. Can be 'D', 'W', 'ME', or 'Y' (day, week, month end, year, respectively). Default is 'D' (daily).
    Returns:
        tuple: (after_date, before_date) as datetime objects	
    Example:
        >>> after_date, before_date = get_date_range(datetime(2023, 10, 1), frequency="ME")
        >>> print(after_date)
        2023-10-01 00:00:00
        >>> print(before_date)
        2023-10-31 23:59:59
        >>> print(get_date_range(datetime(2023, 10, 1), frequency="W"))
    """
    if a_date is None:
        a_date = datetime.now()
    after_date = a_date.replace(hour=0, minute=0, second=0, microsecond=0)
    if frequency == "D":
        before_date = a_date.replace(
            hour=23, minute=59, second=59, microsecond=999999)
    elif frequency == "W":  # Monday to Sunday
        # get the first day of the week (Monday)
        after_date = a_date - timedelta(days=a_date.weekday())
        # get the last day of the week (Sunday)
        before_date = after_date + \
            timedelta(days=6, hours=23, minutes=59,
                      seconds=59, microseconds=999999)
    elif frequency == "ME":
        # get the first day of the month
        after_date = a_date.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0)
        # get the first day of next month
        next_month_date = after_date.replace(month=(after_date.month % 12) + 1)
        if next_month_date.month == 1:
            next_month_date = next_month_date.replace(year=next_month_date.year + 1)
        before_date = next_month_date.replace(
            day=1, hour=0, minute=0, second=0, microsecond=999999) - timedelta(seconds=1)
    elif frequency == "Y":
        # get the first day of the year
        after_date = a_date.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        # get the first day of next year
        next_year_date = after_date.replace(year=after_date.year + 1)
        before_date = next_year_date.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=999999) - timedelta(seconds=1)
    else:
        raise ValueError("Invalid frequency. Use 'D', 'W', 'ME', or 'Y'.")
    return after_date, before_date


def get_iso_date_strings(iso_date:str):
    """
    Convert an ISO formatted date string to year, month, and day strings.
    Args:
        iso_date (str): The ISO formatted date string (e.g., "2023-10-02T12:34:56").
    Returns:
        tuple: (year, year-month, year-month-day) as strings.
    Example:
        >>> iso_date = "2023-10-02T12:34:56"
        >>> year, year_month, year_month_day = get_dates(iso_date)
        >>> print(year)  # Output: "2023"
        >>> print(year_month)  # Output: "2023-10"
        >>> print(year_month_day)  # Output: "2023-10-02"
    Raises:
        ValueError: If the ISO date string is empty or invalid.
    """
    if not iso_date:
        raise ValueError("ISO date string cannot be empty.")
    # Parse the ISO date string 
    iso_datetime = datetime.fromisoformat(iso_date)
    return iso_datetime.strftime("%Y"), iso_datetime.strftime("%Y-%m"), iso_datetime.strftime("%Y-%m-%d")
    