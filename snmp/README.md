# SNMP — Simple Network Management Protocol

A full SNMP simulation with Agent (network device) and Manager (NMS), implementing GET, SET, GETNEXT, Trap, and Inform over UDP.

## Architecture

```
┌─────────────────────┐         UDP          ┌──────────────────────┐
│    SNMP Manager     │ ──── GET/SET/──────> │     SNMP Agent       │
│  (NMS / Monitoring) │ <─── Response ─────  │  (Router / Switch)   │
│                     │                      │                      │
│  listen_trap()      │ <─── TRAP ─────────  │  send_trap()         │
│                     │ <─── INFORM ───────  │  send_inform()       │
│                     │ ──── ACK ──────────> │  (waits for ACK)     │
└─────────────────────┘                      └──────────────────────┘
```

## Components

### SNMPAgent (the network device)
- Maintains a **MIB** (Management Information Base) — a dictionary of OIDs to values
- Listens on UDP for incoming management requests
- Handles community string authentication (read `public`, write `private`)

### SNMPManager (the NMS)
- Sends queries to agents
- Listens for unsolicited Traps and Informs

## Operations Implemented

| Operation  | Direction       | Reliable? | Description                          |
|------------|-----------------|-----------|--------------------------------------|
| GET        | Manager → Agent | No (UDP)  | Read a single OID value              |
| SET        | Manager → Agent | No (UDP)  | Write a value to an OID              |
| GETNEXT    | Manager → Agent | No (UDP)  | Walk the MIB table sequentially      |
| TRAP       | Agent → Manager | No        | Fire-and-forget alert                |
| INFORM     | Agent → Manager | Yes       | Alert with ACK — retransmit on miss  |

## MIB (Management Information Base)

```python
self.mib = {
    '1.3.6.1.2.1.1.1': 'PyRouter System Description',
    '1.3.6.1.2.1.1.5': 'Router_Hostname'
}
```

OIDs follow the real SNMP OID tree structure (`.iso.org.dod.internet.mgmt.mib-2.system...`).

## Run

```bash
python3 SNMP_Agent.py
```

Choose your role at the prompt:
- `a` → Run as Agent (then choose `s`=service, `t`=trap, `i`=inform)
- `m` → Run as Manager (sends a GET request)
- `t` → Run as Trap Listener

**Example — Two terminals:**
```bash
# Terminal 1
python3 SNMP_Agent.py
> Run as (A)gent, (M)anager, or (T)rapListener? a
> Start (S)ervice or Send (T)rap or Send (I)nform? s

# Terminal 2
python3 SNMP_Agent.py
> Run as (A)gent, (M)anager, or (T)rapListener? m
```

## Key Concepts

- **Community strings** — SNMP's authentication mechanism (`public`=read, `private`=write)
- **OID (Object Identifier)** — hierarchical dot-notation address for every manageable value
- **Trap vs Inform** — Trap is fire-and-forget; Inform waits for ACK (more reliable)
- **UDP** — SNMP uses UDP 161 (agent) and UDP 162 (trap receiver)

## CCNA Relevance

SNMP is a core network management protocol on the CCNA exam. Questions cover SNMPv2c vs SNMPv3, community strings, trap vs inform, and the role of the MIB in network monitoring.
