import arrow


def parse_time(datetime_input):
    """The arrow library is sadly not good enough to parse
    certain date strings. It even gives unexpected results for partial
    date strings such as '2015-01' or just '2015', which I think
    should be seen as 'the first moment of 2014'.
    This function should overcome those limitations."""
    date_els, time_els = _split_datetime(datetime_input)
    date_vals = _parse_date(date_els)
    time_vals = _parse_time(time_els)
    return arrow.get(*date_vals, *time_vals)    
    

def _split_datetime(datetime_input):
    dt_input = datetime_input.split(" ")
    if len(dt_input) == 1:
        dt_input.append("")
    date_input, time_input = dt_input
    if "/" in date_input:
        sep = "/"
    elif "-" in date_input:
        sep = "-"
    elif "." in date_input:
        sep = "."
    elif ":" in date_input:
        date_input, time_input = time_input, date_input
    else:
        raise ValueError("Date '{}' can't be understood".format(date_input))
    if time_input and ":" not in time_input:
        raise ValueError("Time '{}' has no ':'-separators".format(time_input))
    return date_input.split(sep), time_input.split(":")


def _parse_date(date_els):
    if not date_els:
        now = arrow.now()
        date_vals = now.year, now.month, now.day
    elif len(date_els) == 2:
        # assumed to be year-month or month-year
        a, b = date_els
        if _is_year(a):
            date_vals = a, b, 1  # 1st of month assumed
        elif _is_year(b):
            date_vals = b, a, 1  # 1st of month assumed
        else:
            date_vals = arrow.now().year, a, b  # assumed M/D
    elif len(date_els) == 3:
        # assumed to be year-month-day or month-day-year
        a, b, c = date_els
        if _is_year(a):
            date_vals = a, b, c
        elif _is_year(c):
            date_vals = c, a, b
    else:
        raise ValueError("Date '{}' can't be understood".format(date_els))
    return map(int, date_vals)


def _parse_time(time_els):
    if len(time_els) == 1:
        time_vals = 0, 0, 0 
    elif len(time_els) == 2:
        time_vals = *time_vals, 0  # assumed H:M
    elif len(time_els) == 3:
        time_vals = time_els  # H:M:S
    else:
        raise ValueError("Time '{}' can't be understood".format(time_els))
    return map(int, time_vals)
        

def _is_year(element):
    return len(element) == 4


