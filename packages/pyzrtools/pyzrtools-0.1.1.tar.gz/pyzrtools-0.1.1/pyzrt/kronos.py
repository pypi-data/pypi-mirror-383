import time
import pytz
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse

UTC = 'UTC'
EAST8 = 'Asia/Shanghai'


def get_epoch13():
    return int(time.time()*1000)


def get_epoch10():
    return int(time.time())


def epoch13_to_iso(epoch13):
    return datetime.utcfromtimestamp(epoch13/1000).isoformat()


def in_hours_of_day(since, to):
    utc_hour = datetime.utcnow().hour
    if since <= utc_hour < to:
        return True
    else:
        return False


def in_time_of_day(since, to, tz=UTC):
    timezone = pytz.timezone(tz)
    now = datetime.now().astimezone(timezone)
    since_time = timezone.localize(
        parse(since, default=datetime(now.year, now.month, now.day)))
    to_time = timezone.localize(
        parse(to, default=datetime(now.year, now.month, now.day)))
    print(since_time, now, to_time)
    if since_time <= now < to_time:
        return True
    else:
        return False


# def in_days_of_week(*args):
#     utc_weekday = datetime.utcnow().isoweekday()
#     if utc_weekday in args:
#         return True
#     else:
#         return False


def in_days_of_week(*args, tz=UTC):
    now = datetime.now().astimezone(pytz.timezone(tz))
    weekday = now.isoweekday()
    if weekday in args:
        return True
    else:
        return False

def get_date_lst(begin_date, end_date):
    if not isinstance(begin_date, datetime):
        begin_date = datetime.strptime(str(begin_date), '%Y%m%d')
    if not isinstance(end_date, datetime):
        end_date = datetime.strptime(str(end_date), '%Y%m%d')
    ret = []
    while begin_date <= end_date:
        ret.append(begin_date.strftime('%Y%m%d'))
        begin_date += timedelta(days=1)
    return ret

if __name__ == '__main__':
    tz_utc = pytz.timezone('UTC')
    tz_e8 = pytz.timezone('Asia/Shanghai')

    now = datetime.now()
    print(now)

    now = datetime.now().astimezone(tz_e8)
    print(now)

    now = datetime.now(tz=tz_e8)
    print(now)

    print()
    since = tz_e8.localize(parse('9:15'))
    print(since)
    since_tz = since.astimezone(tz_e8)
    print(since_tz, since_tz.tzinfo)

    print()
    now = datetime.now().astimezone(tz_e8)
    print(now, now.tzinfo)
    print(tz_e8)
    since = tz_e8.localize(
        parse('9:15', default=datetime(now.year, now.month, now.day)))
    print(since)
    since_tz = since.astimezone(tz_e8)
    print(since_tz, since_tz.tzinfo)

    # date = datetime.now().date()
    # date = datetime.now().today()
    # print(date, type(date))
    # print(date)
