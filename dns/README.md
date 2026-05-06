# DNS — Recursive Resolver with Caching

A simulated recursive DNS resolver implementing real-world DNS behaviors: TTL-based caching, CNAME chaining, round-robin load balancing, and reverse PTR lookups.

## What It Does

Simulates the full DNS resolution chain — authoritative zone file, ISP-level recursive resolver, and client query — all in pure Python with no external libraries.

## Architecture

```
Client Query
     |
     v
RecursiveResolver  <-- cache (TTL-aware)
     |
     | cache miss
     v
DNSZone (Authoritative Server)
     |
     +-- A records (with round-robin)
     +-- CNAME records (triggers recursion)
     +-- PTR records (reverse DNS)
```

## Features

### Caching with TTL
Every record has a TTL. The resolver caches results and checks expiry on each lookup — expired records are evicted and re-fetched from the authoritative server.

### CNAME Resolution (Recursive)
```
www.google.com  CNAME  google.com
google.com      A      8.8.8.8
```
Querying `www.google.com` automatically follows the CNAME and returns the A record. This is the same behavior as real resolvers like `8.8.8.8`.

### Round-Robin Load Balancing
Multiple A records for the same domain are rotated on each query:
```
google.com  A  8.8.8.8
google.com  A  8.8.4.4
google.com  A  142.250.190.46
```
Each query returns a different IP, distributing load across servers.

### Reverse DNS (PTR Records)
IP → hostname lookups using the `in-addr.arpa` format:
```
8.8.8.8  →  8.8.8.8.in-addr.arpa  →  dns.google
```

## Run

```bash
python3 DNSrecursive.py
```

**Expected output:**
```
--- Testing Load Balancing with Multiple Queries ---
Query 1: 8.8.8.8
Query 2: 8.8.4.4
Query 3: 142.250.190.46
...

--- Testing Reverse DNS (IP -> Hostname) ---
8.8.8.8  ->  dns.google
```

## DNS Record Types Implemented

| Type  | Direction         | Example                        |
|-------|-------------------|--------------------------------|
| A     | name → IPv4       | google.com → 8.8.8.8          |
| AAAA  | name → IPv6       | google.com → 2001:4860::      |
| CNAME | alias → canonical | www.google.com → google.com   |
| MX    | domain → mail srv | gmail.com → smtp.google.com   |
| PTR   | IPv4 → name       | 8.8.8.8 → dns.google         |

## CCNA Relevance

DNS resolution is a core topic on the CCNA exam. Understanding the difference between recursive and iterative queries, how TTL controls caching, and how PTR records work for reverse lookups all appear in exam scenarios and real network troubleshooting.
