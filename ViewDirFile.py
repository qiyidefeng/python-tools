# -*- coding:utf-8 -*- 
import re
import sys

if len(sys.argv)!=2:
    print 'Usage: python [].py filename'

f=open(sys.argv[1])
s=f.read().decode('utf-8')

m=re.search(r' Directory of .*', s)
tmp=m.group()
root=tmp.split('of ')[1].strip()

if root.endswith('\\'):
    root=root[:-1]
pwd=root

pattern=r'.*?\d+ bytes'
m=re.search(pwd+pattern, s, re.I|re.S)
print m.group()

while True:
    in_s=raw_input(pwd+'>')
    in_s=in_s.strip()
    in_s=in_s.replace('(', '\(')
    in_s=in_s.replace(')', '\)')
    
    if in_s=='' or in_s=='.':
        continue
    elif in_s=='..':
        if pwd==root:
            continue
        while(pwd[-1]!='\\'):
            pwd=pwd[:-1]
        pwd=pwd[:-1]
    else:
        tmp=pwd+'\\'+in_s
        print tmp
        m=re.search(tmp+pattern, s, re.I|re.S)
        if m is None:
            print 'Dir does not exits.'
        else:
            pwd=tmp
            print m.group()


