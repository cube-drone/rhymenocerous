import copy
import nltk
from collections import defaultdict
import random
import cPickle
import gzip
import os

import syllables

rhyme_entries = nltk.corpus.cmudict.entries()
pronunciation_dictionary = nltk.corpus.cmudict.dict()

mega_sentences = ( nltk.corpus.brown.sents() + 
                nltk.corpus.inaugural.sents() + 
                nltk.corpus.reuters.sents() + 
                nltk.corpus.webtext.sents() + 
                nltk.corpus.inaugural.sents() + 
                nltk.corpus.gutenberg.sents("carroll-alice.txt") +
                nltk.corpus.gutenberg.sents("austen-emma.txt") + 
                nltk.corpus.gutenberg.sents("austen-sense.txt") + 
                nltk.corpus.gutenberg.sents("blake-poems.txt") + 
                nltk.corpus.gutenberg.sents("bible-kjv.txt") + 
                nltk.corpus.gutenberg.sents("chesterton-ball.txt") + 
                nltk.corpus.gutenberg.sents("melville-moby_dick.txt") + 
                nltk.corpus.gutenberg.sents("milton-paradise.txt") + 
                nltk.corpus.gutenberg.sents("whitman-leaves.txt") + 
                nltk.corpus.gutenberg.sents("austen-persuasion.txt") + 
                nltk.corpus.gutenberg.sents("shakespeare-hamlet.txt") + 
                nltk.corpus.gutenberg.sents("shakespeare-macbeth.txt") ) 


last_word_sentences = defaultdict(list)

def last_word( sentence ):
    ss = [ word for word in sentence if len(word) > 1 ]
    if len(ss) > 0:
        return ss[-1]
    else:
        return ""

if os.path.exists( "sentences.gz" ):
    with gzip.open( "sentences.gz", "r" ) as cache_file:
        last_word_sentences = cPickle.load( cache_file )
else:
    for sentence in mega_sentences:
        lw = last_word(sentence)
        last_word_sentences[ lw ].append(sentence)
    with gzip.open( "sentences.gz", "w") as cache_file:
        cPickle.dump(last_word_sentences, cache_file)

def candidate_sentences( word ):
    """
    Return sentences from corpus that have word as the last word. 
    """
    return last_word_sentences[ word.lower() ]

def rhyme_quality( p1, p2 ):
    """ Determine a numerical quality of the rhyme between two pronunciation lists. 
    
        >>> rhyme_quality( ["A", "B", "C"], ["A", "B"] )
        0
        >>> rhyme_quality( ["A", "B", "C"], ["B", "C"] )
        2
        >>> rhyme_quality( ["A", "B"], ["A", "B"] )
        0
        >>> rhyme_quality( ["B", "B", "C", "D"], ["A", "B", "C", "D"] )
        3
    """
    p1 = copy.deepcopy(p1)
    p2 = copy.deepcopy(p2)
    p1.reverse()
    p2.reverse()
    if p1 == p2:
        # G-Spot rocks the G-Spot
        return 0
    quality = 0
    for i, p_chunk in enumerate(p1):
        try:
            if p_chunk == p2[i]:
                quality += 1
            if p_chunk != p2[i]:
                break
        except IndexError:
            break
    return quality
    

def word_rhyme_candidates( word ):
    """
        Produce a list of potential rhyme candidates for a word
        >>> print word_rhyme_candidates("battalion")[:5]
        ['stallion', 'italian', 'scallion', 'medallion', 'mccallion']
    """
    candidates = []
    try:
        pronunciations = pronunciation_dictionary[word]
    except KeyError:
        return []
    if pronunciations == []:
        return []
    for pronunciation in pronunciations:
        for rhyme_word, rhyme_pronunciation in rhyme_entries:
            quality = rhyme_quality( pronunciation, rhyme_pronunciation )
            if quality > 0:
                candidates.append( (quality, rhyme_word) )
    candidates.sort()
    candidates.reverse()
    best_quality = candidates[0][0]
    worst_allowable_quality = best_quality - 1
    candidates = [ candidate for q, candidate in candidates if q >= worst_allowable_quality ]

    return candidates

def rhyme( sentence ):
    target_syllables = syllables.sentence_syllables( sentence )
    tokens = nltk.word_tokenize(sentence) 
    rhymes = word_rhyme_candidates(last_word(tokens))
    cs = []
            
    if len(tokens) == 1:
        return ", ".join(rhymes[:12])

    for rhyme in rhymes:
        cs += candidate_sentences( rhyme )

    syllable_sentences = []
    for sentence in cs:
        ss = sum( [ syllables.syllables(word) for word in sentence ] )
        syllable_sentences.append( (ss, " ".join(sentence)) )

    syllable_sentences.sort()
    syllable_sentences.reverse()
    
    if len( syllable_sentences ) == 0:
        if len( rhymes ) > 0: 
            return ", ".join(rhymes[:12])
        else:
            return "month, orange, Nantucket"
    
    syllable_numbers = [ n for n, sentence in syllable_sentences ] 
    closest_number = min( syllable_numbers, key=lambda x:abs(x-target_syllables) )
    
    closest_sentences = [ sentence for n, sentence in syllable_sentences if n == closest_number ] 

    return random.choice(closest_sentences)
