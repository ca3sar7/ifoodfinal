import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/backguard.js', 'r', encoding='utf-8') as f:
    bg = f.read()

pos = bg.find('window.location.href =')
if pos == -1:
    pos = bg.find('location.href')

print(bg[pos-200:pos+1500])

