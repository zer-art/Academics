import pandas as pd 
import textdistance
from collections import Counter
import re

word = []
with open("S:/Github/Minor Project/Minor-Project/dev/app/autocorrect book.txt", 'r',encoding="utf-8" ) as f:
     data = f.read()
     data = data.lower()
     data = re.sub(r'[^a-zA-Z0-9\s]', '', data)  # Remove punctuation
     data = re.sub(r'\s+', ' ', data)  # Remove extra spaces     
     word = data.split()  # Split into words
     
set_word = set(word)  # Create a set of unique words
word_list = list(set_word)  # Convert set back to list
vocab = pd.DataFrame(word_list, columns=['word'])  # Create DataFram


word_freq = Counter(word)  # Count occurrences of each word

word_probs = {}
for i in word_freq.keys():
    word_probs[i] = word_freq[i] / len(word)  # Calculate probabilities

def autocorrect(word, vocab=vocab, word_probs=word_probs):   
    # Calculate the probability of the closest 5 word
    closest_words = sorted(vocab['word'], key=lambda x: textdistance.levenshtein.distance(word, x))[:15]
    closest_word_probs = {w: word_probs[w] for w in closest_words if w in word_probs}
    # Sort the closest words by their probabilities     
    sorted_closest_words = sorted(closest_word_probs.items(), key=lambda x: x[1], reverse=True)
    # Return the 5 word with the highest probability
    return pd.DataFrame(sorted_closest_words[:15],columns=['word', 'probability'])
