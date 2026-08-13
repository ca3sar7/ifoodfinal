import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

pos = js.find('async function createPixCharge')
if pos != -1:
    print(js[pos+3000:pos+6000])

