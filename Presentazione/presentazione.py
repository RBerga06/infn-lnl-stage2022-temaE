# Per hilights per immagini nella presentazione


class E:
	Timestamp: float

t: List[E] = []



tempi = []
for event in t:
	tempi.append(event.Timestamp)


diff = []
for i in range (1, len(tempi)):
	temp_diff = tempi[i] - tempi[i-1]
	diff.append(temp_diff)


bits = []
for d in diff:
	bits.append(diff % 2)




def conv1(byte):
	sum = 0
	for i in range(8):
		sum = sum + byte[7-i] * 2**i
	return sum

def conv2(byte):
	sum = 0
	for i in range(8):
		sum = sum + byte[7-i] * 2**i
	return sum



bug = False

randNumbers = []
randNumbers_b = []
nRandNumbersPossibili = len(bits)//8

for i in range(nRandNumbersPossibili):
	temp_byte = [0]*8
	for j in range(8):
		temp_byte[j] = bits[i*8 + j]

	randNumbers.append(conv1(temp_byte))
	if bug:
		randNumbers_b.append(conv2(temp_byte))

if bug:
	randNumbers += randNumbers_b



i = 0

def random_byte():
	n = randNumbers[i]
	i = (i + 1) % len(randNumbers)
	return n


