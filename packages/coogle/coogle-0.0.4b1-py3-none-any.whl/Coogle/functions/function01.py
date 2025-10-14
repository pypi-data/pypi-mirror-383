import re
from .functions import Tuples
from urllib.parse import urlparse
from urllib.parse import parse_qs
from ..exceptions import InvalidToken
#======================================================================

async def checktok(token):
    if len(token) == 73 and token[1] == "/":
        pass
    else:
        raise InvalidToken("Invalid Token")

#======================================================================

async def gouid(link: str, pattern=None):
    if link.startswith(Tuples.DATA01):
        moones = re.search(pattern, link)
        moonus = moones.group(3) if moones else None
        return moonus
    else:
        moones = urlparse(link)
        moonus = parse_qs(moones.query)['id'][0]
        return moonus

#======================================================================
