from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))
DATABASE_FORMAT = "%Y-%m-%d %H:%M:%S"


def to_ist(value):
    if not value:
        return ""
    try:
        parsed = datetime.strptime(value, DATABASE_FORMAT)
    except (TypeError, ValueError):
        return value
    utc_time = parsed.replace(tzinfo=timezone.utc)
    return utc_time.astimezone(IST).strftime(DATABASE_FORMAT)


# end of timeutil.py