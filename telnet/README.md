# Telnet — TCP Flow Control Simulation

A Telnet client/server pair that simulates **TCP flow control** (sliding window) using custom TCP segment headers over UDP.

## What It Demonstrates

This project is not about Telnet the application — it uses the Telnet client/server model to simulate how **TCP's receive window** prevents a fast sender from overwhelming a slow receiver.

## The Problem Flow Control Solves

```
Fast Sender (Client)          Slow Receiver (Server)
       |                              |
       |--- "Hi" (2 bytes) ---------> | Buffer: 4/4 free → 2/4 free
       |<-- ACK, window=2 ----------- |
       |                              |
       |--- "Yo" (2 bytes) ---------> | Buffer: 2/4 free → 0/4 free
       |<-- ACK, window=0 ----------- |
       |                              |
[Client sees window=0, WAITS]         [Server processes buffer, clears it]
       |                              |
       |--- "Go" (2 bytes) ---------> | Buffer free again
       |<-- ACK, window=4 ----------- |
```

## Custom TCP Segment

Each packet includes a simulated TCP header with:
- `seq` — Sequence number (tracks byte stream position)
- `ack_num` — Acknowledgment number (next expected byte)
- `window` — Receiver's available buffer space
- `flags` — Control flags
- `data` — Payload

## Flow Control Logic

**Server (`TelnetServer.py`)**
- Has a `buffer_capacity = 4` bytes (intentionally small for testing)
- Drops packets that exceed available buffer
- Sends ACK with current `window` size in the header
- Simulates slow application processing with `time.sleep(5)` when buffer fills

**Client (`TelnetClient.py`)**
- Checks `remote_window` before sending — pauses if it's 0
- Uses **Stop-and-Wait ARQ**: sends one segment, waits for ACK before next
- Updates `remote_window` from every ACK received
- Retransmits on timeout

## Run

```bash
# Terminal 1
python3 Telnet_server.py

# Terminal 2
python3 Telnet_client.py
```

**Expected output (client side):**
```
Preparing to send: 2 bytes
Success! ACKed 102
Server Window is now: 2

Preparing to send: 2 bytes
Success! ACKed 104
Server Window is now: 0

Preparing to send: 2 bytes
[Flow Control] Window is 0. Server is busy. Waiting...
```

## Key Concepts

- **Receive Window** — advertised by receiver; shrinks as buffer fills
- **Stop-and-Wait** — simplest form of reliable transfer (one packet in flight)
- **Sequence numbers** — track byte position, detect duplicates/reorders
- **ACK numbers** — confirm receipt, signal next expected byte

## CCNA Relevance

TCP flow control is tested on the CCNA exam. Understanding how the receive window prevents buffer overflow, and why TCP uses sequence/acknowledgment numbers, is fundamental to troubleshooting slow network transfers.
