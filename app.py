from collections import Counter
from math import log2, ceil
# A compression algorithm

def generate_binary_combinations(n):
    if n == 1:
        return ['0', '1']
    else:
        prev_combinations = generate_binary_combinations(n - 1)
        new_combinations = []
        for combo in prev_combinations:
            new_combinations.append(combo + '0')
            new_combinations.append(combo + '1')
        return new_combinations

def pre_mapping(st): # returns a list containing tuples in format (ngram,occurence,efficiency)
    
    pre_mapdict = []
    max_word = len(max(st.split(),key=len))
    
    onegram = [st[i:i+1] for i in range(len(st))] # Here 'n', the lenght of character to check occurence of is one
    count = Counter(onegram)
    for ngram in list(count.items()):
        pre_mapdict.append((ngram[0],ngram[1],0)) # unigrams cannot be compressed, hence effieciency = zero
    
    temp_ngrams = []

    for n in range (2,max_word+1): # This loop will find the most repeated ngram or a set of character
        ngrams = [st[i:i+n] for i in range(len(st) - n + 1)] # Here 'n' the length of character to check occurence of is 'n'
        count = Counter(ngrams)

        if count.most_common()[0][1] == 1:
            break

        for ngram in list(count.items()):
            # efficiency = len(ngram[0]) * (ngram[1]- 1) - ngram[1]
            efficiency = (len(ngram[0]) * ngram[1]) - (len(ngram[0]) + ngram[1]) # Mrinal's Efficiency Parameter = (LenghtxOccurence) - (lenght+occurence) = Number of Bytes saved
            if ngram[1] > 1 :
                temp_ngrams.append((ngram[0],ngram[1],efficiency))
                
    temp_ngrams.sort(key = lambda x: x[2], reverse = True)
    pre_mapdict = pre_mapdict + temp_ngrams[:256 - len(pre_mapdict)] # temp_ngrams is sliced because since we only have 256 bytes available to assign 
                                                                     # and unigrams must be assigned one
                                                                     # so, ngrams can only be assigned 256 - no. of unigrams(since it HAS to be assigned a byte)

    pre_mapdict.sort(key = lambda x: x[2], reverse = True)

    return pre_mapdict   


def mapping(premapdict):

    ngram_list = [i[0] for i in premapdict]

    var = ceil(log2(len(ngram_list)))
    binlist = generate_binary_combinations(var)
    
    mapp = {}
    
    for i in range(len(ngram_list)):
        mapp.update({ngram_list[i]:binlist[i]})

    # with open('map.txt','w') as f1:
    #     f1.write(str(mapp))

    return mapp

def compressor(st,map_dict):        # params: string to be converted, mapping dictionary
    map1 = list(map_dict.items())
    map1.sort(key = lambda x: len(x[0]), reverse = True) # Here we sort the mapping dict by changing into list (on basis of len of word)
    map2 = {} # It contains a sorted version of mapping dict by ngram lenght in descending order 
    for i in map1:
        map2.update({i[0]:i[1]})


    
    for substr, replacement in map2.items(): # replaces character by its corrsponding bit in the mapping dict
        st = st.replace(substr, str(replacement))
    
    # Spilting the numbers
    newstr = ''
    counter = 0
    for i in st: # this splits the numbers in 8
        newstr+=i
        counter+=1
        if counter == 8:
            newstr+=' '
            counter = 0
    print(newstr)

    # Structure of defbyte = 1 + 4 digits of separator value + 3 digits of zero padding value
    if len(newstr.split()[-1]) == 8: # checks the last element length
        exdigitlen = 8
    else:
        exdigitlen = len([i for i in newstr.split() if len(i)<8][0])

    definerbyte = '1'+ str(bin(len(newstr.split()[0])))[2:].zfill(4) + str(bin(8-exdigitlen))[2:].zfill(3)
    binlist = [definerbyte]+(newstr+((8-exdigitlen)*'0')).split() # It contains Defbyte + zero padded bytes
    char_list = [chr(int(i)) for i in binlist] # This list contains the character equivalent of the bytes

    

    compressedstr = ''.join(char_list)

    return (map_dict,compressedstr)


