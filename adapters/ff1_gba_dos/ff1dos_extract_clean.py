#!/usr/bin/env python3
import csv
import os
import sys
import re

ROM = sys.argv[1]
OUT = sys.argv[2]

with open(ROM, 'rb') as f:
    data = f.read()

dec = {}
# A-Z
for i in range(26): dec[0x8260+i]=chr(65+i)
# a-z
for i in range(26): dec[0x8281+i]=chr(97+i)
# 0-9
for i in range(10): dec[0x824f+i]=str(i)
# symbols
dec.update({
    0x8140:' ',0x8143:',',0x8144:'.',0x8146:':',0x8147:';',0x8148:'?',0x8149:'!',0x8151:'_',0x815e:'/',0x8166:"'",0x817c:'-',0x8193:'%',0x810a:'\n',0x8160:' ',0x827C:','
})
# icons
dec.update({0x8740:'[Sword]',0x8742:'[Knife]',0x8743:'[Nunchaku]',0x8746:'[Staff]',0x8747:'[Robe]',0x8749:'[Armlet]',0x874c:'[Gloves]',0x874d:'[W-MAG]',0x874e:'[B-MAG]',0x874f:'[Potion]',0x8750:'[Bag]'})

def decode_at(start, maxlen=150):
    out=[]; i=start; c=0
    while i+1<len(data) and c<maxlen:
        b=data[i]|(data[i+1]<<8)
        if b==0x0000: break
        if b in dec: out.append(dec[b])
        elif 0x8260<=b<=0x8279: out.append(chr(65+b-0x8260))
        elif 0x8281<=b<=0x829a: out.append(chr(97+b-0x8281))
        elif 0x824f<=b<=0x8258: out.append(chr(48+b-0x824f))
        else:
            # skip most control codes inline
            if b < 0x8000 or b > 0x9000:
                pass
            else:
                out.append(f'<{b:04X}>')
        i+=2; c+=1
    return ''.join(out), i

results=[]; seen=set(); idx=0

# Focused areas
areas=[
    ('Class',0x1da85c,0x1da980),
    ('ItemName',0x19a261,0x19a660),
    ('WeaponName',0x19a65a,0x19ac10),
    ('ArmorName',0x19ac06,0x19b320),
    ('SpellName',0x1a021d,0x1a0900),
    ('MonsterName',0x2257ac,0x226000),
    ('ItemDesc',0x19bc9f,0x19d500),
]

for label,start,end in areas:
    i=start
    while i<end-4:
        b=data[i]|(data[i+1]<<8)
        if 0x8260<=b<=0x829a or 0x824f<=b<=0x8258 or b==0x8140 or b in (0x8740,0x8742,0x8743,0x8746,0x8747):
            s,ni=decode_at(i,80)
            # clean
            s2=re.sub(r'<[0-9A-F]{4}>','',s)
            s2=s2.replace('[Sword]','').replace('[Knife]','').replace('[Nunchaku]','').replace('[Staff]','').replace('[Robe]','').replace('[Armlet]','').replace('[Gloves]','').replace('[W-MAG]','').replace('[B-MAG]','').replace('[Potion]','').replace('[Bag]','')
            s2=s2.strip()
            if len(s2)>=2 and len(s2)<=60:
                # avoid pure numbers/punctuation
                if re.search(r'[A-Za-z]',s2):
                    key=(label,s2)
                    if key not in seen:
                        seen.add(key)
                        results.append({'id':f'{label}_{idx:05d}','original':s2,'traducao':'','status':'pendente','nota':f'{i:08X}'})
                        idx+=1
            i=ni
            continue
        i+=2

os.makedirs(os.path.dirname(OUT),exist_ok=True)
with open(OUT,'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['id','original','traducao','status','nota'])
    w.writeheader()
    for r in results: w.writerow(r)
print(len(results))
