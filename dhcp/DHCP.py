import struct
import socket
import random
from enum import Enum
from typing import Dict, List, Optional

class DHCPMessageType(Enum):
    """DHCP Message Types (Option 53)"""
    DISCOVER = 1
    OFFER = 2
    REQUEST = 3
    DECLINE = 4
    ACK = 5
    NAK = 6
    RELEASE = 7
    INFORM = 8

class DHCPOpCode(Enum):
    """DHCP Operation Codes"""
    BOOTREQUEST = 1  # Client to Server
    BOOTREPLY = 2    # Server to Client

class DHCPMessage:
    """
    DHCP Message Format (RFC 2131)
    
    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |     op (1)    |   htype (1)   |   hlen (1)    |   hops (1)    |
    +---------------+---------------+---------------+---------------+
    |                            xid (4)                            |
    +-------------------------------+-------------------------------+
    |           secs (2)            |           flags (2)           |
    +-------------------------------+-------------------------------+
    |                          ciaddr  (4)                          |
    +---------------------------------------------------------------+
    |                          yiaddr  (4)                          |
    +---------------------------------------------------------------+
    |                          siaddr  (4)                          |
    +---------------------------------------------------------------+
    |                          giaddr  (4)                          |
    +---------------------------------------------------------------+
    |                          chaddr  (16)                         |
    +---------------------------------------------------------------+
    |                          sname   (64)                         |
    +---------------------------------------------------------------+
    |                          file    (128)                        |
    +---------------------------------------------------------------+
    |                          options (variable)                   |
    +---------------------------------------------------------------+
    """
    
    MAGIC_COOKIE = b'\x63\x82\x53\x63'  # DHCP Magic Cookie
    
    def __init__(self):
        self.op = DHCPOpCode.BOOTREQUEST
        self.htype = 1  # Ethernet
        self.hlen = 6   # MAC address length
        self.hops = 0
        self.xid = 0    # Transaction ID
        self.secs = 0
        self.flags = 0
        self.ciaddr = '0.0.0.0'  # Client IP
        self.yiaddr = '0.0.0.0'  # Your IP (offered by server)
        self.siaddr = '0.0.0.0'  # Server IP
        self.giaddr = '0.0.0.0'  # Gateway IP
        self.chaddr = b'\x00' * 16  # Client hardware address
        self.sname = b'\x00' * 64   # Server name
        self.file = b'\x00' * 128   # Boot file name
        self.options: Dict[int, bytes] = {}  # DHCP options
    
    def pack(self) -> bytes:
        """
        TODO: Pack the DHCP message into bytes for transmission.
        
        Steps:
        1. Convert op from enum to integer (op.value)
        2. Use struct.pack to pack the fixed fields:
           Format: '!BBBBLHHLLLL' for op, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr
        3. Convert IP addresses to 32-bit integers using socket.inet_aton()
        4. Append chaddr (16 bytes), sname (64 bytes), file (128 bytes)
        5. Append MAGIC_COOKIE
        6. Pack options using _pack_options()
        7. Append option 255 (End option): b'\xff'
        
        Return the complete byte string
        """
        # TODO: Implement this method
        return None
    
    @classmethod
    def unpack(cls, data: bytes) -> 'DHCPMessage':
        """
        TODO: Unpack received bytes into a DHCPMessage object.
        
        Steps:
        1. Create a new DHCPMessage instance
        2. Use struct.unpack to extract fixed fields (first 236 bytes)
        3. Convert IP addresses from integers to strings using socket.inet_ntoa()
        4. Extract chaddr, sname, file
        5. Verify MAGIC_COOKIE is present
        6. Parse options using _parse_options()
        
        Return the DHCPMessage object
        """
        # TODO: Implement this method
        pass
        return None
    
    def _pack_options(self) -> bytes:
        """Pack DHCP options into bytes"""
        option_bytes = b''
        for code, value in self.options.items():
            option_bytes += struct.pack('!BB', code, len(value))
            option_bytes += value
        return option_bytes
    
    def _parse_options(self, data: bytes) -> None:
        """Parse DHCP options from bytes"""
        i = 0
        while i < len(data):
            code = data[i]
            if code == 255:  # End option
                break
            if code == 0:  # Pad option
                i += 1
                continue
            length = data[i + 1]
            value = data[i + 2:i + 2 + length]
            self.options[code] = value
            i += 2 + length
    
    def set_option(self, code: int, value: bytes) -> None:
        """Set a DHCP option"""
        self.options[code] = value
    
    def get_option(self, code: int) -> Optional[bytes]:
        """Get a DHCP option"""
        return self.options.get(code)
    
    def get_message_type(self) -> Optional[DHCPMessageType]:
        """Get DHCP message type from option 53"""
        msg_type = self.get_option(53)
        if msg_type:
            return DHCPMessageType(msg_type[0])
        return None


# Helper function for testing
def mac_to_bytes(mac: str) -> bytes:
    """Convert MAC address string to bytes (e.g., 'aa:bb:cc:dd:ee:ff')"""
    return bytes.fromhex(mac.replace(':', ''))


print("DHCP Message Structure Created!")
print("\nYour TODO:")
print("1. Implement DHCPMessage.pack() method")
print("2. Implement DHCPMessage.unpack() method")
print("\nThink about:")
print("- How to convert between IP strings and 32-bit integers")
print("- The order of bytes (network byte order = big-endian)")
print("- struct format characters: B=unsigned char, H=unsigned short, L=unsigned long")