import datetime

def timeParser(x,days):
  firstDate = datetime.datetime.strptime(x,'%Y-%m-%d')
  secondDate = firstDate + datetime.timedelta(days=days)
  secondDate = secondDate.strftime("%Y-%m-%d")
  return secondDate
