import os

dirs = [
    'c:/xampp/htdocs/ifood',
    'c:/xampp/htdocs/ifood/quiz-clone'
]

invalid_found = []

for d in dirs:
    for root, dirs_list, files in os.walk(d):
        for f in files:
            if '#' in f or '?' in f:
                full_p = os.path.join(root, f)
                invalid_found.append(full_p)
                print("Found invalid filename:", full_p)
                try:
                    os.remove(full_p)
                    print("  -> Removed invalid file!")
                except Exception as e:
                    print("  -> Could not remove:", e)

if not invalid_found:
    print("Zero invalid filenames found!")

