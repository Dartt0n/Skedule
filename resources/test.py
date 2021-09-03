import json
from pathlib import Path

a = {}

'''pathlist = Path('texts/').rglob('*.txt')
for path in pathlist:
     # because path is object not string
     path_in_str = str(path)
     
     with open(path_in_str, encoding='utf-8') as f:
          a.update({path_in_str[6:-4]:f.read()})

with open('texts/texts.json', 'w', encoding='utf-8') as f:    
     f.write(json.dumps(a,ensure_ascii = False))
'''
with open('texts/texts.json', encoding='utf-8') as f:
     shit = json.loads(f.read())
print(shit['confirm_class'])