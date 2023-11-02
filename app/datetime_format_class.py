from datetime import datetime, timedelta

# Datetime formatting class for routes.py
    
class DateTimeFormat:
    '''
    A class that takes a datetime object and it includes methods for
    formatting date and time.
    
    date_format method:
        - returns one of the following:
            If the date is today, it returns "Today".
            If the date is yesterday, it returns "Yesterday".
            Otherwise, it returns formatted date.
    time_format method:
        - return formatted time.
    '''
    def __init__(self, date_time: datetime):
        self.date_time = date_time
        
    def date_format(self):
        if self.date_time.date() == datetime.today().date():
            return "Today"
        elif self.date_time.date() == (datetime.today().date() - timedelta(days=1)):
            return "Yesterday"
        else:
            return self.date_time.strftime("%b %d, %Y")
        
    def time_format(self):
        no_zero_hour = self.date_time.strftime("%I") if self.date_time.strftime("%I")[0] != '0' else self.date_time.strftime("%I")[1]
        return self.date_time.strftime(f"{no_zero_hour}:%M %p")