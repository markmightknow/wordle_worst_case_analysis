from collections import defaultdict
import time
import sys
from functools import reduce
import gc


def viable_word(w):
    if 'X' in w:
        return False
    if 'Q' in w:
        return False
    if len(set(w)) != 5:
        if w[0] not in ('S', 'L'):
            return False
        if len(set(w[1:])) != 4:
            return False
        return True
    else:
        return True


def check_s_3(a,b,c):
    return not (('S' in a) and ('S' in b) and ('S' in c))

def check_l_3(a,b,c):
    return not (('L' in a) and ('L' in b) and ('L' in c))

def find_q(batch_start, batch_end):
    
    VIABLE_WORDS = [x.strip() for x in open('viable_words.txt', 'r').read().split('\n') if x.strip()]
    
    NEEDED_LETTERS = [
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'M', 'N', 'O', 'P', 'R', 'T', 'U', 'V', 'W', 'Y', 'Z'
    ]

    LS = {'L', 'S'}

    none_of_this = defaultdict(set)
    for word in VIABLE_WORDS:
        for letter in NEEDED_LETTERS:
            if letter not in word:
                none_of_this[letter].add(word)
        none_of_this['L'].add(word)
        none_of_this['S'].add(word)

    viable_words_prepared = {
        w: tuple(sorted(w))
        for w in VIABLE_WORDS
    }

    none_of_this_5 = defaultdict(set)
    for item in viable_words_prepared.values():
        none_of_this_5[item] = reduce(
            set.intersection,
            (
                none_of_this[letter]
                for letter in item
            )   
        )
    del none_of_this
    gc.collect()
    
    viable_words_prepared = {
        w: tuple(sorted(w))
        for w in VIABLE_WORDS
    }

    pairs = [
        (w, other_w)
        for w in VIABLE_WORDS
        for other_w in none_of_this_5[viable_words_prepared[w]]
        if w < other_w
    ]

    pairs_by_members = defaultdict(set)
    pairs_by_lower_member = defaultdict(list)
    for (a,b) in pairs:
        pairs_by_members[a].add(b)
        pairs_by_members[b].add(a)
        if a < b:
            pairs_by_lower_member[a].append(b)
        else:
            pairs_by_lower_member[b].append(a)
    quintuples = []

    for i,a in enumerate(sorted(VIABLE_WORDS[batch_start:batch_end + 1])):
        t_0 = time.time()
        quintuples_a = [
            (a, b, c, d, e)
            for b in pairs_by_lower_member[a]
            for c in pairs_by_lower_member[b]
            if check_s_3(a,b,c)
            if check_l_3(a,b,c)
            if c in pairs_by_members[a]        
            for d in pairs_by_lower_member[c]
            if d in pairs_by_members[b]
            if d in pairs_by_members[a]
            if check_s_3(d,b,c)
            if check_s_3(d,a,c)
            if check_s_3(d,a,b)
            if check_l_3(d,b,c)
            if check_l_3(d,a,c)
            if check_l_3(d,a,b)

            for e in pairs_by_lower_member[d]
            if e in pairs_by_members[c]
            if e in pairs_by_members[b]
            if e in pairs_by_members[a]
            if check_s_3(e,b,c)
            if check_s_3(e,a,c)
            if check_s_3(e,a,b)
            if check_s_3(e,d,c)
            if check_s_3(e,d,b)
            if check_s_3(e,d,a)
            if check_l_3(e,b,c)
            if check_l_3(e,a,c)
            if check_l_3(e,a,b)
            if check_l_3(e,d,c)
            if check_l_3(e,d,b)
            if check_l_3(e,d,a)       
        ]
        print(i, len(quintuples_a), time.time() - t_0)
        quintuples.extend(quintuples_a)
    open('quintuple_batch_{}_{}.txt'.format(batch_start, batch_end), 'w').write(
        '\n'.join(
            ' '.join(sorted(item))
            for item in sorted(quintuples)
        )
    )
    
if __name__ == '__main__':
    find_q(int(sys.argv[1]), int(sys.argv[2]))
