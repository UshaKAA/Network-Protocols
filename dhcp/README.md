# DHCP — Dynamic Host Configuration Protocol

A from-scratch implementation of DHCP message parsing and a full DHCP client, built directly from **RFC 2131**.

## What It Does

- **`DHCP.py`** — Defines the DHCP message structure with manual `struct.pack/unpack`. Implements all fixed header fields (op, htype, hlen, xid, ciaddr, yiaddr, siaddr, giaddr, chaddr) plus variable-length options parsing.
- **`DHCP_Server.py`** — A working DHCP client that crafts a real `DISCOVER` packet, sends it over UDP broadcast, and fully parses the server's `OFFER` response including options 1 (subnet mask), 3 (router), 51 (lease time), 53 (message type), and 54 (server ID).

## Protocol Flow Implemented

```
Client                        Server
  |                              |
  |-------- DHCP DISCOVER ------>|   (broadcast, xid generated)
  |                              |
  |<-------- DHCP OFFER ---------|   (yiaddr = offered IP)
  |                              |
  | (REQUEST / ACK not shown)    |
```

## Key Concepts

- **Magic Cookie** (`0x63825363`) — marks the start of the DHCP options field
- **Transaction ID (xid)** — random 32-bit value used to match OFFER to DISCOVER
- **Options parsing** — TLV (Type-Length-Value) loop for all option codes
- **Network byte order** — all fields packed as big-endian (`!` prefix in struct format)

## DHCP Message Format (RFC 2131)

```
Offset  Size   Field
0       1      op       (1=BOOTREQUEST, 2=BOOTREPLY)
1       1      htype    (1=Ethernet)
2       1      hlen     (6=MAC length)
3       1      hops
4       4      xid      (Transaction ID)
8       2      secs
10      2      flags    (0x8000 = broadcast)
12      4      ciaddr   (Client IP)
16      4      yiaddr   (Your/offered IP)
20      4      siaddr   (Server IP)
24      4      giaddr   (Gateway IP)
28      16     chaddr   (Client MAC, zero-padded)
44      64     sname    (Server name)
108     128    file     (Boot filename)
236     4      magic cookie
240+    var    options
```

## Run

```bash
# View the message structure and TODOs
python3 DHCP.py

# Run the client (requires a DHCP server on the network, or test with a mock)
python3 DHCP_Server.py
```

## What I Learned

Building this forced me to understand exactly why DHCP uses UDP broadcast (the client has no IP yet), how the magic cookie separates the fixed header from options, and why transaction IDs are necessary when multiple clients discover simultaneously.
