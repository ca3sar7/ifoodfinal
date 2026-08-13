import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

pos = js.find('btnFinish?.addEventListener')
if pos == -1:
    pos = js.find('btnFinish.addEventListener')
if pos == -1:
    pos = js.find('btnFinish')

print(js[pos:pos+3000])

