"""
Persian Date Utilities for converting Gregorian dates to Persian (Shamsi) calendar
"""

import jdatetime
from datetime import datetime, date
from typing import Union, Optional
import pytz


def to_persian_date(gregorian_date: Union[datetime, date, str], format_str: str = '%Y/%m/%d') -> str:
    """
    Convert Gregorian date to Persian (Shamsi) date string
    
    Args:
        gregorian_date: Gregorian date as datetime, date, or string
        format_str: Persian date format string (default: '%Y/%m/%d')
        
    Returns:
        Persian date string
        
    Format codes:
        %Y: 4-digit year (e.g., 1403)
        %y: 2-digit year (e.g., 03)
        %m: Month (01-12)
        %d: Day (01-31)
        %B: Full month name (e.g., فروردین)
        %b: Abbreviated month name (e.g., فر)
        %A: Full weekday name (e.g., شنبه)
        %a: Abbreviated weekday name (e.g., ش)
    """
    if gregorian_date is None:
        return ""
    
    # Handle string input
    if isinstance(gregorian_date, str):
        try:
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S']:
                try:
                    gregorian_date = datetime.strptime(gregorian_date, fmt)
                    break
                except ValueError:
                    continue
            else:
                return str(gregorian_date)  # Return original if can't parse
        except:
            return str(gregorian_date)
    
    # Convert to jdatetime
    if isinstance(gregorian_date, datetime):
        persian_date = jdatetime.datetime.fromgregorian(datetime=gregorian_date)
    elif isinstance(gregorian_date, date):
        persian_date = jdatetime.date.fromgregorian(date=gregorian_date)
    else:
        return str(gregorian_date)
    
    # Format the Persian date
    try:
        return persian_date.strftime(format_str)
    except:
        # Fallback to simple format
        return f"{persian_date.year}/{persian_date.month:02d}/{persian_date.day:02d}"


def to_persian_datetime(gregorian_datetime: Union[datetime, str], format_str: str = '%Y/%m/%d %H:%M') -> str:
    """
    Convert Gregorian datetime to Persian (Shamsi) datetime string
    
    Args:
        gregorian_datetime: Gregorian datetime as datetime or string
        format_str: Persian datetime format string (default: '%Y/%m/%d %H:%M')
        
    Returns:
        Persian datetime string
    """
    if gregorian_datetime is None:
        return ""
    
    # Handle string input
    if isinstance(gregorian_datetime, str):
        try:
            # Try common datetime formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M']:
                try:
                    gregorian_datetime = datetime.strptime(gregorian_datetime, fmt)
                    break
                except ValueError:
                    continue
            else:
                return str(gregorian_datetime)  # Return original if can't parse
        except:
            return str(gregorian_datetime)
    
    # Convert to jdatetime
    if isinstance(gregorian_datetime, datetime):
        # Remove timezone info for jdatetime (it works with naive datetime)
        if gregorian_datetime.tzinfo is not None:
            gregorian_datetime = gregorian_datetime.replace(tzinfo=None)
        
        persian_datetime = jdatetime.datetime.fromgregorian(datetime=gregorian_datetime)
    else:
        return str(gregorian_datetime)
    
    # Format the Persian datetime
    try:
        return persian_datetime.strftime(format_str)
    except:
        # Fallback to simple format
        return f"{persian_datetime.year}/{persian_datetime.month:02d}/{persian_datetime.day:02d} {persian_datetime.hour:02d}:{persian_datetime.minute:02d}"


def get_persian_month_name(month_number: int) -> str:
    """
    Get Persian month name by month number
    
    Args:
        month_number: Month number (1-12)
        
    Returns:
        Persian month name
    """
    persian_months = {
        1: 'فروردین',
        2: 'اردیبهشت',
        3: 'خرداد',
        4: 'تیر',
        5: 'مرداد',
        6: 'شهریور',
        7: 'مهر',
        8: 'آبان',
        9: 'آذر',
        10: 'دی',
        11: 'بهمن',
        12: 'اسفند'
    }
    return persian_months.get(month_number, '')


def get_persian_weekday_name(weekday_number: int) -> str:
    """
    Get Persian weekday name by weekday number (0=Saturday, 6=Friday)
    
    Args:
        weekday_number: Weekday number (0-6)
        
    Returns:
        Persian weekday name
    """
    persian_weekdays = {
        0: 'شنبه',
        1: 'یکشنبه',
        2: 'دوشنبه',
        3: 'سه‌شنبه',
        4: 'چهارشنبه',
        5: 'پنج‌شنبه',
        6: 'جمعه'
    }
    return persian_weekdays.get(weekday_number, '')


def format_persian_date_pretty(gregorian_date: Union[datetime, date, str]) -> str:
    """
    Format Persian date in a pretty, readable format
    
    Args:
        gregorian_date: Gregorian date as datetime, date, or string
        
    Returns:
        Pretty formatted Persian date string (e.g., "۱۵ فروردین ۱۴۰۳")
    """
    if gregorian_date is None:
        return ""
    
    # Handle string input
    if isinstance(gregorian_date, str):
        try:
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S']:
                try:
                    gregorian_date = datetime.strptime(gregorian_date, fmt)
                    break
                except ValueError:
                    continue
            else:
                return str(gregorian_date)
        except:
            return str(gregorian_date)
    
    # Convert to jdatetime
    if isinstance(gregorian_date, datetime):
        persian_date = jdatetime.datetime.fromgregorian(datetime=gregorian_date)
    elif isinstance(gregorian_date, date):
        persian_date = jdatetime.date.fromgregorian(date=gregorian_date)
    else:
        return str(gregorian_date)
    
    # Convert numbers to Persian digits
    persian_digits = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
    }
    
    day_str = str(persian_date.day)
    year_str = str(persian_date.year)
    
    # Convert to Persian digits
    for eng, per in persian_digits.items():
        day_str = day_str.replace(eng, per)
        year_str = year_str.replace(eng, per)
    
    month_name = get_persian_month_name(persian_date.month)
    
    return f"{day_str} {month_name} {year_str}"


def format_persian_datetime_pretty(gregorian_datetime: Union[datetime, str]) -> str:
    """
    Format Persian datetime in a pretty, readable format
    
    Args:
        gregorian_datetime: Gregorian datetime as datetime or string
        
    Returns:
        Pretty formatted Persian datetime string (e.g., "۱۵ فروردین ۱۴۰۳، ۱۴:۳۰")
    """
    if gregorian_datetime is None:
        return ""
    
    # Handle string input
    if isinstance(gregorian_datetime, str):
        try:
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M']:
                try:
                    gregorian_datetime = datetime.strptime(gregorian_datetime, fmt)
                    break
                except ValueError:
                    continue
            else:
                return str(gregorian_datetime)
        except:
            return str(gregorian_datetime)
    
    # Convert to jdatetime
    if isinstance(gregorian_datetime, datetime):
        # Remove timezone info for jdatetime (it works with naive datetime)
        if gregorian_datetime.tzinfo is not None:
            gregorian_datetime = gregorian_datetime.replace(tzinfo=None)
        
        persian_datetime = jdatetime.datetime.fromgregorian(datetime=gregorian_datetime)
    else:
        return str(gregorian_datetime)
    
    # Convert numbers to Persian digits
    persian_digits = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
    }
    
    day_str = str(persian_datetime.day)
    year_str = str(persian_datetime.year)
    hour_str = f"{persian_datetime.hour:02d}"
    minute_str = f"{persian_datetime.minute:02d}"
    
    # Convert to Persian digits
    for eng, per in persian_digits.items():
        day_str = day_str.replace(eng, per)
        year_str = year_str.replace(eng, per)
        hour_str = hour_str.replace(eng, per)
        minute_str = minute_str.replace(eng, per)
    
    month_name = get_persian_month_name(persian_datetime.month)
    
    return f"{day_str} {month_name} {year_str}، {hour_str}:{minute_str}"


# Jinja2 template filters
def persian_date_filter(gregorian_date, format_str='%Y/%m/%d'):
    """Jinja2 filter for converting dates to Persian format"""
    return to_persian_date(gregorian_date, format_str)


def persian_datetime_filter(gregorian_datetime, format_str='%Y/%m/%d %H:%M'):
    """Jinja2 filter for converting datetimes to Persian format"""
    return to_persian_datetime(gregorian_datetime, format_str)


def persian_date_pretty_filter(gregorian_date):
    """Jinja2 filter for pretty Persian date formatting"""
    return format_persian_date_pretty(gregorian_date)


def persian_datetime_pretty_filter(gregorian_datetime):
    """Jinja2 filter for pretty Persian datetime formatting"""
    return format_persian_datetime_pretty(gregorian_datetime)
