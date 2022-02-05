# wordle_worst_case_analysis
Code and outputs from analysis determining that the wordle game can always be won in six moves.

This is for the general case where you assume all 12,972 valid wordle words could be the answer.

There is some good discussion of the problem here: https://puzzling.stackexchange.com/questions/114316/whats-the-optimal-strategy-for-wordle

The discovered solution starts at the word LARNT and can be found in full in the wordle_tree_larnt_lte_6_20220205.txt file.

0 denotes grey, 1 denotes yellow, 2 denotes green in the file.

This diagram below shows the handcrafted portion of the LARNT wordle tree with max depth 6. Notice the need to find sequences of words with good 'consonant harmony', i.e. they allow many different consonants to be tested in just a short sequence of words. This is the key idea to finding a strategy that ensures the word can always be guessed in 6 moves at most. The rest is a fairly straightforward local min-max search to divide and conquer cases. 

Now you just need very good memory, vocabulary, and logic and you will be safe each day at the wordle board!

![image](https://user-images.githubusercontent.com/63890649/151963926-df404aec-528e-4f3a-835d-dcfbb8bd2e12.png)
