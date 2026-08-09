import sys
p = sys.argv[1]
c = open(p, 'r', encoding='utf-8').read()
c = c.replace('\u2713', '[OK]')
c = c.replace('\u2192', '->')
c = c.replace('\u2705', '[DONE]')
open(p, 'w', encoding='utf-8').write(c)
print('Fixed')
