from collections import namedtuple

from construct import Struct, Container, Embed, Enum, MetaField
from construct import MetaArray, If, Switch, Const, Peek
from construct import OptionalGreedyRange, RepeatUntil
from construct import Flag, PascalString, Adapter
from construct import UBInt8, UBInt16, UBInt32, UBInt64
from construct import SBInt8, SBInt16, SBInt32, SBInt64
from construct import BFloat32, BFloat64
from construct import BitStruct, BitField
from construct import StringAdapter, LengthValueAdapter, Sequence


DUMP_ALL_PACKETS = 1

# Strings.
# This one is a UCS2 string, which effectively decodes single writeChar()
# invocations. We need to import the encoding for it first, though.
from lib2d.common.encodings import ucs2
from codecs import register
register(ucs2)


class DoubleAdapter(LengthValueAdapter):

    def _encode(self, obj, context):
        return len(obj) / 2, obj


def AlphaString(name):
    return StringAdapter(
        DoubleAdapter(
            Sequence(name,
                UBInt16("length"),
                MetaField("data", lambda ctx: ctx["length"] * 2),
            )
        ),
        encoding="ucs2",
    )




dimensions = {
    "earth": 0,
    "sky": 1,
}
dimension = Enum(UBInt8("dimension"), **dimensions)

grounded = Struct("grounded", UBInt8("grounded"))
position = Struct("position",
    BFloat64("x"),
    BFloat64("y"),
    BFloat64("stance"),
    BFloat64("z")
)
orientation = Struct("orientation", BFloat32("rotation"), BFloat32("pitch"))


faces = {
    "noop": -1,
    "-y": 0,
    "+y": 1,
    "-z": 2,
    "+z": 3,
    "-x": 4,
    "+x": 5,
}
face = Enum(SBInt8("face"), **faces)

packets = {
    0: Struct("ping",
        UBInt32("pid"),
    ),
    1: Struct("login",
        UBInt32("protocol"),
        AlphaString("username"),
        AlphaString("password"),
    ),
    2: Struct("handshake",
        AlphaString("username"),
    ),
    3: Struct("chat",
        AlphaString("message"),
    ),
    4: Struct("time",
        UBInt64("timestamp")),
    5: Struct("position", position, grounded),
    6: Struct("orientation", orientation, grounded),
    7: Struct("location", position, orientation, grounded),
    8: Struct("animate",
        UBInt32("eid"),
        Enum(UBInt8("animation"),
            noop=0,
            arm=1,
            hit=2,
            leave_bed=3,
            start_sprint=4,
            stop_sprint=5,
            unknown=102,
            crouch=104,
            uncrouch=105,
        ),
    ),
    9: Struct("use",
        UBInt32("eid"),
        UBInt32("target"),
        UBInt8("button"),
    ),
    10: Struct("health",
        UBInt16("hp"),
    ),
    11: Struct("spawn",
        SBInt32("x"),
        SBInt32("y"),
        SBInt32("z"),
    ),
    12: Struct("entity",
        UBInt32("eid"),
        Enum(UBInt8("type"), **{
            "Creeper": 50,
            "Skeleton": 51,
            "Spider": 52,
            "GiantZombie": 53,
            "Zombie": 54,
            "Slime": 55,
            "Ghast": 56,
            "ZombiePig": 57,
            "Enderman": 58,
            "Pig": 90,
            "Sheep": 91,
            "Cow": 92,
            "Chicken": 93,
            "Squid": 94,
            "Wolf": 95,
        }),
        SBInt32("x"),
        SBInt32("y"),
        SBInt32("z"),
        SBInt8("yaw"),
        SBInt8("pitch"),
    ),

}

packet_stream = Struct("packet_stream",
    OptionalGreedyRange(
        Struct("full_packet",
            UBInt8("header"),
            Switch("payload", lambda context: context["header"], packets),
        ),
    ),
    OptionalGreedyRange(
        UBInt8("leftovers"),
    ),
)

packets_by_name = dict((v.name, k) for (k, v) in packets.iteritems())


def parse_packets(bytestream):
    """
    Opportunistically parse out as many packets as possible from a raw
    bytestream.

    Returns a tuple containing a list of unpacked packet containers, and any
    leftover unparseable bytes.
    """

    container = packet_stream.parse(bytestream)

    l = [(i.header, i.payload) for i in container.full_packet]
    leftovers = "".join(chr(i) for i in container.leftovers)

    if DUMP_ALL_PACKETS:
        for packet in l:
            print "Parsed packet %d" % packet[0]
            print packet[1]

    return l, leftovers

incremental_packet_stream = Struct("incremental_packet_stream",
    Struct("full_packet",
        UBInt8("header"),
        Switch("payload", lambda context: context["header"], packets),
    ),
    OptionalGreedyRange(
        UBInt8("leftovers"),
    ),
)


def parse_packets_incrementally(bytestream):
    """
    Parse out packets one-by-one, yielding a tuple of packet header and packet
    payload.

    This function returns a generator.

    This function will yield all valid packets in the bytestream up to the
    first invalid packet.

    :returns: a generator yielding tuples of headers and payloads
    """

    while bytestream:
        parsed = incremental_packet_stream.parse(bytestream)
        header = parsed.full_packet.header
        payload = parsed.full_packet.payload
        bytestream = "".join(chr(i) for i in parsed.leftovers)

        yield header, payload


def make_packet(packet, *args, **kwargs):
    """
    Constructs a packet bytestream from a packet header and payload.

    The payload should be passed as keyword arguments. Additional containers
    or dictionaries to be added to the payload may be passed positionally, as
    well.
    """

    if packet not in packets_by_name:
        print "Couldn't find packet name %s!" % packet
        return ""

    header = packets_by_name[packet]

    for arg in args:
        kwargs.update(dict(arg))
    container = Container(**kwargs)

    if DUMP_ALL_PACKETS:
        print "Making packet %s (%d)" % (packet, header)
        print container
    payload = packets[header].build(container)
    return chr(header) + payload


def make_error_packet(message):
    """
    Convenience method to generate an error packet bytestream.
    """

    return make_packet("error", message=message)
