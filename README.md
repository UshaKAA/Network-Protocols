# Network Protocols — Python Implementations

A collection of core networking protocols implemented from scratch in Python, built alongside CCNA exam preparation. Each project simulates real protocol behavior using raw sockets and binary packet construction — no high-level libraries.

## Projects

| Protocol | Description | Port |
|----------|-------------|------|
| [DHCP](./dhcp/) | Dynamic Host Configuration Protocol — IP lease negotiation | UDP 67/68 |
| [DNS](./dns/) | Recursive DNS resolver with caching, round-robin, and PTR records | UDP 53 |
| [SMTP](./smtp/) | Simple Mail Transfer Protocol server — full command state machine | TCP 25 |
| [SNMP](./snmp/) | SNMP Agent + Manager — GET, SET, GETNEXT, Trap, Inform | UDP 161/162 |
| [Telnet](./telnet/) | Telnet client/server with TCP flow control simulation | UDP 25000 |
| [TFTP](./tftp/) | Trivial File Transfer Protocol — reliable file transfer over UDP | UDP 69 |

## Key Concepts Demonstrated

- **Raw socket programming** — `socket`, `struct`, `select`
- **Binary packet construction** — manual byte packing with `struct.pack/unpack`
- **Protocol state machines** — implementing RFC-defined message flows
- **Reliability over UDP** — Stop-and-Wait ARQ, retransmits, timeouts
- **Flow control** — sliding window simulation in Telnet
- **Caching & TTL** — DNS resolver cache with expiry logic
- **Network byte order** — big-endian encoding throughout

## How to Run

Each subdirectory has its own `README.md` with setup and run instructions. All you need is Python 3.8+.

```bash
python3 --version   # Confirm Python 3.8+
cd dhcp/ && python3 DHCP_Server.py
```

## Background

These projects were built as a hands-on complement to CCNA 200-301 exam prep, using GNS3 and Wireshark for real packet capture and validation. The goal was to understand protocols at the byte level, not just conceptually.

---

*Author: Kalib Abdillahi Ahmed — Network Engineer candidate, Djibouti*
