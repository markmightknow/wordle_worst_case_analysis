# wordle_worst_case_analysis
Code and outputs from analysis determining that the wordle game can always be won in six moves.

This is for the general case where you assume all 12,972 valid wordle words could be the answer.

The discovered solution starts at the word LARNT and can be found in full in the wordle_tree_larnt_lte_6_20220201.txt file.

0 denotes grey, 1 denotes yellow, 2 denotes green in the file.

This diagram shows the handcrafted portion of the LARNT wordle tree with max depth 6: 

![image](https://user-images.githubusercontent.com/63890649/151963926-df404aec-528e-4f3a-835d-dcfbb8bd2e12.png)
