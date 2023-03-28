from nrclex import NRCLex
from html.parser import HTMLParser
import sys
import urllib.request
import numpy as np
import math
from PIL import Image


# define class HTML-Parser
class MyHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.data = []
        self.capture = False

    def handle_starttag(self, tag, attrs):
        if tag in ('p', 'h1'):
            self.capture = True

    def handle_endtag(self, tag):
        if tag in ('p', 'h1'):
            self.capture = False

    def handle_data(self, data):
        if self.capture:
            self.data.append(data)
            
# get website url from parameter
try:
    content = sys.argv[1]
    print('[STAT]\tLets analyse the text from these page: ', content)
except IndexError:
	sys.exit('[ERROR]\tYou forgot telling me where to look up..') 

try:
    png = sys.argv[2]
except IndexError:
	png = 'CREATION'

parser = MyHTMLParser()            
parser.feed(urllib.request.urlopen(content).read().decode())
linkdata = parser.data

text_object = NRCLex('nrc_en.json')

size = round(math.sqrt(len(linkdata)))


j = 0 # counter for resize
cnt = 50
seizemulti = 50
array = np.zeros([size*seizemulti, size*seizemulti, 3], dtype=np.uint8)			


if linkdata is not None:
	# filtering parsed text
	text = ""
	for x in range(size*seizemulti):
		for y in range(size*seizemulti):
			phrase = linkdata[j].rstrip("\n\r+0-9[]()+")
			#print(phrase)
			
			# skip unwanted characters     
			text = text + phrase
			
			# let's show the emotions
			emotion = NRCLex(phrase)

			red = 0
			green = 0
			blue = 0
			
			# calculate value
			if emotion.raw_emotion_scores.get('negative'):
				red = (100*3.137*emotion.raw_emotion_scores['negative']) - cnt/seizemulti
			elif emotion.raw_emotion_scores.get('positive'):
				blue = (100*1.961*emotion.raw_emotion_scores['positive']) - cnt/seizemulti

			## calculate value for red:
			# positive-low arousal: trust, positive, surprise, joy		
			if emotion.raw_emotion_scores.get('trust'):
				red = red + (50*3.137*emotion.raw_emotion_scores['trust']) - cnt/seizemulti			
			if emotion.raw_emotion_scores.get('joy'):			
				red = red + (50*3.137*emotion.raw_emotion_scores['joy']) - cnt/seizemulti						
			if emotion.raw_emotion_scores.get('surprise'):						
				red = red + (50*3.137*emotion.raw_emotion_scores['surprise']) - cnt/seizemulti
											
			## calculate value for blue:
			# negative-high arousal: fear, anger, sadness
			if emotion.raw_emotion_scores.get('fear'):
				blue = blue + (50*3.137*emotion.raw_emotion_scores['fear']) - cnt/seizemulti			
			if emotion.raw_emotion_scores.get('anger'):
				blue = blue + (50*3.137*emotion.raw_emotion_scores['anger']) - cnt/seizemulti							
			if emotion.raw_emotion_scores.get('sadness'):
				blue = blue + (50*3.137*emotion.raw_emotion_scores['sadness']) - cnt/seizemulti					

			## calculate value for green: anticip, disgust, negative
			if emotion.raw_emotion_scores.get('anticip'):
				green = green + (50*3.137*emotion.raw_emotion_scores['anticip']) - cnt/seizemulti					
			if emotion.raw_emotion_scores.get('disgust'):
				green = green + (50*3.137*emotion.raw_emotion_scores['disgust']) - cnt/seizemulti								
			if emotion.raw_emotion_scores.get('negative'):
				green = green + (50*3.137*emotion.raw_emotion_scores['negative']) - cnt/seizemulti					
			#		array = np.append(array, [red, green, blue], axis=1)

			## creating picture point
			array[x,y] = [red, green, blue]	

			# counting down blurring..
			cnt = cnt - 1		
			if cnt == 0:			 		
				
				# reset counter
				try:
					linkdata[j + 1]
					j = j + 1
				except IndexError:
					j = 0 			
					
				cnt = 10


		#print('Number of phrases: ', cnt)
		#print('Number for parser: ', len(linkdata))

# save image
im2 = Image.fromarray(array.astype('uint8'))
im2.save(png + '.png')
