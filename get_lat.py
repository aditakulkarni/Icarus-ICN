import sys

lat =[]
l100 =[]
l400 =[]
l500 =[]
l1000=[]
l2000=[]
l6000=[]
l12000=[]
cache =''
strat = ''

s = 'HYBRID'

for arg in sys.argv[1:]:
	f = file(arg, 'r')

	for line in f:		
		columns = line.split(' ')
		columns = [col.strip() for col in columns]
		if len(columns) >= 1 and columns[0] == 'Cache:':
			cache = columns[2]
		if len(columns) >= 1 and columns[0] == s:
			strat = s
		if len(columns) > 1 and columns[1] == 'lat:' and strat == s:
			lat.append(float(columns[2]))
			if cache == '100':
				l100.append(float(columns[2]))
				strat = ''
			elif cache == '400':
				l400.append(float(columns[2]))
				strat = ''
			elif cache == '500':
				l500.append(float(columns[2]))
				strat = ''
			elif cache == '1000':
				l1000.append(float(columns[2]))
				strat = ''
			elif cache == '2000':
				l2000.append(float(columns[2]))
				strat = ''
			elif cache == '6000':
				l6000.append(float(columns[2]))
				strat = ''
			else:
				l12000.append(float(columns[2]))
				strat = ''

print "lat:",sorted(lat, reverse=True)
print "100:",l100
print "400:",l400
print "500:",l500
print "1000:",l1000
print "2000:",l2000
print "6000:",l6000
print "12000:",l12000
