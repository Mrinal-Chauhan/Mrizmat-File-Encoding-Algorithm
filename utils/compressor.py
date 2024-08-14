from collections import Counter
from math import log2, ceil, floor
import os
import msgpack
import psutil
import ahocorasick
import re

"""
Introduction:
==============
This Python program presents a custom file compression algorithm designed to optimize the storage and transmission of data.
Efficient file compression is crucial in various applications, ranging from data storage and transfer to network communication.
The algorithm implemented here employs advanced techniques, to achieve a balance between high compression ratios and reasonable decompression speeds.

Why Use Our Algorithm?
=======================
1. **High Compression Ratios:** Our algorithm excels at reducing the size of files, conserving valuable storage space and facilitating faster data transfer.
2. **Versatility:** Whether you're dealing with text files, images, or other data formats, our algorithm is designed to handle a wide range of file types.
3. **Ease of Integration:** The program provides simple and intuitive functions for compressing and decompressing files, making it easy to integrate into your existing projects.

"""


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





def find_patterns(patterns, text):
    # Initialize Aho-Corasick automaton
    A = ahocorasick.Automaton()

    # Add patterns to the automaton
    for idx, pattern in enumerate(patterns):
        A.add_word(pattern, (idx, pattern))

    # Build the automaton
    A.make_automaton()

    # Store the counts of patterns found
    found_patterns = {}

    # Find patterns in the text
    for end_index, (insert_order, original_value) in A.iter(text):
        if original_value in found_patterns:
            found_patterns[original_value] += 1
        else:
            found_patterns[original_value] = 1

    return found_patterns

def mapl_predictor(size):
    if size > 31:
        return 2
    else:
        return 1 
    
def removebranch(lst): # This function removes all the nodes of a ngram except one with the highest efficiency.
    # Example: for a 5-gram, which is all, 4-gram, 3-gram, 2-gram and unigram, it will compare between all the subsets and choose one with highest efficiency.
    listo = []

    for branch in lst:
        for elements in lst:
            if not branch[0] == elements[0]:
                if branch[0] in elements[0]:
                    listo.append(elements)
                    lst.remove(elements)
    print('removed elements:\n',listo,'\n\n\n')
    return lst


def pre_mapping(st, speedmode, mapsizemode): # returns a list containing tuples in format (ngram,occurence,efficiency)
    
    pre_mapdict = []
    
    speedmodedict = {1:50, 2:36, 3:18, 4:9, 5:6}
    mapsizemodedict = {1:32, 2:64, 3:128, 4:256, 5:512}
    max_word = speedmodedict[speedmode]
    mapsize = mapsizemodedict[mapsizemode]

    onegram = [st[i:i+1] for i in range(len(st))] # Here 'n', the lenght of character to check occurence of is one
    count = Counter(onegram)
    for char in list(count.items()):
        pre_mapdict.append((char[0],char[1],0)) # unigrams cannot be compressed, hence effieciency = zero
    
    temp_ngrams = []
    
    for n in range (2,max_word+1): # This loop will find the most repeated ngram or a set of character
        ngrams = [st[i:i+n] for i in range(len(st) - n + 1)] # Here 'n' the length of character to check occurence of is 'n'
        # The below will generate a dictionary: {word:frequency} while searching using aho-corasick algo
        count = find_patterns(ngrams,st)
        
        highestf = max([i[1] for i in list(count.items())])   # Gets the frequecy of the most repeated word of the ngram list
        if highestf == 1:  # if no more repetetion found, then stop the search
            break          # This is done by checking if all the characters have frequency one
        
        for ngram in list(count.items()):
            # efficiency = len(ngram[0]) * (ngram[1]- 1) - ngram[1]
            efficiency = (len(ngram[0]) * ngram[1]) - (len(ngram[0]) + ngram[1]) # Mrinal's Efficiency Parameter = (LenghtxOccurence) - (lenght+occurence) = Number of Bytes saved
            if ngram[1] > 1 :
                temp_ngrams.append((ngram[0],ngram[1],efficiency))


    temp_ngrams.sort(key = lambda x: x[2], reverse = True)
    
    

    #Now we eliminate the repeated words of the same branch
    temp_ngrams = removebranch(temp_ngrams)
    


    # temp_ngrams is sliced because since we only have 256 bytes available to assign and unigrams must be assigned one so, ngrams can only be assigned 256 - no. of unigrams(since it HAS to be assigned a byte)
    pre_mapdict = pre_mapdict + temp_ngrams[:256 - len(pre_mapdict)] 
    
    
    # Now slicing pre-mapdict for the given mode
    totalsize = 1 if len(pre_mapdict) < 16 else 3 if len(pre_mapdict) < 2**16 else 5
    for i in range(len(pre_mapdict)):
        lngram = len(pre_mapdict[i][0])
        totalsize = totalsize + lngram + mapl_predictor(lngram)
        if totalsize > mapsize * 2**20:
            pre_mapdict = pre_mapdict[:i]
            break

    pre_mapdict.sort(key = lambda x: x[2], reverse = True)
    print('premapdict:\n',pre_mapdict,'\n\n\n')
    return pre_mapdict   



def mapping(premapdict):

    ngram_list = [i[0] for i in premapdict]

    var = ceil(log2(len(ngram_list)))
    binlist = generate_binary_combinations(var)
    
    mapp = {}
    
    for i in range(len(ngram_list)):
        mapp.update({ngram_list[i]:binlist[i]})
    print('Mapp:\n',mapp,'\n\n\n')
    return mapp

def replace_01(input_string, mapdict ):
    keys = mapdict.keys()
    pattern = f'({ "|".join(map(re.escape, keys)) })'
    result = re.split(pattern, input_string)


    for i in range(len(result)):
        char = result[i]
        if char in list(keys):
            result[i] = mapdict[char]

    st = ''.join(result)
    return st


def compressor(st,map_dict):        # params: string to be converted, mapping dictionary
    map1 = list(map_dict.items())
    map1.sort(key = lambda x: len(x[0]), reverse = True) # Here we sort the mapping dict by changing into list (on basis of len of word)
    map2 = {} # It contains a sorted version of mapping dict by ngram length in descending order 
    for i in map1:
        map2.update({i[0]:i[1]})

    print('compressor-map-sorted\n',map2,'\n\n\n')
    
    
    new_map1 = list({key:val for key,val in list(map2.items()) if '1' in key or '0' in key}.items())
    new_map1.sort(key = lambda x: len(x[0]), reverse = True)
    new_map2 = {}
    for i in new_map1:
        new_map2.update({i[0]:i[1]})
    # for substr, replacement in newmap2.keys():
    #     st.replace()

    # First replacing 0s and 1s separately 
    st = replace_01(st,new_map2)
    for item in new_map2.keys():
        del map2[item]
    print('compressor-map-sorted2 no 0,1\n',map2,'\n\n\n')

    
    # Now replacing other characters
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
    print('newstr:\n',newstr,'\n\n\n')

    # Structure of defbyte = 1 + 4 digits of separator value + 3 digits of zero padding value
    if len(newstr.split()[-1]) == 8: # checks the last element length
        exdigitlen = 8
    else:
        exdigitlen = len([i for i in newstr.split() if len(i)<8][0])

    definerbyte = '1'+ str(bin(len(list(map2.values())[0])))[2:].zfill(4) + str(bin(8-exdigitlen))[2:].zfill(3)
    print('defbyte:\n',definerbyte,'\n\n\n')
    
    binlist = [definerbyte]+(newstr+((8-exdigitlen)*'0')).split() # It contains Defbyte + zero padded bytes
    print('binlist:\n',binlist,'\n\n\n')
    int_list = [int(i,2) for i in binlist] # This list contains the number equivalent of the bytes
    print('intlist:\n',int_list,'\n\n\n')
    return int_list



def compressfile(filepath, smode=3, mapsmode=1):
    """  
    There are two compression parameters:

        A) speedmode(1-5):  This mode puts a cap on the ngram checking parameter to improve speed
            1 - Best Compression,    ngram search limit(50gram)
            2 - Good Compression,    ngram search limit(36gram)
            3 - Normal Compression,  ngram search limit(18gram)
            4 - Fast Compression,    ngram search limit(9gram)
            5 - Fastest Compression, ngram search limit(6gram)
        These numbers are decided to personal choice only! They have no logical reasoning behind them (hamari marzi😜)
        
        B) mapsizemode(1-5): This mode puts the cap on the size of mapping dictionary to change compression quality
            1 - 32mb
            2 - 64mb
            3 - 128mb
            4 - 256mb
            5 - 512mb
        Putting a cap on mapping dictionary size WONT necessarily, but CAN reduce the compression limit
        Lower size of mapping dict means removal of low efficiency ngrams 
    """   
    fobj = open(filepath,encoding='utf-8')
    st = fobj.read()
    fobj.close()
    premap = pre_mapping(st,smode,mapsmode)
    mapdict = mapping(premap)
    
    compressed = compressor(st,mapdict)
        
    maplist = list(mapdict.keys()) # this contains only the keys of dictionary
    print('maplist-compressfile:\n',maplist,'\n\n\n')
    serialised_maplist = msgpack.packb(maplist) # The list is converted into a msgpack object for serialisation
    
    len_smapl = str(bin(len(serialised_maplist)))[2:].zfill(32)
    
    headerbytes = bytearray([int(len_smapl[8*i:8*(i+1)],2) for i in range(4)])

    filext = bytes(str(os.path.basename(filepath)).split('.')[1]+'.','utf-8')
    
    compressed_data = filext+bytes(headerbytes)+bytes(serialised_maplist)+bytes(compressed)  # This contains compressed data in the format:
    print('comp data:',compressed_data)
    compfilename = str(os.path.basename(filepath)).split('.')[0]+'.azy'                   # file extention + '.' + 4 bytes of lenght of maplist + maplist + compressed string(with first byte as defbyte)
    
    with open(compfilename,'wb') as f:
        f.write(bytearray(compressed_data)) #bytearray function converts the number back to binary to write in the file

    
    
# This function creates a chunker object which can used with next() function to read data in chunks
def chunker(filepath,mode,maplistlen = 512,seek=0,):
        # File path gives path to file which is to be loaded
        # Mode gives the amount of memory to be used out of available memory (1-10)
        # Get current available to memory
        available_memory = floor(psutil.virtual_memory()[1]*(mode/10))
        # This will take half of the available memory minus the header bytes(4), the definer byte(1) and the len(maplist)
        chunk_size = floor((available_memory-(maplistlen+5)-(available_memory*0.05))/2)   
        
        with open(filepath,'rb') as fobj:
            fobj.seek(seek,0)
            while True:
                data = fobj.read(chunk_size)
                if not data:
                    break
                yield data

# This function will decompress a compressed file on the basis of the mode given
def decompressfile(filepath,mode=9):
    # First we read the file extension
    with open(filepath,'rb') as f:
        file_ext = f.read(6).split(b'.')[0].decode('utf-8')
        len_filext = len(file_ext)+1 # we add 1 for the '.' we use as the separator
        print(file_ext)
        print(len_filext)
    # First we read the headerbytes and get the length of maplist
    with open(filepath,'rb') as fobj:
        fobj.seek(len_filext,0)
        maplist_len = int.from_bytes(fobj.read(4), byteorder='big', signed=False)
    
    # Now we read the file again, the file point is set to 4, read till length of maplist
    
    # The available memory is split into 3 parts:
    # 1) First part is reserved for mapping dict which is equal to the lenght of mapdict
    # 2) In the second part, 5% of available memory is reserve memory, which is not utilised and is kept for emergency stack overflow
    # 3) The rest of the available memory is divided in two halves which is used for operations on compressed string and reading writing operations.
    
    # First load maplist into memory. Max size(512 megabytes) 
    with open(filepath,'rb') as fobj:
        fobj.seek(len_filext+4,0)
        packed_maplist = fobj.read(maplist_len)

    # Creating a mapping dict to store the data from mapping list to mapping dict
    maplist = msgpack.unpackb(packed_maplist)
    print('maplist:\n',maplist,'\n\n\n')
    

    # Now we read the definer byte of the compressed string
    with open(filepath,'rb') as fobj:
        fobj.seek(len_filext+4+maplist_len,0)
        read_defbyte = fobj.read(1)
        defbyte = str(bin(int.from_bytes(read_defbyte, byteorder='big')))[2:].zfill(8)
        sepval = int(defbyte[1:5],2)
        zeropadval =int(defbyte[5:],2)
        print('definer byte:',defbyte)
        print('sepval:',sepval)
        print('zeropadval:',zeropadval,'\n\n\n')
    mapdict = {str(bin((i)))[2:].zfill(sepval):maplist[i] for i in range(len(maplist))}
    print('mapdict after sepval\n',mapdict,'\n\n\n')
    # Now we read the compressed string but in chunks
    
    # Below is the generator object which will automatically delete the last chunk of data loaded into memory if not in use.
    chunkgen = chunker(filepath,mode,maplistlen=maplist_len,seek=(len_filext+5+maplist_len))
    print(mapdict)
    try:
        while True:
            chunk = list(next(chunkgen))
            for index,val in enumerate(chunk):
                chunk[index] = str(bin(val))[2:].zfill(8)
            print('chunk1:',chunk,'\n')

            # Removing zeropadding
            exitdigit = chunk[-1][:8-zeropadval]
            chunk.pop()
            chunk.append(exitdigit)
            chunk = ''.join(chunk) 
            print('chunk2- no zero padding:',chunk,'\n')
            
            chunk = [chunk[i:i+sepval] for i in range(0, len(chunk), sepval)] # splits the string with the separator value
            
            print('chunk3- split with sepval:',chunk,'\n')
            # Now decoding the data with the help of the mapping dict
            for index, val in enumerate(chunk):
                if val in mapdict:
                    chunk[index] = mapdict[val]
            print('chunk4- decoded data:',chunk,'\n')
            # Now we convert it into a string
            for i in range(len(chunk)-1):
                chunk[0] = chunk[0] + chunk.pop(1)
            print('chunk5- list containing decomp:',chunk)
            # Now we write the contents into the file
            decompfilename = str(os.path.basename(filepath)).split('.')[0]+'-decomp.'+ file_ext
            with open(decompfilename,'a') as fobj:
                fobj.write(chunk[0])

    except StopIteration:
        pass


# pre_mapping('Hi guys my name is azmat hussain and I am a very good good boy with very handsome looks and I also like to sing',1,3)

import timeit
 
startTime = timeit.default_timer()

compressfile('test.txt',5,1)

endTime = timeit.default_timer()
 
print('Time Taken:',endTime - startTime)
