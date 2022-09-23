## Description
Builds Anki language collections from books if the books are pdfs, for Spanish only

### Warning
The code in here is pretty hacky and just for personal use would probably need modification for others and was written very quickly. This will almost certainly not work out of the box and is not an example of well written code.

### Install Pre-reqs

```
pip install -r requirements.txt
```

### Prep Your Exclude Cards
Existing anki collections can be excluded from newly generated collections. To ensure your cards are excluded place the unzipped `.anki2` files in `exclude_cards` these can be in sub directories. e.g.
```
# From inside exclude_cards/
unzip my_collection.apkg
ls my_collection/
# Output
# collection.anki2	media
````

### Run The Script With Your Book
```
python main.py books/my_book.pdf
```

This will also output how much of the book is already covered by your exclude words and how much of the book would be covered if you learnt each collection.
