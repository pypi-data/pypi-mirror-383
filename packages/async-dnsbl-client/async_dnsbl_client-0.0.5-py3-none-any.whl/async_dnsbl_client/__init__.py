import aiodns
import asyncio
import socket

from .dnsbl_zones import dnsbl_zones


async def resolve_with_priv(name, query_type='A', priv=None, resolver=None):

    #loop = asyncio.get_event_loop()
    resolver = resolver or aiodns.DNSResolver()

    retval = {
        'query': {
            'name': name,
            'query_type': query_type
        },
        'priv': priv
    }


    try:
        result = await resolver.query(name, query_type)
    except aiodns.error.DNSError as e:
        retval['result'] = None
    else:
        retval['result'] = result
    
    return retval

async def host2ips(host: str) -> list:
    """ convert host to list of IP addresses 
        '1.2.3.4' -> ['1.2.3.4']
        'one.one.one.one' -> ['1.1.1.1', '1.0.0.1']
    """

    try:
        socket.inet_aton(host)
        return [ host ]
    except socket.error:          
        # this is hostname
        ips = list()
        resolver = aiodns.DNSResolver()
        r = await resolver.query(host, 'A')
        ips = [ a.host for a in r ]
        return ips


async def dnsbl(host, zonelist = None, nameserver=None):
    zonelist = zonelist or dnsbl_zones
    nameservers = [nameserver] if nameserver else None
    resolver = aiodns.DNSResolver(nameservers=nameservers)
    ips = await host2ips(host)
    corolist = list()

    for ip in ips:
        revip = '.'.join(ip.split('.')[::-1])
        for zone in zonelist:
            corolist.append(resolve_with_priv(revip+'.'+zone, priv=zone, resolver=resolver))

    R = await asyncio.gather(*corolist)
    return [ x['priv'] for x in R if x['result'] ]
