import sys

l100 =[]
l400 =[]
l6000=[]
l12000=[]
cache =''
for arg in sys.argv[1:]:
	f = file(arg, 'r')

	for line in f:		
		columns = line.split(' ')
		columns = [col.strip() for col in columns]
		if len(columns) >= 1 and columns[0] == 'Cache:':
			cache = columns[2]
		if len(columns) > 1 and columns[1] == 'lat:':
			if cache == '100':
				l100.append(float(columns[2]))
			elif cache == '400':
				l400.append(float(columns[2]))
			elif cache == '6000':
				l6000.append(float(columns[2]))
			else:
				l12000.append(float(columns[2]))

print "100:",l100
print "400:",l400
print "6000:",l6000
print "12000:",l12000


x = min(float(s) for s in l100)
print x
x = min(float(s) for s in l400)
print x
x = min(float(s) for s in l6000)
print x
x = min(float(s) for s in l12000)
print x
