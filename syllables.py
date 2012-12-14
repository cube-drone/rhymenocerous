import nltk
from collections import defaultdict

rhyme_entries = nltk.corpus.cmudict.entries()

syllable_guide = defaultdict( lambda: 1 )
for word, pronunciations in rhyme_entries:
    syllable_guide[word] = len([x for x in pronunciations if x[-1].isdigit() ]) 

def syllables( word ):
    """
        >>> print syllables( "I" )
        1
        >>> print syllables( "battalion" )
        3
    """
    return syllable_guide[word.lower()]

def sentence_syllables( sentence ):
    """
        >>> print sentence_syllables( "I am a battalion" )
        7
    """
    tokens = nltk.word_tokenize(sentence) 
    return sum( [ syllables(word) for word in tokens ] )
    
