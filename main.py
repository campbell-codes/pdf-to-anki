import sys, re, os

if len(sys.argv) != 3:
    print("Usage: python main.py <YOUR_BOOK.pdf> <CHUNK_SIZE>")
    print("e.g. python main.py books/mybook.pdf 1000")
    exit(1)
book_path = sys.argv[1]
chunk_size = int(sys.argv[2])

from tika import parser
import translators as ts
import enchant
from ankipandas import Collection

def extract_question_from_cards(anki2_path):
    col = Collection(anki2_path)
    card_values = col.notes.to_dict()['nflds']
    stripped_questions = []
    for card in card_values.items():
        # A very crude way to extract the actual word (ignoring la, el...)
        card_word = card[1][0].split("[")[0].split(" ")[-1].lower()
        # Remove any html formatting very crude again
        html_content = re.search(r">([a-zA-ZA-zÀ-ú]+)<", card_word)
        if html_content:
            card_word = html_content.group(1)
        # strip any remaining special chars or punctuation
        text_only_matches = re.search(r"[a-zA-ZA-zÀ-ú]+", card_word)
        try:
            stripped_questions.append(text_only_matches[0])
        except:
            print("warning failed to save card with content: " + card_word)
            print("original: " + card[1][0])
    return stripped_questions

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]



exclude_words = []
for dir in os.walk("exclude_cards"):
    # Walk files only
    for f in dir[2]:
        if f.endswith(".anki2"):
            anki_path = dir[0] + "/" + f
            print("Adding to exclusion: " + anki_path)
            exclude_words += extract_question_from_cards(anki_path)

print("Ignoring " + str(len(exclude_words)) + " exclude words")

word_dict = enchant.request_dict("es_ES")

raw = parser.from_file(book_path)
all_words = re.findall("[a-zA-ZA-zÀ-ú]+", raw['content'])

word_frequency = {}

# Convert words to lower case and remove non words e.g. names, muggles...
for word_with_case in all_words:
    word = word_with_case.lower()
    if word in word_frequency:
        word_frequency[word] += 1
    elif word_dict.check(word):
        word_frequency[word] = 1

all_words_in_book = word_frequency.copy()

for word in exclude_words:
    if word in word_frequency:
        del word_frequency[word]

# print(word_frequency)
words_sorted = sorted(word_frequency, key=word_frequency.get, reverse=True)

word_sets = list(divide_chunks(words_sorted, chunk_size))

def calculate_book_percentage(learned_words, word_frequencies):
    learned_count = 0
    not_learned_count = 0

    for word in word_frequencies:
        if word in learned_words:
            learned_count += word_frequencies[word]
        else:
            not_learned_count += word_frequencies[word]

    return (learned_count / (learned_count + not_learned_count))*100

total_set = exclude_words
print("Comprehension Level")
print("Exclude Only: " + str(calculate_book_percentage(total_set, all_words_in_book)) + "%")

i = 1
for word_set in word_sets:
    total_set += word_set
    print("Exclude + " + str(i) + " sets : " + str(calculate_book_percentage(total_set, all_words_in_book)) + "%")
    i+=1
