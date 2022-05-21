import os
import csv

os.chdir(os.path.dirname(os.path.abspath(__file__)))

datums = csv.reader(open("./books.tsv", "r"), delimiter="\t", )

books = []
for d in list(datums)[1:]:
    d = [f'"{b.strip()}"' if b else "nil" for b in d]
    books.append(f"{{{', '.join(d)}}}")
all_books = ",\n  ".join(books)
print(f"{{\n  {all_books}\n}}")
