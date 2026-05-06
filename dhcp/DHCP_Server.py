import random
import socket
import struct


class DHCPMessageType:
    """DHCP Message Type - (Option 53 field)"""
    DISCOVER = 1
    OFFER = 2
    REQUEST = 3
    DECLINE = 4
    ACK = 5
    NAK = 6
    RELEASED = 7
    INFORM = 8

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


class DHCPClient:
    """
    DHCP Client - Request IP from DHCP server
    """

    def __init__(self, mac_addr: str):
        """
        Args:
            mac_addr (str): e.g "aa:bb:cc:dd:ee:ff"
        """
        self.mac_addr = mac_addr
        self.transaction_id = None
        self.mac_bytes = self._mac_to_bytes()
        self.offered_ip = None
        self.server_ip = None

    def _mac_to_bytes(self) -> bytes:
        return bytes.fromhex(self.mac_addr.replace(":", ''))

    def create_discover(self) -> bytes:
        """Create DHCP DISCOVER message"""
        # Header Fields
        op = 1  # BOOTREQUEST
        htype = 1  # Ethernet
        hlen = 6  # MAC length
        hops = 0  # Increment by each relay
        xid = random.randint(0, 0xFFFFFFFF)
        self.transaction_id = xid  # Store for matching OFFER
        secs = 0
        flags = 0x8000  # Broadcast flag

        # IP Address Fields (all 0.0.0.0 for Discovery)
        empty_ip = socket.inet_aton("0.0.0.0")
        ciaddr = empty_ip
        yiaddr = empty_ip
        siaddr = empty_ip
        giaddr = empty_ip

        # chaddr - MAC padded to 16 bytes
        chaddr = struct.pack('6s10x', self.mac_bytes)

        # Empty Fields
        sname = b'\x00' * 64
        file = b'\x00' * 128

        # Pack the fixed portion
        str_format = '!BBBBLHH4s4s4s4s16s64s128s'
        header = struct.pack(str_format,
                             op, htype, hlen, hops,
                             xid, secs, flags,
                             ciaddr, yiaddr, siaddr, giaddr,
                             chaddr, sname, file)

        # Magic cookie
        magic_cookie = b'\x63\x82\x53\x63'

        # Options
        opt53 = struct.pack('!BBB', 53, 1, DHCPMessageType.DISCOVER)
        end_opt = b'\xff'

        return header + magic_cookie + opt53 + end_opt

    
    def parse_offer(self, data: bytes) -> dict:
        
        # 1. Verify the message is long enough (minimum 240 bytes)
        if len(data) < 240:
            raise ValueError('Message too short')

        # 2. Unpack the fixed header (236 bytes) using struct.unpack
        header_size = struct.calcsize('!BBBBLHH4s4s4s4s16s64s128s')
        header_bytes = data[:header_size]    # 236 bytes header

        # 3. Extract and validate:
        recv_header = struct.unpack('!BBBBLHH4s4s4s4s16s64s128s', header_bytes)

        op = recv_header[0]
        xid = recv_header[4]
        yiaddr = recv_header[8]
        siaddr = recv_header[9]
        chaddr = recv_header[10]

        if op != DHCPMessageType.OFFER:
            raise ValueError("Incorrect DHCP operation code")
        elif xid != self.transaction_id:
            raise ValueError("Transaction ID mismatch")

        yiaddr = socket.inet_ntoa(yiaddr)

        siaddr = socket.inet_ntoa(siaddr)

        chaddr = chaddr[:6]
        
        # 4. Check for magic cookie at byte 236:
        if data[header_size:240] != b'\x63\x82\x53\x63':
            raise ValueError("Invalid DHCP magic cookie.")

        # 5: Parse options starting at byte 240
        options = dict()
        options_offset = header_size + 4 # Start after header and magic cookie

        while options_offset < len(data): # Loop through the entire data, starting from options
            # First, check if there's at least 1 byte for the code
            if options_offset >= len(data):
                raise ValueError("Malformed DHCP options: missing option code.")
            
            code = data[options_offset]

            # Handle special codes
            if code == 255: # End option
                break
            elif code == 0: # Pad option
                options_offset += 1
                continue

            # Now, check if there are at least 2 bytes (code + length)
            if options_offset + 1 >= len(data):
                raise ValueError("Malformed DHCP options: missing option length.")
            length = data[options_offset + 1]

            # Next, check if there are enough bytes for the value
            if options_offset + 2 + length > len(data):
                raise ValueError("Malformed DHCP options: option value extends beyond packet end.")
            
            value = data[options_offset + 2 : options_offset + 2 + length]
            options[code] = value   # Store the raw bytes
            # Update offset to move to the next option
            options_offset += 1 + 1 + length # code (1 byte) + length (1 byte) + value (length bytes)
            
            # ... (your existing code up to options_offset update) ...

        # 6: Extract important options and convert their values
        parsed_info = {
            'offered_ip': yiaddr, # yiaddr is already extracted and converted
            'server_ip': None, # Will be set by Option 54
            'subnet_mask': None, # Will be set by Option 1
            'router': None, # Will be set by Option 3
            'lease_time': None, # Will be set by Option 51
            'message_type': None # Will be set by Option 53
        }

        # Validate Option 53: Message Type
        if 53 not in options:
            raise ValueError("DHCP Message Type option (53) missing.")
        
        # Option 53 value should be a single byte indicating the message type
        message_type_bytes = options[53]
        if len(message_type_bytes) != 1:
            raise ValueError(f"Malformed Option 53: expected 1 byte, got {len(message_type_bytes)}.")
        
        message_type_code = message_type_bytes[0] # Get the integer value of the byte

        if message_type_code != DHCPMessageType.OFFER:
            raise ValueError(f"Invalid DHCP Message Type: expected OFFER ({DHCPMessageType.OFFER}), got {message_type_code}.")
        parsed_info['message_type'] = DHCPMessageType.OFFER

        # Extract and convert other options
        if 54 in options: # Server Identifier
            parsed_info['server_ip'] = socket.inet_ntoa(options[54])

        if 1 in options: # Subnet Mask
            parsed_info['subnet_mask'] = socket.inet_ntoa(options[1])
        
        if 3 in options: # Router (Gateway)
            parsed_info['router'] = socket.inet_ntoa(options[3])

        if 51 in options: # Lease Time
            lease_time_bytes = options[51]
            if len(lease_time_bytes) != 4:
                raise ValueError(f"Malformed Option 51 (Lease Time): expected 4 bytes, got {len(lease_time_bytes)}.")
            parsed_info['lease_time'] = struct.unpack('!L', lease_time_bytes)[0]
        
        return parsed_info

op = 0x3d
len= 0x3d 
hw= 0x1
print(f'option:{int(op)}, Len: {int(len)}, HW: {int(hw)}')
