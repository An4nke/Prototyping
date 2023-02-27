from textblob import TextBlob
from textblob_de import TextBlobDE
import re
import numpy as np
import math
import sys
from PIL import Image 

## usage
# python text2polarisation.py '[text]' [image-name]

## parameters
try:
    content = sys.argv[1]
except IndexError:
	sys.exit('[ERROR]\tText for analysis missing..') 

try:
    png = sys.argv[2]
except IndexError:
	png = 'CREATION'
	
print('[STAT]\tOur creation will be saved as: ', png)	

# language
language = ''

# number of sentences
sentencenr = 0

# create textblob
blob = TextBlob(content)


 # language?
for w in blob.words:
	sentencenr = sentencenr + 1
	if re.match(r"and", w):
		language = 'en'
	elif re.match(r"und", w):
		language = 'de'

if language == 'de':
    blob = TextBlobDE(content)

# calculate width and size of image out of sentencenumber
width = round(math.sqrt(sentencenr))
height = round(math.sqrt(sentencenr))


## starting Text analysis
# array for polarity values of sentences
polarity = []

for sentence in blob.sentences:
	print('[STAT]\t[POLARITY]\t', sentence.sentiment.polarity)       
	# polarity
	polarity.append(sentence.sentiment.polarity)


red = 0
green = 0
blue = 0
i = 0 # counter for all tuples
j = 0 # counter for resize
cnt = 10
lim = 0.2
seizemulti = 10


# create image-array
blurrarray = np.zeros([width*seizemulti, height*seizemulti, 3], dtype=np.uint8)


## smoothing everyting: +- 3 Pixel? +- 5 Pixel?
for x in range(width*seizemulti):
	for y in range(height*seizemulti):		
		# calculate value
		if polarity[j] < -1*float(lim):
			red = (100*3.137*polarity[j]) - cnt/seizemulti
		elif polarity[j] > float(lim):
			blue = (100*1.961*polarity[j]) - cnt/seizemulti
		else:
			green = (100*1.176*polarity[j]) - cnt/seizemulti

		## creating picture point
		blurrarray[x,y] = [red, green, blue]	

		# counting down blurring..
		cnt = cnt - 1		
		if cnt == 0:			 		
			i = i + 1
			
			# reset counter
			try:
				polarity[j + 1]
				j = j + 1
			except IndexError:
				j = 0 			
				
			cnt = 10


## save picture
im2 = Image.fromarray(blurrarray.astype('uint8'))
im2.save(png + '.png')
