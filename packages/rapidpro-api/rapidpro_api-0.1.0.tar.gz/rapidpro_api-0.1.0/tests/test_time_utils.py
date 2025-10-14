import pytest
from datetime import datetime
from freezegun import freeze_time
from rapidpro_api.time_utils import get_previous_half_month_date_range
from rapidpro_api.time_utils import get_last_friday_date, get_last_week_ending_on_friday_range
from rapidpro_api.time_utils import yesterday_end_of_day
from rapidpro_api.time_utils import get_date_range
from rapidpro_api.time_utils import get_iso_date_strings


class TestGetPreviousHalfMonthDateRange:

    def test_date_in_second_half_of_month(self):
        # Test for a date in the second half of the month (after 15th)
        test_date = datetime(2023, 10, 20)
        after_date, before_date = get_previous_half_month_date_range(test_date)

        assert after_date == datetime(2023, 10, 1, 0, 0, 0)
        assert before_date == datetime(2023, 10, 14, 23, 59, 59, 999999)

    def test_date_in_first_half_of_month(self):
        # Test for a date in the first half of the month (before or on 15th)
        test_date = datetime(2023, 10, 10)
        after_date, before_date = get_previous_half_month_date_range(test_date)

        assert after_date == datetime(2023, 9, 15, 0, 0, 0)
        assert before_date == datetime(2023, 9, 30, 23, 59, 59, 999999)

    def test_exactly_day_fifteen(self):
        # Test for a date exactly on the 15th (edge case)
        test_date = datetime(2023, 10, 15)
        after_date, before_date = get_previous_half_month_date_range(test_date)

        assert after_date == datetime(2023, 9, 15, 0, 0, 0)
        assert before_date == datetime(2023, 9, 30, 23, 59, 59, 999999)

    def test_first_day_of_month(self):
        # Test for the first day of the month (edge case)
        test_date = datetime(2023, 10, 1)
        after_date, before_date = get_previous_half_month_date_range(test_date)

        assert after_date == datetime(2023, 9, 15, 0, 0, 0)
        assert before_date == datetime(2023, 9, 30, 23, 59, 59, 999999)

    def test_last_day_of_month(self):
        # Test for the last day of the month (edge case)
        test_date = datetime(2023, 10, 31)
        after_date, before_date = get_previous_half_month_date_range(test_date)

        assert after_date == datetime(2023, 10, 1, 0, 0, 0)
        assert before_date == datetime(2023, 10, 14, 23, 59, 59, 999999)

    def test_month_transition_january_december(self):
        # Test transition from January to previous December (year boundary)
        test_date = datetime(2023, 1, 10)
        after_date, before_date = get_previous_half_month_date_range(test_date)

        assert after_date == datetime(2022, 12, 15, 0, 0, 0)
        assert before_date == datetime(2022, 12, 31, 23, 59, 59, 999999)

    def test_february_short_month(self):
        # Test with February in a non-leap year
        test_date = datetime(2023, 3, 5)
        after_date, before_date = get_previous_half_month_date_range(test_date)

        assert after_date == datetime(2023, 2, 15, 0, 0, 0)
        assert before_date == datetime(2023, 2, 28, 23, 59, 59, 999999)

    def test_february_leap_year(self):
        # Test with February in a leap year
        test_date = datetime(2024, 3, 5)
        after_date, before_date = get_previous_half_month_date_range(test_date)

        assert after_date == datetime(2024, 2, 15, 0, 0, 0)
        assert before_date == datetime(2024, 2, 29, 23, 59, 59, 999999)

    def test_none_date(self):
        # Test when no date is provided (should use current date)
        with freeze_time("2023-10-20"):
            after_date, before_date = get_previous_half_month_date_range()

            assert after_date == datetime(2023, 10, 1, 0, 0, 0)
            assert before_date == datetime(2023, 10, 14, 23, 59, 59, 999999)


class TestGetLastFridayDate:

    def test_regular_wednesday(self):
        test_date = datetime(2025, 5, 21)  # Wednesday
        last_friday = get_last_friday_date(test_date)
        assert last_friday == datetime(2025, 5, 16, 23, 59, 59, 999999)

    def test_on_friday(self):
        test_date = datetime(2025, 5, 16)  # Friday
        last_friday = get_last_friday_date(test_date)
        assert last_friday == datetime(2025, 5, 9, 23, 59, 59, 999999)

    def test_on_saturday(self):
        test_date = datetime(2025, 5, 17)  # Saturday
        last_friday = get_last_friday_date(test_date)
        assert last_friday == datetime(2025, 5, 16, 23, 59, 59, 999999)

    def test_on_sunday(self):
        test_date = datetime(2025, 5, 18)  # Sunday
        last_friday = get_last_friday_date(test_date)
        assert last_friday == datetime(2025, 5, 16, 23, 59, 59, 999999)

    def test_none_date(self):
        with freeze_time("2025-05-21"):
            last_friday = get_last_friday_date()
            assert last_friday == datetime(2025, 5, 16, 23, 59, 59, 999999)

    def test_year_boundary(self):
        test_date = datetime(2024, 1, 2)  # Tuesday
        last_friday = get_last_friday_date(test_date)
        assert last_friday == datetime(2023, 12, 29, 23, 59, 59, 999999)

    def test_leap_year(self):
        test_date = datetime(2024, 3, 1)  # Friday (leap year)
        last_friday = get_last_friday_date(test_date)
        assert last_friday == datetime(2024, 2, 23, 23, 59, 59, 999999)

    def test_invalid_type(self):
        with pytest.raises(AttributeError):
            # Not a datetime object
            get_last_friday_date("2023-10-20")


class TestGetLastWeekEndingOnFridayRange:

    def test_regular_tuesday(self):
        test_date = datetime(2025, 5, 20)  # Tuesday
        after_date, before_date = get_last_week_ending_on_friday_range(
            test_date)
        assert after_date == datetime(2025, 5, 10, 0, 0, 0)
        assert before_date == datetime(2025, 5, 16, 23, 59, 59, 999999)

    def test_on_friday(self):
        test_date = datetime(2025, 5, 16)  # Friday
        after_date, before_date = get_last_week_ending_on_friday_range(
            test_date)
        assert after_date == datetime(2025, 5, 3, 0, 0, 0)
        assert before_date == datetime(2025, 5, 9, 23, 59, 59, 999999)

    def test_on_saturday(self):
        test_date = datetime(2025, 5, 17)  # Saturday
        after_date, before_date = get_last_week_ending_on_friday_range(
            test_date)
        assert after_date == datetime(2025, 5, 10, 0, 0, 0)
        assert before_date == datetime(2025, 5, 16, 23, 59, 59, 999999)

    def test_on_sunday(self):
        test_date = datetime(2025, 5, 18)  # Sunday
        after_date, before_date = get_last_week_ending_on_friday_range(
            test_date)
        assert after_date == datetime(2025, 5, 10, 0, 0, 0)
        assert before_date == datetime(2025, 5, 16, 23, 59, 59, 999999)

    def test_none_date(self):
        with freeze_time("2025-05-20"):
            after_date, before_date = get_last_week_ending_on_friday_range()
            assert after_date == datetime(2025, 5, 10, 0, 0, 0)
            assert before_date == datetime(2025, 5, 16, 23, 59, 59, 999999)

    def test_year_boundary(self):
        test_date = datetime(2024, 1, 2)  # Wednesday
        after_date, before_date = get_last_week_ending_on_friday_range(
            test_date)
        assert after_date == datetime(2023, 12, 23, 0, 0, 0)
        assert before_date == datetime(2023, 12, 29, 23, 59, 59,999999)

    def test_leap_year(self):
        test_date = datetime(2024, 3, 1)  # Friday (leap year)
        after_date, before_date = get_last_week_ending_on_friday_range(
            test_date)
        assert after_date == datetime(2024, 2, 17, 0, 0, 0)
        assert before_date == datetime(2024, 2, 23, 23, 59, 59, 999999)

    def test_invalid_type(self):
        with pytest.raises(AttributeError):
            get_last_week_ending_on_friday_range(
                "2023-10-20")  # Not a datetime object



class TestYesterdayEndOfDay:
    def test_yesterday_end_of_day(self):
        # Freeze time to a specific date
        with freeze_time("2023-10-01"):
            yesterday_end = yesterday_end_of_day()
            assert yesterday_end == datetime(2023, 9, 30, 23, 59, 59, 999999)
        # Test with a different date
        with freeze_time("2023-10-15"):
            yesterday_end = yesterday_end_of_day()
            assert yesterday_end == datetime(2023, 10, 14, 23, 59, 59, 999999)
    def test_yesterday_end_of_day_edge_cases(self):
        # Test with a date in a leap year
        with freeze_time("2024-03-01"):
            yesterday_end = yesterday_end_of_day()
            assert yesterday_end == datetime(2024, 2, 29, 23, 59, 59, 999999)
        # Test with a date at the beginning of the month
        with freeze_time("2023-10-01"):
            yesterday_end = yesterday_end_of_day()
            assert yesterday_end == datetime(2023, 9, 30, 23, 59, 59, 999999)
        # Test with a date at the end of the month
        with freeze_time("2023-10-31"):
            yesterday_end = yesterday_end_of_day()
            assert yesterday_end == datetime(2023, 10, 30, 23, 59, 59, 999999)

class TestGetDateRange:

    def test_daily_frequency(self):
        test_date = datetime(2023, 10, 20)
        after_date, before_date = get_date_range(test_date, frequency="D")
        assert after_date == datetime(2023, 10, 20, 0, 0, 0)
        assert before_date == datetime(2023, 10, 20, 23, 59, 59, 999999)

    def test_weekly_frequency(self):
        test_date = datetime(2023, 10, 20)  # Friday
        after_date, before_date = get_date_range(test_date, frequency="W")
        assert after_date == datetime(2023, 10, 16, 0, 0, 0)  # Monday
        assert before_date == datetime(2023, 10, 22, 23, 59, 59, 999999)  # Sunday

    def test_monthly_frequency(self):
        test_date = datetime(2023, 10, 20)
        after_date, before_date = get_date_range(test_date, frequency="ME")
        assert after_date == datetime(2023, 10, 1, 0, 0, 0, 0)
        assert before_date == datetime(2023, 10, 31, 23, 59, 59, 999999)

    def test_yearly_frequency(self):
        test_date = datetime(2023, 10, 20)
        after_date, before_date = get_date_range(test_date, frequency="Y")
        assert after_date == datetime(2023, 1, 1, 0, 0, 0)
        assert before_date == datetime(2023, 12, 31, 23, 59, 59, 999999)

    def test_invalid_frequency(self):
        test_date = datetime(2023, 10, 20)
        with pytest.raises(ValueError, match="Invalid frequency. Use 'D', 'W', 'ME', or 'Y'."):
            get_date_range(test_date, frequency="INVALID")
            get_date_range(test_date, frequency="M")

    def test_none_date_daily(self):
        with freeze_time("2023-10-20"):
            after_date, before_date = get_date_range(None, frequency="D")
            assert after_date == datetime(2023, 10, 20, 0, 0, 0)
            assert before_date == datetime(2023, 10, 20, 23, 59, 59, 999999)

    def test_none_date_weekly(self):
        with freeze_time("2023-10-20"):
            after_date, before_date = get_date_range(None, frequency="W")
            assert after_date == datetime(2023, 10, 16, 0, 0, 0)  # Monday
            assert before_date == datetime(2023, 10, 22, 23, 59, 59, 999999)  # Sunday

    def test_none_date_monthly(self):
        with freeze_time("2023-10-20"):
            after_date, before_date = get_date_range(None, frequency="ME")
            assert after_date == datetime(2023, 10, 1, 0, 0, 0)
            assert before_date == datetime(2023, 10, 31, 23, 59, 59, 999999)

    def test_none_date_yearly(self):
        with freeze_time("2023-10-20"):
            after_date, before_date = get_date_range(None, frequency="Y")
            assert after_date == datetime(2023, 1, 1, 0, 0, 0)
            assert before_date == datetime(2023, 12, 31, 23, 59, 59, 999999)

    def test_leap_year_daily(self):
        test_date = datetime(2024, 2, 29)  # Leap year
        after_date, before_date = get_date_range(test_date, frequency="D")
        assert after_date == datetime(2024, 2, 29, 0, 0, 0)
        assert before_date == datetime(2024, 2, 29, 23, 59, 59, 999999)

    def test_leap_year_monthly(self):
        test_date = datetime(2024, 2, 15)  # Leap year
        after_date, before_date = get_date_range(test_date, frequency="ME")
        assert after_date == datetime(2024, 2, 1, 0, 0, 0)
        assert before_date == datetime(2024, 2, 29, 23, 59, 59, 999999)

    def test_year_boundary_weekly(self):
        test_date = datetime(2023, 12, 31)  # Sunday
        after_date, before_date = get_date_range(test_date, frequency="W")
        assert after_date == datetime(2023, 12, 25, 0, 0, 0)  # Monday
        assert before_date == datetime(2023, 12, 31, 23, 59, 59, 999999)  # Sunday

    def test_year_boundary_monthly(self):
        test_date = datetime(2023, 12, 31)
        after_date, before_date = get_date_range(test_date, frequency="ME")
        assert after_date == datetime(2023, 12, 1, 0, 0, 0)
        assert before_date == datetime(2023, 12, 31, 23, 59, 59, 999999)

    def test_year_boundary_yearly(self):
        test_date = datetime(2023, 12, 31)
        after_date, before_date = get_date_range(test_date, frequency="Y")
        assert after_date == datetime(2023, 1, 1, 0, 0, 0)
        assert before_date == datetime(2023, 12, 31, 23, 59, 59, 999999)

    def test_end_of_november_month(self):
        test_date = datetime(2023, 11, 30, 0,0,0)
        after_date, before_date = get_date_range(test_date, frequency="ME")
        assert after_date == datetime(2023, 11, 1, 0, 0, 0)
        assert before_date == datetime(2023, 11, 30, 23, 59, 59, 999999)


class TestGetIsoDateStrings:

    def test_get_iso_date_strings(self):
        date_str = "2023-10-01T12:00:00Z"
        year, month, day = get_iso_date_strings(date_str)
        assert year == "2023"
        assert month == "2023-10"
        assert day == "2023-10-01"

    def test_get_iso_date_strings_invalid_format(self):
        with pytest.raises(ValueError):
            get_iso_date_strings("invalid-date-format")

    def test_get_iso_date_strings_none(self):
        with pytest.raises(ValueError):
            get_iso_date_strings(None)  # Should raise ValueError for None input