# async-dnsbl-client
Asynchronous dnsbl client

## Install
~~~
pip3 install async-dnsbl-client
~~~
or
~~~
pip3 install git+https://github.com/yaroslaff/async-dnsbl-client
~~~

## CLI usage:
~~~
$ adnsbl.py 117.207.230.178 
dnsbl.sorbs.net
dul.dnsbl.sorbs.net
spam.dnsbl.sorbs.net
zen.spamhaus.org
noptr.spamrats.com
b.barracudacentral.org
web.dnsbl.sorbs.net
pbl.spamhaus.org

# or with hostname
$ bin/adnsbl.py gmail-smtp-in.l.google.com
~~~

you may remove some DNSBL from checklist with `-r`/`--remove`: `-r dnsbl.sorbs.net dul.dnsbl.sorbs.net`, or add new
DNSBL zones same way with `-a`/`--append`.

`adnsbl.py` exit code is 0 if host isn't blacklisted anywhere, and 1 otherwise.

## Usage in your python code
See adnsbl.py sources, it's simple.
~~~python
import asyncio
import async_dnsbl_client

result = asyncio.run(async_dnsbl_client.dnsbl('gmail-smtp-in.l.google.com'))

~~~

## Why not adns?
There is already python3 adns support in [python3-adns](https://github.com/trolldbois/python3-adns) package. But it crashes on ARM machines (such as Raspberri Pi (arch: armv7l) and Oracle Ampere A1 (arch: aarch64)). (maybe you know why?)

~~~python3
>>> import adns
>>> adns.init()
Segmentation fault (core dumped)
~~~

on 'normal' amd64 it works fine, 

async-dnsbl-client works fine on ARM machines (), checking host in 53 blacklists in 0.127s (fastest).

## See also

This project uses [aiodns package](https://github.com/saghul/aiodns) 

[pydnsbl](https://github.com/dmippolitov/pydnsbl) - more mature package, looks more powerful, same fast. (But I need my project because sometimes simpler is better)
