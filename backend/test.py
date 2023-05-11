from datetime import datetime, timedelta
from calendar import monthrange

current_date = datetime.today()
month_range = monthrange(current_date.year, current_date.month)
first_date_tm = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
date_prev_month = first_date_tm - timedelta(days=1)
prev_month_range = monthrange(date_prev_month.year, date_prev_month.month)

first_date = date_prev_month.replace(day=1)
last_date = date_prev_month.replace(day=prev_month_range[1], hour=23, minute=59, second=59)
numdays = prev_month_range[1]
date_list = [(first_date + timedelta(days=x)).date() for x in range(numdays)]
x = {date:0 for date in date_list}
print(x)