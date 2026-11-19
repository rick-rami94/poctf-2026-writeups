#!/usr/bin/env python3
"""Extract files from an embedded Godot .pck (self-contained game executable).

Godot appends the PCK to the exe and writes its length in the last 12 bytes.
This finds the GDPC directory and carves every entry out to <outdir>.

Usage:
    python3 pck_extract.py POCTF2026-GH04.x86_64 ./pck_out
"""
import struct,sys,os
f=open(sys.argv[1],'rb').read(); out=sys.argv[2]
sz=struct.unpack('<q',f[-12:-4])[0]; s=len(f)-12-sz
fmt,ma,mi,pa,flags=struct.unpack('<5I',f[s+4:s+24])
base,diro=struct.unpack('<QQ',f[s+24:s+40])
print(fmt,ma,mi,pa,flags,base,diro)
p=s+diro
n=struct.unpack('<I',f[p:p+4])[0];p+=4
for i in range(n):
    l=struct.unpack('<I',f[p:p+4])[0];p+=4
    name=f[p:p+l].rstrip(b'\0').decode();p+=l
    off,size=struct.unpack('<QQ',f[p:p+16]);p+=16
    md5=f[p:p+16];p+=16
    fl=struct.unpack('<I',f[p:p+4])[0];p+=4
    name=name.replace('res://','')
    print(name,size,fl)
    d=os.path.join(out,name);os.makedirs(os.path.dirname(d) or out,exist_ok=True)
    open(d,'wb').write(f[s+base+off:s+base+off+size])
