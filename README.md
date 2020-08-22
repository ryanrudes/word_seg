# Self-supervised Word Segmentation
A Python script which trains a keras model to perform the low-level NLP task of word segmentation (inferring spaces within a string of text, ie. 'thisisagithubrepo' &rarr; 'this is a github repo'

Text is datascraped from [this](https://www.gutenberg.org/browse/scores/top) site, which contains raw text files of a variety of books. The text is messy, so the beginning of the program works to fix it up as much as possible.

Recommendation is 100 books, but you can customize the number of books scraped with a command-line argument, in addition to the number of parallel threads for downloading them: \
`python3 word_seg.py num-books num-concurrent-threads`, ie.`python3 word_seg.py 100`
