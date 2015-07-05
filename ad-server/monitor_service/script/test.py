import time
import datetime
a='2014-12-31 10:00:00'
#print a.strftime("%Y-%m-%d %H:%M:%S")
tmp=time.strptime(a, "%Y-%m-%d %H:%M:%S")
otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", tmp)
#a=tmp+datetime.timedelta(minutes=5)
a=datetime.datetime.strptime("2014-03-04 21:08:12", "%Y-%m-%d %H:%M:%S") 
a=a+datetime.timedelta(minutes=5)
b=a.strftime("%Y-%m-%d %H:%M:%S")
print b,type(b)
