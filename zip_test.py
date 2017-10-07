import datetime
td = datetime.datetime
dt = datetime.datetime.today().date()
tm = datetime.datetime.today().time()
print tm
yr = td.today().strftime("%Y-%m")
print yr
wk = td.today().strftime("%W")
print wk
wd = td.today().strftime("%A")
print wd

s = "2014-07-01 14:43:00"

st = td.strptime(s,"%Y-%d-%m %H:%M:%S").strftime("%b %d %Y %I:%M %p")
print st

p = "Jan 7 2014 02:43 PM"

pt = td.strptime(p,"%b %-m %Y %I:%M %p").strftime("%d-%-m-%Y %H:%M:%S")
print pt
