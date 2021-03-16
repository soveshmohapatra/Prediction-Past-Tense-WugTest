import sys
from collections import defaultdict
import re
import random
from min_edit import min_edit
from math import e

### calculates pearson correlation btwn two lists of numbers
def pearson(v1,v2):
	if len(v1)!=len(v2): return None
	s1 = sum(v1)
	s2 = sum(v2)
	m1 = s1/len(v1)
	m2 = s2/len(v2)
	xy = 0.0
	xx = 0.0
	yy = 0.0
	for i in range(len(v1)):
		xy += (v1[i]-m1)*(v2[i]-m2)
		xx += (v1[i]-m1)*(v1[i]-m1)
		yy += (v2[i]-m2)*(v2[i]-m2)
	return xy/((xx**.5)*(yy**.5))

def get_training(f):
###	returns the training data as three dictionaries:
### the verb's orthographic singular form is the key of each one
### pres[verb] gives the phonetic transcription of the verb's present form
### past[verb] gives the phonetic transcription of the verb's past form
### label[verb] gives the morphological rule category
	pres = defaultdict(lambda:'')
	past = defaultdict(lambda:'')
	label = defaultdict(lambda:'')
	for v in f.readlines():
		orth, ppres, opast, ppast, cat = v.split(',')
		pres[orth] = ppres
		past[orth] = ppast
		label[orth] = cat.strip()
	f.close()
	return (pres, past, label)

### takes a phonetic transcription of a wug verb, a dictionary
### of actual verb forms to compare it to, and a number n.
### returns all neighbors within n as a dictionary of neighbor, distance pairs
### if n is negative (by default), all neighbors are returned
def get_neighbors(wugphon='', dict={}, n=-1):
	neighbors = defaultdict(lambda:0.0)
	for v in dict:
		d = min_edit(wugphon,dict[v])
		if d <= n or n < 0:
			neighbors[v] = d
	return neighbors

### takes dictionary of neighbor, distance pairs and returns overall similarity
def similarity(neighbors):
	s = 0.55
	sim = 0.0
	for n,d in neighbors.items():
		sim += e**(-d/s)
	return sim

### takes two lists of responses and returns the proportion that match
def accuracy(v1,v2):
	tot = len(v1)
	matches = 0.0
	for x,y in zip(v1,v2):
		if x==y: matches += 1
	return matches/tot

def main():
	trainf = open(sys.argv[1], encoding='utf-8')
	testf = open(sys.argv[2], encoding='utf-8')
	# store training data in three dictionaries for easy access
	pres, past, label = get_training(trainf)

	# lists to create while looping through wug words
	responses = []	# will contain human forced choice responses
	ratings = []	# will contain human wellformedness ratings
	sims = []		# will contain predicted ratings based on similarity
	preds = []		# will contain predicted forced choice responses based on analogy

	# Adding the default dictionary

	present_dictionary = defaultdict(dict)

	#Adding the for loop to find the match for each class in cat and look for orthographic phonetic pairs
	
	for orth, cat in label.items():
		present_dictionary[cat][orth] = pres[orth]

	for wug in testf.readlines():
		f = wug.split(',')
		# skip header line
		if "Orth" in wug: continue
		# extract & store wug data from test file
		orth, phon, rating, regpast, regscore, irregpast, irregscore, irregclass = f[0], f[1], float(f[2]), f[3], float(f[4]), f[5], float(f[6]), f[7].strip()
		# add rating for this wug to the list
		ratings.append(float(rating))
		# determine participants' preferred past category
		response = ""
		if regscore < irregscore: response = irregclass		# participants preferred irregular
		else:	# participants preferred the regular
			# determine & store the regular transformation
			if regpast[-2:] == 'Id': response = "NULL->Id"
			elif regpast[-1:] == 'd': response = "NULL->d"
			elif regpast[-1:] == 't': response = "NULL->t"
		# store participants' preferred past category
		responses.append(response)

		### PART 2 - calculate and store similarity of this wug's present tense
		### form to the present tense forms in the training data
		# collect neighboring present forms
		presneighbors = get_neighbors(wugphon = f[1],dict = pres)
		# calculate similarity over all neighbors
		sim = similarity(presneighbors)
		# add similarity for this wug to the list
		sims.append(sim)

		print(orth, sim, rating)

		### PART 3 - compute and store analogical predictions
		### your code goes here (if you wish, you can also write new functions
		### or code outside this loop, but that's not necessary).

		#Declaring the dictionary

		dict_sims = dict()
		
		#Using the for loop for creating the pairs 

		for c,d in present_dictionary.items():
			neighboring_elements_wug = get_neighbors(phon, d)
			dict_sim = similarity(neighboring_elements_wug)
			dict_sims[c] = dict_sim

		#Finding of the highest sim which is possible in the given dict_sims pairs

		prediction_for_the_highest_sim = max(dict_sims, key = lambda z: dict_sims[z])

		preds.append(prediction_for_the_highest_sim)

		#Checking the if - else statements for 

		if response == prediction_for_the_highest_sim:
			produce = "It is a match"
		else:
			produce = "It is not a match"
		
		print("Wug: " + orth, "\n Considered Past Tense: " + response, "\n Predicted Past Tense from the Model: " + prediction_for_the_highest_sim,
		"\n " + produce, "\n Relating Neighbors of " + orth + ": " + str(list(get_neighbors(wugphon = phon, dict = pres, n = 2))))

	testf.close()
	print("Correlation Ratings X Similarities:", pearson(ratings,sims))

	### uncomment the next line after PART 3 is done
	print("Accuracy of Analogical Predictions:", accuracy(responses,preds))

if __name__ == "__main__":
    main()
