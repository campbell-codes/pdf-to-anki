## Description
Builds Anki language decks from books if the books are pdfs, for Spanish only.

This will take a Spanish book and generate an anki deck with english translations and text to speech sounds included in the deck.

### Warning
The code in here is pretty hacky and is just for personal use it would probably need modification for others and was written very quickly. This will almost certainly not work out of the box and is not an example of well written code.

### Install Pre-reqs

```
pip install -r requirements.txt
```

### Prep Your Exclude Cards
Existing anki decks can be excluded from newly generated decks. To ensure your cards are excluded place the unzipped `.anki2` files in `exclude_cards` these can be in sub directories. e.g.
```
# From inside exclude_cards/
unzip my_deck.apkg
ls my_deck/
# Output
# deck.anki2	media
````

### Run The Script With Your Book
```
# e.g.
python3.9 main.py books/harry-potter-2-la-camara-secreta.pdf 1000 "La Cámara Secreta"
```

This will output decks of size 1000 with deck 1 having the most frequent words occuring in the book and the final deck having the least frequent.

This will also output how much of the book is already covered by your exclude words and how much of the book would be covered if you learnt each deck.
