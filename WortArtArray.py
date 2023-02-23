from textblob import TextBlob
from textblob_de import TextBlobDE
import re
from html.parser import HTMLParser
import urllib.request
from PIL import Image
import numpy as np
import math
import sys
  

  
            
# define object/class for analysis
class textforart:
    
    def __init__(self, language, sentence_lens, sentences, commas, polarity):  
       # Sprache
       self.language = language

       # Satz
       if len(sentences) == 0:
           sentences = ['Hello fellow human beeing ^.^']
       self.senctences = sentences
       
       # Sentence lengthes
       if len(sentence_lens) == 0:
           sentence_lens = [0]
       self.sentence_lens = sentence_lens       
       
       # Commas
       if len(commas) == 0:       
           commas = [0]
       self.commas = commas
            
       # Bewertung
       if len(polarity) == 0:        
           polarity = [0]
       self.polarity = polarity
       
       # Komplezität
       complexity = [0]
       self.complexity = ''

       
       # Satzlänge
       self.sentence_number = len(sentences)      
       self.min_sentence_length = min(sentence_lens)
       self.max_sentence_length = max(sentence_lens)
       self.mean_sentence_length = sum(sentence_lens) / len(sentences)  
       
       # Kommas
       self.number_commas = len(commas)
       self.min_number_commas = min(commas)
       self.max_number_commas = max(commas)
       self.mean_number_commas = len(commas)/ len(sentences)   
        
       # Bewertung
       self.sum_sentences_polarity = sum(polarity)
       self.min_sentences_polarity = min(polarity)
       self.max_sentences_polarity = max(polarity)
       self.mean_sentences_polarity = sum(polarity) / len(sentences)
        
       # Schätzer für Komplexität  
       self.max_complexity = 0
       self.min_complexity = 0
       self.mean_complexity = 0   
       
       # signatur Word -> mean purpose
       self.signatur_word = '' 

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
    lim = sys.argv[2]
    print('[STAT]\tLets use ', lim, ' for distinguishing our colors.')
except IndexError:
	lim = 0.1


            
#content = 'https://en.wikipedia.org/wiki/Pretty_Good_Privacy'
#content = 'https://commonmark.org/help/'
#content = 'https://de.wikipedia.org/wiki/Serotonin'
parser = MyHTMLParser()            
parser.feed(urllib.request.urlopen(content).read().decode())
linkdata = parser.data
line = []

if linkdata is not None:
	# language
    language = ''

    # filtering parsed text
    text = ""
    for phrases in linkdata:
            phrases = phrases.rstrip("\n\r+0-9[]()+")
            # skip unwanted characters         
            text = text + phrases
         
    # create textblob
    blob = TextBlob(text)
    
    # language?
    cnt = 0
    for w in blob.words:
        cnt = cnt + 1
        if re.match(r"and", w):
            language = 'en'
        elif re.match(r"und", w):
            language = 'de'

    if language == 'de':
        blob = TextBlobDE(text)

# number of words
# calculate width and size of image out of words
width = round(math.sqrt(cnt))
height = round(math.sqrt(cnt))

print('square of wordnumber: ', width)

# create image-array
array = np.zeros([width, height, 3], dtype=np.uint8)

#print(array[1:10,1:10])

## starting Text analysis
sentence_lens = []
commas = []
polarity = []



for sentence in blob.sentences:    
	# length of sentences
	sentence_lens.append(len(sentence))     
	# number of commas
	commas.append(len(re.findall(',', str(sentence))))       
	# polarity
	polarity.append(sentence.sentiment.polarity)

# calculate some stats
art = textforart(language, sentence_lens, blob.sentences, commas, polarity) 


plength = len(polarity)

print('number of polarity: ', plength)


red = 0
green = 0
blue = 0
i = 0 # counter for all tuples
j = 0 # counter for resize
cnt = 10

blurrarray = np.zeros([width*10, height*10, 3], dtype=np.uint8)


# number of polarity < number of image-tupel -> resizefaktor
resize = cnt/plength

## smoothing everyting: +- 3 Pixel? +- 5 Pixel?
for x in range(width*10):
	for y in range(height*10):		
		# calculate value
		if polarity[j] < -1*float(lim):
			#if -150*polarity[j] > 255:
				#blue = 250
			#else:
			#red = 200*polarity[j]
			red = (100*3.137*polarity[j]) - cnt/10
			#print('red: ', red)
		elif polarity[j] > float(lim):
			#if -150*polarity[j] > 255:
				#blue = 255
			#else:
			#blue = 200*polarity[j]
			blue = (100*1.961*polarity[j]) - cnt/10
			#print('blue: ', blue)
		else:
			#if 150*polarity[j] > 255:
				#green = 255
			#else:
			#green = 200*polarity[j]
			green = (100*1.176*polarity[j]) - cnt/10
			#print('green: ', green)

		#array[x,y] = [red, green, blue]	
		
		blurrarray[x,y] = [red, green, blue]	
			
		print('polarity: ',  polarity[j], 'i: ', i, 'j: ', j, 'x: ', x, 'y: ', y, 'arr: ', blurrarray[x,y])
		# counting down blurring..
		cnt = cnt - 1
		
		if cnt == 0:			 		
			i = i + 1
			
			# reset counter
			if j >= resize*1000:
				j = 0
			else:
				j = j + 1
			cnt = 10


#for wi in blob.sentences:
	#if i == width:
		#i = 0
		#j = j + 1
		
	#if j == height:
		#continue
	
	#print('x: ', i, 'y: ', j, 'arr: ', array[i,j])
	#print(wi, ' / ', i)
	# make image-array with words
	# red -> positive values
	# blue -> negative values
	# green -> neutral
	#if wi.polarity < -0:
		#if -150*wi.polarity > 255:
			#red = 255
		#else:
			#red = -150*wi.polarity
		#line.append([0, 0, red])
	#elif wi.polarity > 0.1:
		#if 150*wi.polarity > 255:
			#green = 255
		#else:
			#green = 150*wi.polarity			
			#line.append([green, 0, 0])
	#else:
		#blue = 125				
		#line.append([0, blue, 0])			
		#if 150*wi.polarity > 255:
			#blue = 255
		#else:
			#blue = 150*wi.polarity		
	
	#if wi.polarity < -0:
		#if -150*wi.polarity > 255:
			#red = 255
		#else:
			#red = -150*wi.polarity
		#line.append([0, 0, red])
	#elif wi.polarity > 0.1:
		#if 150*wi.polarity > 255:
			#green = 255
		#else:
			#green = 150*wi.polarity			
		#line.append([green, 0, 0])
	#else:
		#blue = 125				
		#line.append([0, blue, 0])			
		#if 150*wi.polarity > 255:
			#blue = 255
		#else:
			#blue = 150*wi.polarity		
	
	# analyse tags -> calculate values for image
	# noun -> green
	#if wi.tags == 'NN':
		
	#elif wi.tags == 'NNS':
	
	#elif wi.tags == 'NNP':
		
	# red
	#elif wi.tags == 'JJ':
	
	#elif wi.tags == 'JJR':
		
	#elif wi.tags == 'FB':
		
	#elif wi.tags == 'FW':		
	
	#elif wi.tags == 'RB':
	
	# blue
	#elif wi.tags == 'VB':
	
	#elif wi.tags == 'VBN':

	#elif wi.tags == 'VBG':
		
	#elif wi.tags == 'VBZ':
		
	#elif wi.tags == 'VB':	
				
	
	#print(wi.tags)
	#sepword = wi.words
	
	#line.append(r)
	#i = i + 1
	
	
print('[STAT] Kommas: ', art.min_number_commas, ' - ', art.max_number_commas, ' Polarity: ', art.min_sentences_polarity, ' - ', art.max_sentences_polarity)
       
print(blurrarray)
	
# create array-Picture 		
#print(line)
#arrline = np.array(line)		
#im = Image.fromarray(array.astype('uint8'))
#im.save('graph.png')
		
im2 = Image.fromarray(blurrarray.astype('uint8'))
im2.save('blurr2 .png')
