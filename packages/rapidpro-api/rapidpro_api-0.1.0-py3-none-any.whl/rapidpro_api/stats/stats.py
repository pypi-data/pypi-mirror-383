import time
from typing import Dict, Any, Optional, Union

class Stats:
  """
  A statistics collection class for tracking timers, counters, ratios, and attributes.
  
  This class provides functionality to:
  - Track execution times with named timers
  - Count events with optional units
  - Calculate ratios between timers/counters
  - Store arbitrary attributes
  - Export all data as a flat dictionary
  
  Examples:
    >>> stats = Stats()
    
    # Timer usage
    >>> stats.start_timer("processing")
    >>> # ... do some work ...
    >>> stats.end_timer("processing")
    
    # Cumulative timer usage
    >>> stats.start_cumulative_timer("data_load")
    >>> # ... load some data ...
    >>> stats.end_cumulative_timer("data_load")
    >>> # ... do other work ...
    >>> stats.start_cumulative_timer("data_load")
    >>> # ... load even more data ...
    >>> accumulated_time = stats.end_cumulative_timer("data_load")

    # Counter usage
    >>> stats.count("items_processed", 10, "items")
    >>> stats.count("items_processed", 5)  # adds to existing
    
    # Ratio calculation
    >>> stats.ratio("success_rate", "successful_items", "total_items")
    
    # Attributes
    >>> stats.add_attribute("version", "1.0.0")
    
    # Export all data
    >>> data = stats.to_dict()
  """

  def __init__(self):
        self._timers = {}  # {name: {'start': time, 'end': time, 'elapsed': duration}}
        self._cumulative_timers = {} # {name: {'start': time, 'accumulated': total_duration}}
        self._counters = {}  # {name: {'value': amount, 'unit': unit}}
        self._ratios = {}  # {name: {'numerator': name, 'denominator': name, 'value': ratio}}
        self._attributes = {}  # {name: value}
        self._names_used = set()  # Track all names to ensure uniqueness

  def set_timer(self, name: str) -> None:
    """
    Defines a new timer with the given name, but does not start it.
    This is useful for pre-defining timers before starting them, for example if you use them 
    for a ratio (which requires numerator and denominator to be pre-defined).

    Args:
      name: Unique name for the timer
    Raises:
      ValueError: If the timer name is already used by a timer or counter
    Examples:
      >>> stats = Stats()
      >>> stats.set_timer("api_call")
      >>> stats.start_timer("api_call")
      >>> # ... do some work ...
      >>> elapsed = stats.end_timer("api_call")
      
    """
    if name in self._names_used:
      raise ValueError(f"Name '{name}' is already in use")
    
    self._names_used.add(name)
    self._timers[name] = {
      'start': None,
      'end': None,
      'elapsed': 0.0
    }

  def start_timer(self, name: str) -> None:
    """
    Start a timer with the given name.
    
    Args:
      name: Unique name for the timer
      
    Raises:
      ValueError: If the name is already used by a timer or counter
      
    Examples:
      >>> stats = Stats()
      >>> stats.start_timer("api_call")
    """
    if name in self._names_used and name not in self._timers:
      raise ValueError(f"Name '{name}' is already in use")

    current_time = time.time()
    self._timers[name] = {
      'start': current_time,
      'end': None,
      'elapsed': 0.0
    }
    self._names_used.add(name)

  def stop_timer(self, name: str) -> float:
    """
    Alias for end_timer to stop a timer and get elapsed time.
    """
    return self.end_timer(name)

  def end_timer(self, name: str) -> float:
    """
    End a timer and calculate elapsed time.
    
    Args:
      name: Name of the timer to end
      
    Returns:
      Elapsed time in seconds
      
    Raises:
      ValueError: If timer doesn't exist or wasn't started
      
    Examples:
      >>> stats = Stats()
      >>> stats.start_timer("task")
      >>> elapsed = stats.end_timer("task")
    """
    if name not in self._timers:
      raise ValueError(f"Timer '{name}' does not exist")

    timer = self._timers[name]
    if timer['start'] is None:
      raise ValueError(f"Timer '{name}' was not started")

    current_time = time.time()
    elapsed = current_time - timer['start']

    timer['end'] = current_time
    timer['elapsed'] = elapsed

    return elapsed


  def set_cumulative_timer(self, name: str) -> None:
    """
    Defines a new cumulative timer with the given name, but does not start it.
    This is useful for pre-defining timers before starting them, for example if you use them 
    for a ratio (which requires numerator and denominator to be pre-defined).

    Args:
      name: Unique name for the cumulative timer
    Raises:
      ValueError: If the timer name is already used by a timer or counter
    Examples:
      >>> stats = Stats()
      >>> stats.set_cumulative_timer("data_load")
      >>> stats.start_cumulative_timer("data_load")
      >>> # ... load some data ...
      >>> stats.end_cumulative_timer("data_load")
      >>> # ... do other work ...
      >>> stats.start_cumulative_timer("data_load")
      >>> # ... load even more data ...
      >>> accumulated_time = stats.end_cumulative_timer("data_load")
      
    """
    if name in self._names_used:
        raise ValueError(f"Name '{name}' is already in use")
    self._names_used.add(name)
    self._cumulative_timers[name] = {
        'start': None,
        'accumulated': 0.0  # Initialize elapsed to 0 for accumulation
    }
    

  def start_cumulative_timer(self, name: str ) -> None:
    """
    Start an cumulative timer. This allows multiple start-end cycles to accumulate total time.
    
    Args:
      name: Unique name for the cumulative timer
    Raises:
      ValueError: If the name is already used by a timer or counter 
    Examples:
      >>> stats = Stats()
      >>> stats.start_cumulative_timer("data_processing")
      >>> # ... do some work ...
      >>> stats.end_cumulative_timer("data_processing")
      >>> # ... do more work ...
      >>> stats.start_cumulative_timer("data_processing")
      >>> # ... do even more work ...
      >>> stats.end_cumulative_timer("data_processing")
    """
    if name in self._names_used and name not in self._cumulative_timers:
        raise ValueError(f"Name '{name}' is already in use")
      
    current_time = time.time()
    if name not in self._cumulative_timers:
        self._cumulative_timers[name] = {
            'start': current_time,
            'accumulated': 0.0  # Initialize elapsed to 0 for accumulation
        }
        self._names_used.add(name)
    else:
      # if timer not started
      if self._cumulative_timers[name]['start'] is None:
            self._cumulative_timers[name]['start'] = current_time
      return
  
  def get_elapsed_time(self, name: str) -> float:
    """
    Get the elapsed time for a timer. The timer can be either cumulative or "normal".
    if the timer is still running, returns the elapsed time up to now (does not stop the timer).
    if the timer was ended, returns the total elapsed time.
    
    Args:
      name: Name of the timer
      
    Returns:
      Elapsed time in seconds
      
    Raises:
      ValueError: If timer doesn't exist.
      
    Examples:
        >>> stats = Stats()
        >>> # for a normal timer
        >>> stats.start_timer("task")
        >>> # ... do some work ...
        >>> stats.get_elapsed_time("task")  # returns elapsed time so far
        >>> # ... do some more work ...
        >>> stats.end_timer("task")
        >>> elapsed = stats.get_elapsed_time("task")
        >>> # for a cumulative timer
        >>> stats.start_cumulative_timer("data_load")
        >>> # some time passes...
        >>> elapsed = stats.get_elapsed_time("data_load")
    """
    if (name not in self._timers) and (name not in self._cumulative_timers):
        raise ValueError(f"Timer '{name}' does not exist")

    if name in self._cumulative_timers:
        return self._get_elapsed_for_cumulative_timer(name)
    return self._get_elapsed_for_timer(name)

  def _get_elapsed_for_timer(self, name:str) -> float:
        """Helper method to get elapsed time for a normal timer.
        NOTE: Does not check if timer exists.
        Args:
            name: Name of the timer
        Returns:
            Elapsed time in seconds since start, or 0 if not started
        """
        timer = self._timers[name]
        if timer['start'] is None:
            return 0.0  # Timer was never started

        if timer['elapsed'] != 0.0: # timer completed -> return elapsed
            return timer['elapsed']
        # if timer not ended, calculate elapsed time up to now
        if timer['end'] is None:
            return time.time() - timer['start']
        else:
            return timer['end'] - timer['start']


  def _get_elapsed_for_cumulative_timer(self, name: str) -> float:
    """Helper method to get elapsed time for a cumulative timer.
    NOTE: Does not check if timer exists.
    Args:
      name: Name of the cumulative timer
    Returns:
      Elapsed time in seconds since last start, or 0 if not running
    """
    timer = self._cumulative_timers[name]
    if timer['start'] is None:
        return 0.0  # Timer not running
    return time.time() - timer['start']
  
  def get_accumulated_time(self, name: str) -> float:
    """Helper method to get total accumulated time for a cumulative timer.
    NOTE: Does not check if timer exists.
    Args:
      name: Name of the cumulative timer
    Returns:
      Total accumulated time in seconds
    """
    elapsed = self._get_elapsed_for_cumulative_timer(name)
    return self._cumulative_timers[name]['accumulated'] + elapsed


  def end_cumulative_timer(self, name: str, return_elapsed=False) -> float:
    """
    End an cumulative timer and add to total elapsed time.
    
    Args:
        name: Name of the cumulative timer to end
        return_elapsed: If True, returns the elapsed time for this session only. If False 
            (default), returns the total accumulated time.
    Returns:
      Total accumulated time or this session elapsed time if return_elapsed is True
    Raises:
      ValueError: If timer doesn't exist or wasn't started
    Examples:
      >>> stats = Stats()
      >>> stats.start_cumulative_timer("data_processing")
      >>> # ... do some work (10 seconds)...
      >>> total_elapsed = stats.end_cumulative_timer("data_processing")
      >>> # total_elapsed is 10 seconds
      >>> #... do more work ...
      >>> stats.start_cumulative_timer("data_processing")
      >>> # ... do more work (5 seconds)...
      >>> session_elapsed = stats.end_cumulative_timer("data_processing", return_elapsed=True)
      >>> # session_elapsed is 5 seconds 
      >>> total = stats.get_accumulated_time("data_processing")
      >>> # total is 15 seconds

    """
    if name not in self._cumulative_timers:
        raise ValueError(f"Timer '{name}' does not exist")
    elapsed = self._get_elapsed_for_cumulative_timer(name)
    self._cumulative_timers[name]['accumulated'] = self._cumulative_timers[name]['accumulated'] + elapsed
    self._cumulative_timers[name]['start'] = None  # Reset start to None to indicate it's not running
    return elapsed if return_elapsed else self._cumulative_timers[name]['accumulated'] 


  def count(self, counter_name: str, amount: Union[int, float], unit: Optional[str] = None) -> None:
    """
    Add to a counter or create a new one.
    
    Args:
      counter_name: Unique name for the counter
      amount: Amount to add to the counter
      unit: Optional unit description
      
    Raises:
      ValueError: If the name is already used by a timer
      
    Examples:
      >>> stats = Stats()
      >>> stats.count("requests", 1, "requests")
      >>> stats.count("requests", 5, "requests")  # now total is 6
      >>> stats.count("bytes", 1024, "bytes")
    """
    if counter_name in self._timers:
        raise ValueError(f"Name '{counter_name}' is already used by a timer")

    if counter_name not in self._counters:
        self._counters[counter_name] = {'value': 0, 'unit': unit}
        self._names_used.add(counter_name)

    self._counters[counter_name]['value'] += amount

    # Update unit if provided
    if unit is not None:
        self._counters[counter_name]['unit'] = unit

  def get_counter_value(self, counter_name: str) -> Union[int, float]:
    """
    Get the current value of a counter.
    
    Args:
      counter_name: Name of the counter
      
    Returns:
      Current counter value
      
    Raises:
      ValueError: If counter doesn't exist
      
    Examples:
      >>> stats = Stats()
      >>> stats.count("items", 10)
      >>> value = stats.get_counter_value("items")  # 10
    """
    if counter_name not in self._counters:
        raise ValueError(f"Counter '{counter_name}' does not exist")

    return self._counters[counter_name]['value']

  def get_counter_unit(self, counter_name: str) -> Optional[str]:
    """
    Get the unit of a counter.
    
    Args:
      counter_name: Name of the counter
      
    Returns:
      Counter unit or None if not set
      
    Raises:
      ValueError: If counter doesn't exist
    Examples:
      >>> stats = Stats()
      >>> stats.count("items", 10, "pieces")
      >>> unit = stats.get_counter_unit("items")  # "pieces"
    """
    if counter_name not in self._counters:
        raise ValueError(f"Counter '{counter_name}' does not exist")

    return self._counters[counter_name]['unit']

  def set_counter_unit(self, counter_name: str, unit: str) -> None:
    """
    Set or update the unit of a counter.
    
    Args:
      counter_name: Name of the counter
      unit: Unit description to set for the counter
    Raises:
      ValueError: If counter doesn't exist
    Examples:
      >>> stats = Stats()
      >>> stats.count("items", 10)
      >>> stats.set_counter_unit("items", "pieces")
      >>> unit = stats.get_counter_unit("items")  # "pieces"
    """
    if counter_name not in self._counters:
        raise ValueError(f"Counter '{counter_name}' does not exist")

    self._counters[counter_name]['unit'] = unit


  def set_ratio(self, ratio_name: str, numerator: str, denominator: str) -> None:
    """
    Add a ratio definition between two timers or counters.
    The ratio is not calculated until requested.
    Before using a ratio, ensure that both numerator and denominator timers/counters 
    have been defined.

    Args:
      ratio_name: Name for this ratio
      numerator: Name of timer/counter to use as numerator
      denominator: Name of timer/counter to use as denominator
      
    Raises:
      ValueError: If numerator or denominator don't exist
      
    Examples:
      >>> stats = Stats()
      >>> stats.count("success", 80)
      >>> stats.count("total", 100)
      >>> stats.set_ratio("success_rate", "success", "total")
      >>> #
      >>> # with timers, you can do:
      >>> stats.start_timer("num")
      >>> stats.end_timer("den")
      >>> stats.set_ratio("ratio", "num", "den")
      >>> #
      >>> # or set them first
      >>> stats.set_timer("num")
      >>> stats.set_timer("den")
      >>> stats.set_ratio("ratio", "num", "den")
      >>> # 
      >>> # then to calculate the ratio:
      >>> ratio = stats.calculate_ratio("ratio")
    """
    if numerator not in self._timers and numerator not in self._counters and numerator not in self._cumulative_timers:
        raise ValueError(f"Numerator '{numerator}' not found in timers or counters")
    
    if denominator not in self._timers and denominator not in self._counters and denominator not in self._cumulative_timers:
        raise ValueError(f"Denominator '{denominator}' not found in timers or counters")
    
    self._ratios[ratio_name] = {
        'numerator': numerator,
        'denominator': denominator,
        'value': None
    }
  

  def calculate_ratio(self, ratio_name: str) -> float:
    """
    Calculate the value of a previously defined ratio.
    
    Args:
      ratio_name: Name of the ratio to calculate
      
    Returns:
      Calculated ratio value
      
    Raises:
      ValueError: If ratio doesn't exist, timer not completed, or denominator is zero
      
    Examples:
      >>> stats = Stats()
      >>> stats.count("success", 80)
      >>> stats.count("total", 100)
      >>> stats.add_ratio("success_rate", "success", "total")
      >>> ratio = stats.calculate_ratio("success_rate")  # 0.8
    """
    if ratio_name not in self._ratios:
        raise ValueError(f"Ratio '{ratio_name}' does not exist")
    
    ratio_def = self._ratios[ratio_name]
    numerator = ratio_def['numerator']
    denominator = ratio_def['denominator']
    
    def get_value(name: str) -> float:
        if name in self._timers:
            timer = self._timers[name]
            return self.get_elapsed_time(name)
        elif name in self._counters:
            return self._counters[name]['value']
        elif name in self._cumulative_timers:
            return self.get_accumulated_time(name)
        else:
            raise ValueError(f"'{name}' not found in timers or counters")

    num_value = get_value(numerator)
    den_value = get_value(denominator)

    if den_value == 0:
        return 0.0
        #raise ValueError(f"Denominator '{denominator}' cannot be zero")

    ratio_value = num_value / den_value
    self._ratios[ratio_name]['value'] = ratio_value

    return ratio_value


  def set_attribute(self, name: str, value: str) -> None:
    """
    Add an attribute (key-value pair).
    If the attribute already exists, it will be overwritten.
    Args:
      name: Attribute name
      value: Attribute value
      
    Examples:
      >>> stats = Stats()
      >>> stats.add_attribute("version", "1.2.3")
      >>> stats.add_attribute("environment", "production")
    """
    self._attributes[name] = value


  def to_dict(self) -> Dict[str, Any]:
    """
    Export all statistics as a flat dictionary.
    
    For time accumulators, returns the total accumulated time. If the timer is currently running, 
    it adds the elapsed time since it was started to the accumulated time.

    Returns:
      Dictionary containing all timers, counters, ratios, and attributes
      
    Examples:
      >>> stats = Stats()
      >>> stats.start_timer("task")
      >>> stats.end_timer("task")
      >>> stats.count("items", 5, "pieces")
      >>> stats.add_attribute("version", "1.0")
      >>> data = stats.to_dict()
      >>> # Returns: {
      >>> #   'start_task_time': 1234567890.123,
      >>> #   'end_task_time': 1234567891.456,
      >>> #   'items_count': 5,
      >>> #   'items_count_unit': 'pieces',
      >>> #   'version': '1.0'
      >>> # }
    """
    result = {}

    # Add timer data
    for name, timer in self._timers.items():
        if timer['start'] is not None:
            result[f'start_{name}'] = timer['start']
            result[f'start_{name}_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timer['start']))

        if timer['end'] is None:
            result[f'end_{name}'] = time.time()
            # convert to iso datetime string in UTC
            result[f'end_{name}_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result[f'end_{name}']))
        else: 
            result[f'end_{name}'] = timer['end']
            result[f'end_{name}_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timer['end']))
        result[f'{name}_elapsed'] = self.get_elapsed_time(name)

    # Add counter data
    for name, counter in self._counters.items():
        result[f'{name}'] = counter['value']
        result[f'{name}_unit'] = counter['unit'] or "unit"

    # Add ratio data
    for name, ratio in self._ratios.items():
        result[f'{name}'] = self.calculate_ratio(name)
        # Add unit as combination of numerator and denominator units if available
        num_unit = self._get_unit_for_name(ratio['numerator'])
        den_unit = self._get_unit_for_name(ratio['denominator'])
        if num_unit and den_unit and num_unit == den_unit:
            result[f'{name}_unit'] = ""
        else:
            result[f'{name}_unit'] = f"{num_unit}s/{den_unit}"
    
    for name, timer in self._cumulative_timers.items():
        # if timer started, add elapsed time to accumulated
        result[f'{name}'] = self.get_accumulated_time(name)
    # Add attributes
    result.update(self._attributes)
    return result

  def _get_unit_for_name(self, name: str) -> Optional[str]:
    """Helper method to get unit for a timer or counter name."""
    if name in self._counters:
      return self._counters[name]['unit'] or "unit"
    if name in self._timers:
      return "second"
    if name in self._cumulative_timers:
      return "second"
    return None


  def __str__(self) -> str:
    """
    Return a human-readable string representation of all statistics.
    
    Returns:
      Formatted string containing all timers, counters, ratios, and attributes
      
    Examples:
      >>> stats = Stats()
      >>> stats.start_timer("task")
      >>> stats.end_timer("task")
      >>> stats.count("items", 5, "pieces")
      >>> stats.set_attribute("version", "1.0")
      >>> print(stats)
    """
    data = self.to_dict()
    if not data:
        return "Stats: (empty)"

    lines = ["Stats:"]
    for key, value in sorted(data.items()):
        if isinstance(value, float):
            formatted_value = f"{value:.4f}"
        else:
            formatted_value = str(value)
        lines.append(f"  {key}: {formatted_value}")
    
    return "\n".join(lines)