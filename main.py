import sys

if len(sys.argv) != 4:
    print("Usage: python main.py <YOUR_BOOK.pdf> <CHUNK_SIZE> <DECK_NAME_PREFIX>")
    print("e.g. python main.py books/mybook.pdf 1000 \"My Book\"")
    exit(1)
book_path = sys.argv[1]
chunk_size = int(sys.argv[2])
deck_prefix = sys.argv[3]

import random, re, os
from tika import parser
import translators
import enchant
from ankipandas import Collection
import genanki
from gtts import gTTS

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

def random_id():
    return int(random.random()*100000000000)

media_model = genanki.Model(
  random_id(),
  'Simple Model with Media',
  fields=[
    {'name': 'Question'},
    {'name': 'Answer'},
    {'name': 'MyMedia'},                                  # ADD THIS
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '{{Question}}<br>{{MyMedia}}',              # AND THIS
      'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
    },
  ])

def translate_word(word):
    translation = translators.google(word, from_language="es", to_language="en")
    if translation.lower() != word:
        return translation

def get_media(word):
    file_path = "output_decks/media/"+word+".mp3"
    gTTS(text=word, lang="es", slow=False).save(file_path)
    return (file_path, "[sound:"+word+".mp3]")

word_sets = [word_sets[0]]
i = 1
for word_set in word_sets:
    deck_name = deck_prefix + " " + str(i)
    my_deck = genanki.Deck(random_id(),deck_name )
    media_files = []
    for word in word_set:
        translation = translate_word(word)
        if translation:
            media = get_media(word)
            my_note = genanki.Note(model=media_model, fields=[word, translation, media[1]])
            media_files.append(media[0])
            my_deck.add_note(my_note)
    my_package = genanki.Package(my_deck)
    my_package.media_files = media_files
    my_package.write_to_file("output_decks/"+deck_name+'.apkg')
    i+=1
