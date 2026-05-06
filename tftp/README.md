# TFTP — Trivial File Transfer Protocol

A complete TFTP server and client implementing reliable file transfer over UDP with block acknowledgment and retransmission.

## What It Does

TFTP transfers files in 512-byte blocks over UDP. Since UDP has no built-in reliability, the protocol implements its own Stop-and-Wait ARQ: each block must be acknowledged before the next is sent.

## Protocol Flow

```
Client                          Server
  |                               |
  |--- RRQ (filename, mode) ----> |   opcode=1, "challenge.txt\0octet\0"
  |                               |
  |<-- DATA block 1 (512 bytes)-- |   opcode=3, block=1
  |--- ACK block 1 -------------> |   opcode=4, block=1
  |                               |
  |<-- DATA block 2 (512 bytes)-- |
  |--- ACK block 2 -------------> |
  |                               |
  |<-- DATA block N (<512 bytes)- |   Last block signals end of file
  |--- ACK block N -------------> |
```

**End-of-transfer signal:** A DATA block with fewer than 512 bytes means it's the last block.

## Packet Formats

```
RRQ:   [ opcode=1 (2B) ][ filename\0 ][ mode\0 ]
DATA:  [ opcode=3 (2B) ][ block# (2B) ][ payload (0-512B) ]
ACK:   [ opcode=4 (2B) ][ block# (2B) ]
ERROR: [ opcode=5 (2B) ][ error_code (2B) ][ message\0 ]
```

All multi-byte fields use **network byte order** (big-endian), packed with `struct.pack('!H', value)`.

## Reliability (Stop-and-Wait ARQ)

The server retries each block up to 3 times before giving up:

```python
for attempt in range(max_trial):     # 3 attempts
    sock.sendto(packet, client_addr)
    try:
        recv_data, _ = sock.recvfrom(1024)
        if recv_opcode == ACK and recv_block == block_num:
            break   # ACK received, move to next block
    except socket.timeout:
        pass        # Retry
```

## Run

```bash
# Terminal 1 — Start the server (requires sudo for port 69, or change to port > 1024)
sudo python3 TFTP.py
# or modify port to 6900 for testing without sudo

# Terminal 2 — Request a file
python3 TFTP_client.py
```

To test, create a file the server can serve:
```bash
echo "Hello from TFTP!" > challenge.txt
```

## Error Handling

| Error Code | Meaning           |
|------------|-------------------|
| 1          | File not found    |
| 2          | Access violation  |

The server sends an ERROR packet (opcode=5) when the requested file doesn't exist.

## CCNA Relevance

TFTP (UDP/69) is used in real networks to transfer IOS firmware images to Cisco routers and switches, and to back up device configurations. It is specifically tested on the CCNA exam in the context of device management and network operations.
