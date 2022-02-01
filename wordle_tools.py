from functools import reduce
from itertools import product
from collections import defaultdict

import pandas


LOWER_ALPHABET_SET = set('abcdefghijklmnopqrstuvwxyz')
UPPER_ALPHABET = sorted({x.upper() for x in LOWER_ALPHABET_SET})

FIVE_LETTER_WORDS_SET = {
    w.strip().upper()
    for w in open('wordle_words.txt', 'r').read().split('\n')
    if w.strip()
    if set(w.lower()) & LOWER_ALPHABET_SET == set(w.lower())
    if len(w) == 5
}

print(len(FIVE_LETTER_WORDS_SET))
SORTED_FIVE_LETTER_WORDS = sorted(FIVE_LETTER_WORDS_SET)


def read_spine_file(fp):
    return [
        item.split(' ')
        for item in open(fp, 'r').read().split('\n')
        if item.strip()
    ]


ILLS_WORDS = [
    w for w in SORTED_FIVE_LETTER_WORDS if w.endswith('ILLS')
]

ILLS_STRONG_SPINES = read_spine_file('strong_spines.txt')

ILLS_SPINE_WORDS = sorted({w for s in ILLS_STRONG_SPINES for w in s})


def wordl_score(guess, solution):

    res = [0, 0, 0, 0, 0]
    
    for i, letter in enumerate(solution):
        if guess[i] == letter:
            res[i] = 2
        else:
            for j, guessed_letter in enumerate(guess):
                if guessed_letter == letter:
                    if res[j] == 0:
                        res[j] = 1
                        break
    return tuple(res)


def wordle_vector(word):
    return [
        int(item)
        for letter in UPPER_ALPHABET
        for item in (
            word[0] == letter,
            word[1] == letter,
            word[2] == letter,
            word[3] == letter,
            word[4] == letter,
            letter in word
        )
    ]


SORTED_FIVE_LETTER_WORDLE_VECTORS = [
    wordle_vector(word) for word in SORTED_FIVE_LETTER_WORDS
]


def p_info(i, n_v, all_wv):
    p = sum(v[i] for v in all_wv) / n_v
    return p * (1-p)


def dot(a, b):
    return sum(ai * bi for (ai, bi) in zip(a, b))


def info_vector_for_some_words(some_words):

    wv = [wordle_vector(word) for word in some_words]
    n_v = len(wv)
    return [p_info(i, n_v, wv) for i in range(156)]


N_V = len(SORTED_FIVE_LETTER_WORDLE_VECTORS)

THIS = [p_info(i, N_V, SORTED_FIVE_LETTER_WORDLE_VECTORS) for i in range(156)]

INFO_RANK = {
    k: v
    for v, k in sorted(
        zip(
            [dot(v, THIS) for v in SORTED_FIVE_LETTER_WORDLE_VECTORS],
            SORTED_FIVE_LETTER_WORDS
        )
    )
}


def tabulate_strategy_from_search_result(r):
    
    possible_solutions, depth, guesses, scores = r
    
    return [min(possible_solutions), depth] + [
        item
        for i, guess in enumerate(guesses)
        for items in (
            (guess,),
            scores[i+1]
        )
        for item in items
    ]
    

def tabulate_strategy_from_search_results(results):
    
    rows = [
        tabulate_strategy_from_search_result(r)
        for r in results
    ]
    
    max_depth = max(item[1] for item in rows)
    
    column_names = [
        item
        for entries in (
            (
                (
                    'word',
                    'depth',
                ),
            ),
            (
                (
                    'g{}'.format(n),
                    's{}1'.format(n),
                    's{}2'.format(n),
                    's{}3'.format(n),
                    's{}4'.format(n),
                    's{}5'.format(n),
                )
                for n in range(1, max_depth + 1)
            )
        )
        for entry in entries
        for item in entry
    ]
    
    return pandas.DataFrame(rows, columns=column_names)


def map_df_back_to_strategy_dict(df):

    dict_1 = {
        (
            (
                r[2],
            ),
            (
                tuple(map(int, r[3:8])),
            )
        ): r[8]

        for r in df.values
        if r[8]
    }

    dict_2 = {
        (
            (
                r[2],
                r[8]
            ),
            (
                tuple(map(int, r[3:8])),
                tuple(map(int, r[9:14])),
            )
        ): r[14]

        for r in df.values
        if r[14]
    }

    dict_3 = {
        (
            (
                r[2],
                r[8],
                r[14]
            ),
            (
                tuple(map(int, r[3:8])),
                tuple(map(int, r[9:14])),
                tuple(map(int, r[15:20])),
            )
        ): r[20]

        for r in df.values
        if r[20]
    }

    dict_4 = {
        (
            (
                r[2],
                r[8],
                r[14],
                r[20]
            ),
            (
                tuple(map(int, r[3:8])),
                tuple(map(int, r[9:14])),
                tuple(map(int, r[15:20])),
                tuple(map(int, r[21:26])),
            )
        ): r[26]

        for r in df.values
        if r[26]
    }

    dict_5 = {
        (
            (
                r[2],
                r[8],
                r[14],
                r[20],
                r[26]
            ),
            (
                tuple(map(int, r[3:8])),
                tuple(map(int, r[9:14])),
                tuple(map(int, r[15:20])),
                tuple(map(int, r[21:26])),
                tuple(map(int, r[27:32])),
            )
        ): r[32]

        for r in df.values
        if r[32]
    }
    
    return {
        k: v
        for dict_x in (dict_1, dict_2, dict_3, dict_4, dict_5)
        for k, v in dict_x.items()
    }


def split_wordle_set(stack_item, guess):
    depth = stack_item[1]
    word_set = stack_item[0]
    previous_guesses = stack_item[2]
    previous_keys = stack_item[3]
    
    pieces = defaultdict(set)
    for word in word_set:
        pieces[wordl_score(guess, word)].add(word)
    return [
        (
            v,
            depth + 1,
            tuple(list(previous_guesses) + [guess, ]),
            tuple(list(previous_keys) + [k, ]),
        )
        for k, v in pieces.items()
    ]


def apply_wordle_strategy(guessing_strategy, *strategy_args):

    wordle_stack = []  # A stack of tree nodes, each a tuple, containing:
    
    root_node = (
        set(SORTED_FIVE_LETTER_WORDS),  # the remaining possible words
        0,  # the depth, or number of guesses made so far
        '',  # the words guessed so far
        ('!',)  # the wordle scores of the guesses so far, with '!' representing no guesses at the start of the game.
    )
    
    wordle_stack.append(root_node)
    
    tree = [(root_node, None)]
    
    results = []

    pop_count = 0
    while wordle_stack:

        stack_item = wordle_stack.pop()
        pop_count += 1

        if stack_item[3][-1] == (2, 2, 2, 2, 2):
            results.append(stack_item)

        else:
            
            guess = guessing_strategy(stack_item, *strategy_args)
            
            children = split_wordle_set(stack_item, guess)
            
            for child in children:
                tree.append((child, stack_item))
            
            wordle_stack.extend(children)

    return results, tree


def max_info_for_word_set(n_words, word_set):
    sorted_stack_word_vectors = [
        wordle_vector(word) for word in word_set
    ]
    info_vector = [
        p_info(i, n_words, sorted_stack_word_vectors) for i in range(156)
    ]
    guess = max(
        zip(
            [dot(v, info_vector) for v in sorted_stack_word_vectors],
            word_set
        )
    )[-1]
    return guess


def max_info_within_possible_solutions(stack_item):

    sorted_stack_words = sorted(stack_item[0])
    n_words = len(sorted_stack_words)

    guess = max_info_for_word_set(n_words, sorted_stack_words)

    return guess


def calculate_max_group_size_given_guess(guess, possible_solutions):
    
    groups = defaultdict(list)
    
    for word in possible_solutions:
        groups[wordl_score(guess, word)].append(word)
    
    return max([len(group) for group in groups.values()])


def min_max_groups_among_children(stack_item, guess_options, root_word):
    
    if stack_item[1] == 0:
        return root_word
    
    possible_solutions = stack_item[0]
    if len(possible_solutions) < 3:
        return min(possible_solutions)
    
    max_group_sizes = [
        (guess, calculate_max_group_size_given_guess(guess, possible_solutions))
        for guess in guess_options
    ]
    min_max_group_size = min(item[1] for item in max_group_sizes)
    guesses_with_min_max = [item[0] for item in max_group_sizes if item[1] == min_max_group_size]
    return max(guesses_with_min_max, key=lambda k: INFO_RANK[k])


def max_info_within_all_words(stack_item, root_word):
        
    if stack_item[1] == 0:
        return root_word
    
    possible_solutions = stack_item[0]
    
    if len(possible_solutions) < 3:
        return min(possible_solutions)
    
    else:

        sorted_stack_words = sorted(stack_item[0])
        n_words = len(sorted_stack_words)

        sorted_stack_word_vectors = [
            wordle_vector(word)
            for word in sorted_stack_words
        ]

        info_vector = [
            p_info(i, n_words, sorted_stack_word_vectors)
            for i in range(156)
        ]

        guess = max(
            zip(
                [
                    dot(v, info_vector)
                    for v in SORTED_FIVE_LETTER_WORDLE_VECTORS
                ],
                SORTED_FIVE_LETTER_WORDS
            )
        )[-1]

        return guess


def play_from_strategy_dictionary(stack_item, strategy_dict, root_word):
        
    if stack_item[1] == 0:
        return root_word
    
    recorded_move = strategy_dict.get(
        (
            stack_item[2],
            tuple(stack_item[3][1:])
        ),
        None
    )
    
    if recorded_move is None:
        
        print('missing move for:')
        print(stack_item)
        
        return min_max_groups_among_children(
            stack_item,
            SORTED_FIVE_LETTER_WORDS,
            root_word
        )
            
    else:
        return recorded_move


def sieve_batch_file(batch_fp, sieve_words, letters_to_check=None):
    
    if letters_to_check is None:
        letters_to_check = {w[0] for w in sieve_words}
    
    qb = [
        y.split(' ')
        for y in [
            x.strip()
            for x in open(batch_fp, 'r').read().split('\n')
            if x.strip()
        ]
    ]
    
    res = []
    required_letters = set(letters_to_check)

    for r in qb:

        a, b, c, d, e = r

        intersection_count = len(
            (set(a) | set(b) | set(c) | set(d) | set(e)) & required_letters
        )

        if intersection_count >= len(required_letters) - 1:
            res.append(r)
            
    return [
        r for r in res
    ]


def check_partitions(q_key, sieve_words):

    x = [
            tuple(
                wordl_score(q_word, w)
                for q_word in q_key
            )
            for w in sieve_words
        ]
    return len(x) == len(set(x))


def process_batch_files(fps):

    res = []

    for fp in fps:
        print(fp)
    
        sieved_q_keys = sieve_batch_file(fp, ILLS_WORDS)

        res.extend(
            [
                qk
                for qk in sieved_q_keys
                if check_partitions(qk, ILLS_WORDS)
            ]
        )
    return res


def process_batch_files_expert_solve(fps, one_off_pattern):
    
    pattern_words = [
        w for w in SORTED_FIVE_LETTER_WORDS
        if all(
            (w[i] == one_off_pattern[i]) or (one_off_pattern[i] == '_')
            for i in range(5)
        ) 
    ]
    
    letters_to_check = {
        letter
        for word in pattern_words
        for i, letter in enumerate(word)
        if one_off_pattern[i] == '_'
    }
    
    spines = set()
    for fp in fps:
        print(fp)
    
        sieved_q_keys = sieve_batch_file(fp, pattern_words, letters_to_check)

        spines |= {
            
                tuple(qk)
                for qk in sieved_q_keys
                if check_partitions(qk, pattern_words)
        }
        
    return sorted(list(s) for s in spines), pattern_words


def top_one_off_patterns(some_words):
    
    one_offs = defaultdict(list)
    
    for w in some_words:
        for position in range(5):
            one_offs[
                '{}_{}'.format(
                    w[:position],
                    w[position + 1:]
                )
            ].append(w)
    return one_offs, sorted([
        (len(v), k)
        for k, v in one_offs.items()
    ])[::-1][:100]


def filter_to_strong_spines(spines, words_to_isolate):
    
    wordle_score_index = {
        k: v
        for v, k in enumerate(
            sorted(
                product((0, 1, 2), (0, 1, 2), (0, 1, 2), (0, 1, 2), (0, 1, 2))
            )
        )
    }
    
    qw_lookup = {
        (q, w): wordle_score_index[wordl_score(q, w)]
        for q in sorted({qk for s in spines for qk in s})
        for w in SORTED_FIVE_LETTER_WORDS
    }
    
    qs_to_words = defaultdict(set)
    for (q, w), score_index in qw_lookup.items():
        qs_to_words[(q, score_index)].add(w)

    strong_spines = []
    
    for spine in spines:
        
        keys_to_check = {
            tuple(
                (q, qw_lookup[(q, word)])
                for q in spine
            )
            for word in words_to_isolate
        }

        if all(
            len(reduce(
                set.intersection,
                (
                    qs_to_words[item]
                    for item in key_to_check
                )
            )) == 1
            for key_to_check in keys_to_check
        ):
            strong_spines.append(spine)
    
    return strong_spines
    

def sieve_batch_file_for_spines_with_word(batch_fp, word):
       
    qb = [
        y.split(' ')
        for y in [
            x.strip()
            for x in open(batch_fp, 'r').read().split('\n')
            if x.strip()
        ]
    ]
    
    return [r for r in qb if word in r]
