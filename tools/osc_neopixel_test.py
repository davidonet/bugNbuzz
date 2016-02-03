

e = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
while True:
	for i in range(15):
		e[i]=random.randint(0,255)
	send(target,"/outputs/rgb/16",e)
	time.sleep(0.01)
	e = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	send(target,"/outputs/rgb/16",e)
	time.sleep(0.1)