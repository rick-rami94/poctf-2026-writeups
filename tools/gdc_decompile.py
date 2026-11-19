#!/usr/bin/env python3
"""Minimal Godot 4.x GDScript bytecode (.gdc) decompiler.

Parses the identifier/constant/line/token tables and reprints readable source.
Handles zstd-compressed .gdc payloads. Built for POCTF 2026 game-hacking
challenges; token map matches Godot 4.3's GDScriptTokenizer.

Usage:
    python3 gdc_decompile.py scenes/arena/boss.gdc
"""
import struct,sys,subprocess
T="EMPTY ANNOTATION IDENTIFIER LITERAL < <= > >= == != and or not && || ! & | ~ ^ << >> + - * ** / % = += -= *= **= /= %= <<= >>= &= |= ^= if elif else for while break continue pass return match when as assert await breakpoint class class_name const enum extends func in is namespace preload self signal static super trait var void yield [ ] { } ( ) , ; . .. ... : $ -> _ NEWLINE INDENT DEDENT PI TAU INF NAN VCS ` ? ERROR EOF".split()
def var(b,p):
    h=struct.unpack('<I',b[p:p+4])[0];p+=4;t=h&0xff;f64=h&(1<<16)
    if t==0:return None,p
    if t==1:return bool(struct.unpack('<I',b[p:p+4])[0]),p+4
    if t==2:
        if f64:return struct.unpack('<q',b[p:p+8])[0],p+8
        return struct.unpack('<i',b[p:p+4])[0],p+4
    if t==3:
        if f64:return struct.unpack('<d',b[p:p+8])[0],p+8
        return struct.unpack('<f',b[p:p+4])[0],p+4
    if t in(4,21,22):
        l=struct.unpack('<I',b[p:p+4])[0];p+=4;s=b[p:p+l].decode('utf8','replace');p+=(l+3)&~3;return s,p
    if t==5:return struct.unpack('<ff',b[p:p+8]),p+8
    if t==9:return struct.unpack('<fff',b[p:p+12]),p+12
    if t==20:return ('Color',struct.unpack('<ffff',b[p:p+16])),p+16
    raise Exception('variant type %d'%t)
raw=open(sys.argv[1],'rb').read()
ds=struct.unpack('<I',raw[8:12])[0]
b=subprocess.run(['zstd','-dc'],input=raw[12:],capture_output=True).stdout if ds else raw[12:]
ic,cc,lc,tc=struct.unpack('<4I',b[:16]);p=16
ids=[]
for i in range(ic):
    l=struct.unpack('<I',b[p:p+4])[0];p+=4
    ids.append(bytes(x^0xb6 for x in b[p:p+l*4]).decode('utf-32le'));p+=l*4
cs=[]
for i in range(cc):
    v,p=var(b,p);cs.append(v)
lm={};cm={}
for i in range(lc):
    a,c=struct.unpack('<II',b[p:p+8]);p+=8;lm[a]=c
for i in range(lc):
    a,c=struct.unpack('<II',b[p:p+8]);p+=8;cm[a]=c
lines={}
for i in range(tc):
    tk,ln=struct.unpack('<II',b[p:p+8]);p+=8
    tk&=0x7fffffff;ty=tk&0x7f if tk&0x80 or True else tk;ty=tk&0x7f;d=tk>>8
    n=T[ty] if ty<len(T) else '?%d'%ty
    if n in('NEWLINE','INDENT','DEDENT','EOF'):continue
    if n in('IDENTIFIER',):s=ids[d]
    elif n=='ANNOTATION':s='@'+ids[d]
    elif n=='LITERAL':s=repr(cs[d])
    else:s=n
    if ln not in lines: lines[ln]=[cm.get(i,1),[]]
    lines[ln][1].append(s)
for ln in sorted(lines):
    c,t=lines[ln];print('%4d %s%s'%(ln,' '*max(c-1,0),' '.join(t)))
