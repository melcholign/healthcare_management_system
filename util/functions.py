from datetime import date, timedelta
from django.db import connection

def dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def next_weekday_date(weekday):
    """
    Return the date of the weekday that falls within a week from today
    """
    
    weekdays = {
        'mon': 0,
        'tue': 1,
        'wed': 2,
        'thu': 3,
        'fri': 4,
        'sat': 5,
        'sun': 6,
    }
    
    if weekday not in weekdays:
        raise Exception
    
    today = date.today()
    days_until = weekdays[weekday] - today.weekday()
    days_until += 7 if days_until <= 0 else 0
    return str(today+ timedelta(days=(days_until)))
    
# Note: in the session data, account_id actually holds user_id, so the name is currently
# misleading, and will be subject to change in the future
def get_account_id(user_id, account_type):
    """
    Returns the account id corresponding to a user id.
    The account id is related to a type of a user/account (i.e. doctor or patient account)
    """
    with connection.cursor() as cursor:
        cursor.execute(f'''SELECT id FROM accounts_{account_type} WHERE user_id={user_id}''')
        account_id = dictfetchall(cursor)[0]['id']
        
    return account_id