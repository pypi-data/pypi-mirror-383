import pytest
import time
from rapidpro_api.stats import Stats

class TestStats:
    def test_init(self):
        """Test Stats initialization."""
        stats = Stats()
        assert stats._timers == {}
        assert stats._cumulative_timers == {}
        assert stats._counters == {}
        assert stats._ratios == {}
        assert stats._attributes == {}
        assert stats._names_used == set()

    def test_set_timer_success(self):
        """Test setting a timer successfully."""
        stats = Stats()
        stats.set_timer("test_timer")
        
        assert "test_timer" in stats._timers
        assert stats._timers["test_timer"]["start"] is None
        assert stats._timers["test_timer"]["end"] is None
        assert stats._timers["test_timer"]["elapsed"] == 0
        assert "test_timer" in stats._names_used

    def test_set_timer_duplicate_name(self):
        """Test setting a timer with duplicate name raises error."""
        stats = Stats()
        stats.set_timer("test_timer")
        
        with pytest.raises(ValueError, match="Name 'test_timer' is already in use"):
            stats.set_timer("test_timer")

    def test_set_timer_name_conflict_with_counter(self):
        """Test timer name conflicts with existing counter."""
        stats = Stats()
        stats.count("test_name", 5)
        
        with pytest.raises(ValueError, match="Name 'test_name' is already in use"):
            stats.set_timer("test_name")

    def test_set_timer_then_start_timer(self, monkeypatch):
        """Test setting a timer then starting it works correctly."""
        stats = Stats()
        monkeypatch.setattr(time, 'time', lambda: 1000.0)
        
        stats.set_timer("test_timer")
        stats.start_timer("test_timer")
        
        assert stats._timers["test_timer"]["start"] == 1000.0
        assert stats._timers["test_timer"]["end"] is None
        assert stats._timers["test_timer"]["elapsed"] == 0

    def test_set_timer_for_ratio_preparation(self):
        """Test setting timers for ratio preparation."""
        stats = Stats()
        stats.set_timer("timer1")
        stats.set_timer("timer2")
        
        # Should be able to set ratio with pre-defined timers
        stats.set_ratio("time_ratio", "timer1", "timer2")
        assert "time_ratio" in stats._ratios

    def test_start_timer_success(self, monkeypatch):
        """Test starting a timer successfully."""
        stats = Stats()
        monkeypatch.setattr(time, 'time', lambda: 1000.0)
        stats.start_timer("test_timer")
        assert "test_timer" in stats._timers
        assert stats._timers["test_timer"]["start"] == 1000.0
        assert stats._timers["test_timer"]["end"] is None
        assert stats._timers["test_timer"]["elapsed"] == 0.0
        assert "test_timer" in stats._names_used


    def test_start_timer_duplicate_name(self):
        """Test starting a timer with duplicate name raises error."""
        stats = Stats()
        stats._names_used.add("test_timer")
        
        with pytest.raises(ValueError, match="Name 'test_timer' is already in use"):
            stats.start_timer("test_timer")


    def test_end_timer_success(self, monkeypatch):
        """Test ending a timer successfully."""
        stats = Stats()
        time_values = iter([1000.0, 1005.0])
        monkeypatch.setattr(time, 'time', lambda: next(time_values))
        
        stats.start_timer("test_timer")
        elapsed = stats.end_timer("test_timer")
        
        assert elapsed == 5.0
        assert stats._timers["test_timer"]["end"] == 1005.0
        assert stats._timers["test_timer"]["elapsed"] == 5.0


    def test_end_timer_not_exists(self):
        """Test ending a non-existent timer raises error."""
        stats = Stats()
        with pytest.raises(ValueError, match="Timer 'test_timer' does not exist"):
            stats.end_timer("test_timer")


    def test_end_timer_not_started(self):
        """Test ending a timer that wasn't started raises error."""
        stats = Stats()
        stats._timers["test_timer"] = {"start": None, "end": None, "elapsed": None}
        
        with pytest.raises(ValueError, match="Timer 'test_timer' was not started"):
            stats.end_timer("test_timer")


    def test_set_cumulative_timer_success(self):
        """Test setting a cumulative timer successfully."""
        stats = Stats()
        stats.set_cumulative_timer("test_cumulative_timer")
            
        assert "test_cumulative_timer" in stats._cumulative_timers
        assert stats._cumulative_timers["test_cumulative_timer"]["start"] is None
        assert stats._cumulative_timers["test_cumulative_timer"]["accumulated"] == 0.0
        assert "test_cumulative_timer" in stats._names_used

    def test_set_cumulative_timer_duplicate_name(self):
        """Test setting a cumulative timer with duplicate name raises error."""
        stats = Stats()
        stats.set_cumulative_timer("test_cumulative_timer")
            
        with pytest.raises(ValueError, match="Name 'test_cumulative_timer' is already in use"):
            stats.set_cumulative_timer("test_cumulative_timer")

    def test_set_cumulative_timer_name_conflict(self):
        """Test cumulative timer name conflicts with existing timer."""
        stats = Stats()
        stats._names_used.add("test_name")
            
        with pytest.raises(ValueError, match="Name 'test_name' is already in use"):
            stats.set_cumulative_timer("test_name")


    def test_set_cumulative_timer_then_start_cumulative_timer(self, monkeypatch):
        """Test setting a cumulative timer then starting it works correctly."""
        stats = Stats()
        monkeypatch.setattr(time, 'time', lambda: 1000.0)
            
        stats.set_cumulative_timer("test_cumulative_timer")
        stats.start_cumulative_timer("test_cumulative_timer")
            
        assert stats._cumulative_timers["test_cumulative_timer"]["start"] == 1000.0
        assert stats._cumulative_timers["test_cumulative_timer"]["accumulated"] == 0.0

    def test_set_cumulative_timer_for_ratio_preparation(self):
        """Test setting cumulative timers for ratio preparation."""
        stats = Stats()
        stats.set_cumulative_timer("cumulative_timer1")
        stats.set_cumulative_timer("cumulative_timer2")
            
        # Should be able to set ratio with pre-defined cumulative timers
        stats.set_ratio("cumulative_time_ratio", "cumulative_timer1", "cumulative_timer2")
        assert "cumulative_time_ratio" in stats._ratios

    def test_start_cumulative_timer_success(self, monkeypatch):
        """Test starting a cumulative timer successfully."""
        stats = Stats()
        monkeypatch.setattr(time, 'time', lambda: 2000.0)
        stats.start_cumulative_timer("cumulative_timer")
        stats.start_timer("test_timer")
        assert "cumulative_timer" in stats._cumulative_timers
        assert "cumulative_timer" in stats._names_used
        assert stats._cumulative_timers["cumulative_timer"]["start"] == 2000.0  # Simulate start time
        assert stats._cumulative_timers["cumulative_timer"]["accumulated"] == 0.0  # Simulate previous accumulated time


    def test_start_cumulative_timer_duplicate_name(self):
        """Test starting a cumulative timer with duplicate name raises error."""
        stats = Stats()
        stats._names_used.add("cumulative_timer")
        with pytest.raises(ValueError, match="Name 'cumulative_timer' is already in use"):
            stats.start_cumulative_timer("cumulative_timer")  


    def test_start_cumulative_timer_already_running(self, monkeypatch):
        """Test starting a cumulative timer that is already running does nothing."""
        stats = Stats()
        time_values = iter([3000.0, 3005.0])
        monkeypatch.setattr(time, 'time', lambda: next(time_values))
        
        stats.start_cumulative_timer("cumulative_timer")
        initial_start = stats._cumulative_timers["cumulative_timer"]["start"]
        stats.start_cumulative_timer("cumulative_timer")  # Should do nothing
        assert stats._cumulative_timers["cumulative_timer"]["start"] == initial_start  # Start time should remain unchanged 
        assert stats._cumulative_timers["cumulative_timer"]["accumulated"] == 0.0  # Accumulated time should remain unchanged

    def test_get_accumulated_time_started(self):
        """Test getting accumulated time for a running cumulative timer."""
        stats = Stats()
        stats._cumulative_timers["cumulative_timer"] = {
        "start": 1000.0,
        "accumulated": 10.0
        }
        # Simulate current time
        current_time = 1010.0
        original_time = time.time
        time.time = lambda: current_time
        
        accumulated = stats.get_accumulated_time("cumulative_timer")
        assert accumulated == 20.0  # 10 previous + (1010 - 1000)
        
        # Restore original time function
        time.time = original_time 


    def test_get_accumulated_time_not_started(self):
        """Test getting accumulated time for a non-running cumulative timer."""
        stats = Stats()
        stats._cumulative_timers["cumulative_timer"] = {
        "start": None,
        "accumulated": 15.0
        }
        accumulated = stats.get_accumulated_time("cumulative_timer")
        assert accumulated == 15.0  # Just the previous accumulated time


    def test_end_cumulative_timer_success(self, monkeypatch):
        """Test ending a cumulative timer successfully."""
        stats = Stats()
        time_values = iter([2000.0, 2005.0, 2020.0, 2025.0])
        monkeypatch.setattr(time, 'time', lambda: next(time_values))
        
        stats.start_cumulative_timer("cumulative_timer")
        elapsed1 = stats.end_cumulative_timer("cumulative_timer")
        assert elapsed1 == 5.0
        assert stats._cumulative_timers["cumulative_timer"]["accumulated"] == 5.0
        assert stats._cumulative_timers["cumulative_timer"]["start"] is None  # Should be reset after ending

        stats.start_cumulative_timer("cumulative_timer")
        assert stats._cumulative_timers["cumulative_timer"]["start"] == 2020.0  # New start time
        assert stats._cumulative_timers["cumulative_timer"]["accumulated"] == 5.0  # Previous accumulated time remains
        elapsed2 = stats.end_cumulative_timer("cumulative_timer")
        assert elapsed2 == 10.0
        assert stats._cumulative_timers["cumulative_timer"]["accumulated"] == 10.0


    def test_end_cumulative_timer_not_exists(self):
        """Test ending a non-existent cumulative timer raises error."""
        stats = Stats()
        with pytest.raises(ValueError, match="Timer 'cumulative_timer' does not exist"):
            stats.end_cumulative_timer("cumulative_timer")


    def test_end_cumulative_timer_not_started(self):
        """Test ending a cumulative timer that wasn't started raises error."""
        stats = Stats()
        stats._cumulative_timers["cumulative_timer"] = {"start": None, "accumulated": 0.0}
        
        stats.end_cumulative_timer("cumulative_timer")  # Should not raise error, just return 0.0
        assert stats._cumulative_timers["cumulative_timer"]["accumulated"] == 0.0
        assert stats._cumulative_timers["cumulative_timer"]["start"] is None

        
    def test_count_new_counter(self):
        """Test creating a new counter."""
        stats = Stats()
        stats.count("requests", 5, "items")
        
        assert "requests" in stats._counters
        assert stats._counters["requests"]["value"] == 5
        assert stats._counters["requests"]["unit"] == "items"
        assert "requests" in stats._names_used

    def test_count_existing_counter(self):
        """Test adding to an existing counter."""
        stats = Stats()
        stats.count("requests", 5, "items")
        stats.count("requests", 3, "items")
        
        assert stats._counters["requests"]["value"] == 8
        assert stats._counters["requests"]["unit"] == "items"

    def test_count_update_unit(self):
        """Test updating unit of existing counter."""
        stats = Stats()
        stats.count("data", 100, "bytes")
        stats.count("data", 50, "kilobytes")
        
        assert stats._counters["data"]["value"] == 150
        assert stats._counters["data"]["unit"] == "kilobytes"

    def test_count_no_unit(self):
        """Test counter without unit."""
        stats = Stats()
        stats.count("events", 10)
        
        assert stats._counters["events"]["value"] == 10
        assert stats._counters["events"]["unit"] is None

    def test_count_name_conflict_with_timer(self):
        """Test counter name conflicts with timer."""
        stats = Stats()
        stats.start_timer("test_name")
        
        with pytest.raises(ValueError, match="Name 'test_name' is already used by a timer"):
            stats.count("test_name", 5)

    def test_set_ratio_success(self):
        """Test adding a ratio successfully."""
        stats = Stats()
        stats.count("success", 80)
        stats.count("total", 100)
        stats.set_ratio("success_rate", "success", "total")
        
        assert "success_rate" in stats._ratios
        assert stats._ratios["success_rate"]["numerator"] == "success"
        assert stats._ratios["success_rate"]["denominator"] == "total"
        assert stats._ratios["success_rate"]["value"] is None

    def test_set_ratio_with_timers(self, monkeypatch):
        """Test adding a ratio with timers."""
        stats = Stats()
        time_values = iter([1000.0, 1005.0, 1010.0, 1020.0])
        monkeypatch.setattr(time, 'time', lambda: next(time_values))
        
        stats.start_timer("timer1")
        stats.end_timer("timer1")
        stats.start_timer("timer2")
        stats.end_timer("timer2")
        
        stats.set_ratio("time_ratio", "timer1", "timer2")
        assert "time_ratio" in stats._ratios

    def test_set_ratio_numerator_not_found(self):
        """Test adding ratio with non-existent numerator."""
        stats = Stats()
        stats.count("total", 100)
        
        with pytest.raises(ValueError, match="Numerator 'nonexistent' not found"):
            stats.set_ratio("test_ratio", "nonexistent", "total")

    def test_set_ratio_denominator_not_found(self):
        """Test adding ratio with non-existent denominator."""
        stats = Stats()
        stats.count("success", 80)
        
        with pytest.raises(ValueError, match="Denominator 'nonexistent' not found"):
            stats.set_ratio("test_ratio", "success", "nonexistent")

    def test_calculate_ratio_with_counters(self):
        """Test calculating ratio with counters."""
        stats = Stats()
        stats.count("success", 80)
        stats.count("total", 100)
        stats.set_ratio("success_rate", "success", "total")
        
        ratio = stats.calculate_ratio("success_rate")
        assert ratio == 0.8
        assert stats._ratios["success_rate"]["value"] == 0.8

    def test_calculate_ratio_with_timers(self, monkeypatch):
        """Test calculating ratio with timers."""
        stats = Stats()
        time_values = iter([1000.0, 1002.0, 1010.0, 1014.0])
        monkeypatch.setattr(time, 'time', lambda: next(time_values))
        
        stats.start_timer("timer1")
        stats.end_timer("timer1")  # 2 seconds
        stats.start_timer("timer2")
        stats.end_timer("timer2")  # 4 seconds
        
        stats.set_ratio("time_ratio", "timer1", "timer2")
        ratio = stats.calculate_ratio("time_ratio")
        assert ratio == 0.5

    def test_calculate_ratio_not_exists(self):
        """Test calculating non-existent ratio."""
        stats = Stats()
        
        with pytest.raises(ValueError, match="Ratio 'nonexistent' does not exist"):
            stats.calculate_ratio("nonexistent")

    def test_calculate_ratio_timer_not_completed(self):
        """Test calculating ratio with incomplete timer."""
        stats = Stats()
        stats.start_timer("timer1")
        stats.count("total", 100)
        stats.set_ratio("test_ratio", "timer1", "total")
        stats.calculate_ratio("test_ratio") == 0.0  # Should not raise error, just return 0.0

    def test_calculate_ratio_zero_denominator(self):
        """Test calculating ratio with zero denominator."""
        stats = Stats()
        stats.count("success", 80)
        stats.count("total", 0)
        stats.set_ratio("success_rate", "success", "total")
        
        assert stats.calculate_ratio("success_rate") == 0.0  # Should not raise error, just return 0.0

    def test_set_attribute(self):
        """Test adding attributes."""
        stats = Stats()
        stats.set_attribute("version", "1.2.3")
        stats.set_attribute("environment", "production")
        
        assert stats._attributes["version"] == "1.2.3"
        assert stats._attributes["environment"] == "production"

    def test_to_dict_empty(self):
        """Test to_dict with empty stats."""
        stats = Stats()
        result = stats.to_dict()
        assert result == {}

    def test_to_dict_with_timers(self, monkeypatch):
        """Test to_dict with timers."""
        stats = Stats()
        time_values = iter([1000.0, 1005.0])
        monkeypatch.setattr(time, 'time', lambda: next(time_values))
        
        stats.start_timer("test_timer")
        stats.end_timer("test_timer")
        
        result = stats.to_dict()
        assert result["start_test_timer"] == 1000.0
        assert result["end_test_timer"] == 1005.0

    def test_to_dict_with_incomplete_timer(self, monkeypatch):
        """Test to_dict with incomplete timer."""
        stats = Stats()
        # calls to time.time for the following:
        # 1. Set start time to 1000.0
        # 2. Set end time to 1005.0
        # 3. Calculate elapsed as 5.0
        time_values = iter([1000.0, 1005.0, 1007.0])
        monkeypatch.setattr(time, 'time', lambda: next(time_values))
    
        stats.start_timer("test_timer")
        
        result = stats.to_dict()
        assert result["start_test_timer"] == 1000.0
        assert result["end_test_timer"] == 1005.0
        assert result["test_timer_elapsed"] == 7.0

    def test_to_dict_with_counters(self):
        """Test to_dict with counters."""
        stats = Stats()
        stats.count("requests", 10, "item")
        stats.count("bytes", 1024)
        
        result = stats.to_dict()
        assert result["requests"] == 10
        assert result["requests_unit"] == "item"
        assert result["bytes"] == 1024
        assert result["bytes_unit"] == "unit"

    def test_to_dict_with_ratios(self):
        """Test to_dict with ratios."""
        stats = Stats()
        stats.count("success", 80, "requests")
        stats.count("total", 100, "requests")
        stats.set_ratio("success_rate", "success", "total")
        stats.calculate_ratio("success_rate")
        
        result = stats.to_dict()
        assert result["success_rate"] == 0.8
        assert result["success_rate_unit"] == ""

    def test_to_dict_with_timer_ratio(self, monkeypatch):
        """Test to_dict with timer-based ratio."""
        stats = Stats()
        time_values = iter([1000.0, 1002.0, 1010.0, 1014.0])
        monkeypatch.setattr(time, 'time', lambda: next(time_values))
        
        stats.start_timer("timer1")
        stats.end_timer("timer1")
        stats.start_timer("timer2")
        stats.end_timer("timer2")
        
        stats.set_ratio("time_ratio", "timer1", "timer2")
        stats.calculate_ratio("time_ratio")
        
        result = stats.to_dict()
        assert result["time_ratio"] == 0.5
        assert result["time_ratio_unit"] == ""

    def test_to_dict_with_mixed_ratio_units(self, monkeypatch):
        """Test to_dict with ratio having different unit types."""
        stats = Stats()
        time_values = iter([1000.0, 1005.0])
        monkeypatch.setattr(time, 'time', lambda: next(time_values))
        
        stats.start_timer("processing_time")
        stats.end_timer("processing_time")
        
        stats.count("items", 100, "piece")
        stats.set_ratio("rate", "items", "processing_time")
        stats.calculate_ratio("rate")
        
        result = stats.to_dict()
        assert result["rate"] == 20.0  # 100 / 5
        assert result["rate_unit"] == "pieces/second"

    def test_to_dict_with_attributes(self):
        """Test to_dict with attributes."""
        stats = Stats()
        stats.set_attribute("version", "1.2.3")
        stats.set_attribute("environment", "production")
        
        result = stats.to_dict()
        assert result["version"] == "1.2.3"
        assert result["environment"] == "production"

    def test_to_dict_comprehensive(self, monkeypatch):
        """Test to_dict with all types of data."""
        stats = Stats()
        
        # Add timer
        time_values = iter([1000.0, 1005.0])
        monkeypatch.setattr(time, 'time', lambda: next(time_values))
        
        stats.start_timer("task")
        stats.end_timer("task")
        
        # Add counters
        stats.count("success", 80, "request")
        stats.count("total", 100, "request")
        
        # Add ratio
        stats.set_ratio("success_rate", "success", "total")
        stats.calculate_ratio("success_rate")
        
        # Add attributes
        stats.set_attribute("version", "1.0.0")
        
        result = stats.to_dict()
        
        # Check all data is present
        assert result["start_task"] == 1000.0
        assert result["end_task"] == 1005.0
        assert result["success"] == 80
        assert result["success_unit"] == "request"
        assert result["total"] == 100
        assert result["total_unit"] == "request"
        assert result["success_rate"] == 0.8
        assert result["success_rate_unit"] == ""
        assert result["version"] == "1.0.0"

    def test_get_unit_for_name_counter(self):
        """Test _get_unit_for_name with counter."""
        stats = Stats()
        stats.count("items", 10, "pieces")
        
        unit = stats._get_unit_for_name("items")
        assert unit == "pieces"


    def test_get_counter_value_success(self):
        """Test getting counter value successfully."""
        stats = Stats()
        stats.count("items", 10)
        
        value = stats.get_counter_value("items")
        assert value == 10

    def test_get_counter_value_after_multiple_counts(self):
        """Test getting counter value after multiple increments."""
        stats = Stats()
        stats.count("requests", 5)
        stats.count("requests", 3)
        stats.count("requests", 2)
        
        value = stats.get_counter_value("requests")
        assert value == 10

    def test_get_counter_value_float(self):
        """Test getting counter value with float."""
        stats = Stats()
        stats.count("temperature", 23.5)
        stats.count("temperature", 1.5)
        
        value = stats.get_counter_value("temperature")
        assert value == 25.0

    def test_get_counter_value_not_exists(self):
        """Test getting value of non-existent counter raises error."""
        stats = Stats()
        
        with pytest.raises(ValueError, match="Counter 'nonexistent' does not exist"):
            stats.get_counter_value("nonexistent")

    def test_get_counter_unit_success(self):
        """Test getting counter unit successfully."""
        stats = Stats()
        stats.count("items", 10, "pieces")
        
        unit = stats.get_counter_unit("items")
        assert unit == "pieces"

    def test_get_counter_unit_none(self):
        """Test getting counter unit when not set."""
        stats = Stats()
        stats.count("items", 10)
        
        unit = stats.get_counter_unit("items")
        assert unit is None

    def test_get_counter_unit_updated(self):
        """Test getting counter unit after update."""
        stats = Stats()
        stats.count("data", 100, "bytes")
        stats.count("data", 50, "kilobytes")
        
        unit = stats.get_counter_unit("data")
        assert unit == "kilobytes"

    def test_get_counter_unit_not_exists(self):
        """Test getting unit of non-existent counter raises error."""
        stats = Stats()
        
        with pytest.raises(ValueError, match="Counter 'nonexistent' does not exist"):
            stats.get_counter_unit("nonexistent")

    def test_set_counter_unit_success(self):
        """Test setting counter unit successfully."""
        stats = Stats()
        stats.count("items", 10)
        stats.set_counter_unit("items", "pieces")
        
        unit = stats.get_counter_unit("items")
        assert unit == "pieces"

    def test_set_counter_unit_update_existing(self):
        """Test updating existing counter unit."""
        stats = Stats()
        stats.count("data", 100, "bytes")
        stats.set_counter_unit("data", "kilobytes")
        
        unit = stats.get_counter_unit("data")
        assert unit == "kilobytes"

    def test_set_counter_unit_override_none(self):
        """Test setting unit on counter that had no unit."""
        stats = Stats()
        stats.count("events", 5)
        assert stats.get_counter_unit("events") is None
        
        stats.set_counter_unit("events", "occurrences")
        unit = stats.get_counter_unit("events")
        assert unit == "occurrences"

    def test_set_counter_unit_not_exists(self):
        """Test setting unit of non-existent counter raises error."""
        stats = Stats()
        
        with pytest.raises(ValueError, match="Counter 'nonexistent' does not exist"):
            stats.set_counter_unit("nonexistent", "pieces")

    def test_counter_methods_integration(self):
        """Test integration of all counter methods."""
        stats = Stats()
        
        # Create counter without unit
        stats.count("items", 5)
        assert stats.get_counter_value("items") == 5
        assert stats.get_counter_unit("items") is None
        
        # Set unit
        stats.set_counter_unit("items", "pieces")
        assert stats.get_counter_unit("items") == "pieces"
        
        # Add more to counter
        stats.count("items", 3, "pieces")
        assert stats.get_counter_value("items") == 8
        assert stats.get_counter_unit("items") == "pieces"
        
        # Update unit
        stats.set_counter_unit("items", "objects")
        assert stats.get_counter_unit("items") == "objects"
        assert stats.get_counter_value("items") == 8  # Value unchanged
    def test_get_unit_for_name_timer(self):
        """Test _get_unit_for_name with timer."""
        stats = Stats()
        stats.start_timer("task")
        
        unit = stats._get_unit_for_name("task")
        assert unit == "second"

    def test_get_unit_for_name_not_found(self):
        """Test _get_unit_for_name with non-existent name."""
        stats = Stats()
        
        unit = stats._get_unit_for_name("nonexistent")
        assert unit is None

    def test_float_values(self):
        """Test with float values."""
        stats = Stats()
        stats.count("temperature", 23.5, "celsius")
        stats.count("temperature", 1.5, "celsius")
        
        assert stats._counters["temperature"]["value"] == 25.0

    def test_ratio_with_uncalculated_value(self):
        """Test to_dict with uncalculated ratio."""
        stats = Stats()
        stats.count("success", 80)
        stats.count("total", 100)
        stats.set_ratio("success_rate", "success", "total")
        result = stats.to_dict()
        assert result["success_rate"] == 80/100
        