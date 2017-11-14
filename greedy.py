cache_size = 0.7*100
count = 1
name = '/home/adita/Greedy 08142017/youtube_traces/All traces/sorted_cont'
f4 = open(name,'r')
f1 = open('l1'+str(cache_size),'w')
f2 = open('l2'+str(cache_size),'w')
f3 = open('l3'+str(cache_size),'w')
for f in f4:

	if count <= cache_size:
		f1.write(f)
	elif count > cache_size and count <= cache_size*2:
		f2.write(f)
	elif count > cache_size*2 and count <= cache_size*3:
		f3.write(f)
	else:
		break
	count +=1
