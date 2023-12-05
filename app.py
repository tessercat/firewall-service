""" The ipset service app module. """
import ipaddress
import logging
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.responses import PlainTextResponse
from starlette.routing import Route
import libipset


logger = logging.getLogger("uvicorn.error")


def is_ipv4(value):
    """ Return True if the value is an IPv4 address. """
    try:
        ipaddress.IPv4Address(value)
    except ValueError:
        return False
    else:
        if any(octet != "0" and octet[0] == "0" for octet in value.split(".")):
            return False
    return True


def is_ipv6(value):
    """ Return True if the value is an IPv6 address. """
    try:
        ipaddress.IPv6Address(value)
    except ValueError:
        return False
    return True


async def add_entry(request):
    """ Validate request params and add the address to the ipset. """
    address = request.query_params.get("address")
    if not address:
        raise HTTPException(400, detail="Missing address param")
    ipset = request.query_params.get("ipset")
    if not ipset:
        raise HTTPException(400, detail="Missing ipset param")
    if is_ipv4(address):
        setname = f"{ipset}.v4"
    elif is_ipv6(address):
        setname = f"{ipset}.v6"
    else:
        raise HTTPException(400, detail="Bad address")
    try:
        libipset.add_entry(setname, address)
    except ValueError as err:
        logger.warning(err.args[0])
        raise HTTPException(400, detail=err.args[0]) from err
    logger.info('Added %s to %s', address, setname)
    return PlainTextResponse("Success")


app = Starlette(routes=[
    Route("/", add_entry, methods=["PUT"]),
])
