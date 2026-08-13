import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

funcs = ['getPixPersonalPayload', 'getPixAddressPayload', 'loadRewardSelection', 'saveRewardSelection', 'STORAGE_KEYS']

for fn in funcs:
    pos = js.find(fn)
    print(f"=== {fn} ===")
    if pos != -1:
        print(js[pos:pos+600])
        print("\n" + "="*40 + "\n")

