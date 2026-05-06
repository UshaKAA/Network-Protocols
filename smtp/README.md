# SMTP — Simple Mail Transfer Protocol Server

A working SMTP server implementing the full RFC 5321 command state machine over TCP.

## What It Does

Listens on TCP port 25 and handles real SMTP sessions end-to-end — from the initial greeting through `HELO`, `MAIL FROM`, `RCPT TO`, `DATA`, and `QUIT`.

## SMTP Session Flow

```
Server                          Client
  |                               |
  |<---- TCP Connection --------->|
  |                               |
  |--- 220 Welcome to SMTP ------>|
  |                               |
  |<------ HELO client.com -------|
  |--- 250 Hello client.com ----->|
  |                               |
  |<------ MAIL FROM:<a@b.com> ---|
  |--- 250 OK, sender is ... ---->|
  |                               |
  |<------ RCPT TO:<x@y.com> -----|
  |--- 250 OK, recipient is ... ->|
  |                               |
  |<------ DATA ------------------|
  |--- 354 End with <CRLF>.<CRLF>->|
  |<------ [email body] ----------|
  |<------ . ---------------------|
  |--- 250 OK, message queued --->|
  |                               |
  |<------ QUIT ------------------|
  |--- 221 Goodbye -------------->|
```

## Commands Implemented

| Command     | Response Code | Description               |
|-------------|---------------|---------------------------|
| `HELO`      | 250           | Identify client domain    |
| `MAIL FROM` | 250           | Set sender address        |
| `RCPT TO`   | 250           | Set recipient address     |
| `DATA`      | 354 → 250     | Send email body           |
| `QUIT`      | 221           | End session               |
| (unknown)   | 502           | Command not implemented   |

## Run

```bash
# Terminal 1 — Start the server
python3 SMTPServer.py

# Terminal 2 — Connect manually with telnet or netcat
telnet 127.0.0.1 25
# or
nc 127.0.0.1 25
```

**Manual session example:**
```
220 Welcome to SMTP Server
HELO mail.example.com
250 Hello mail.example.com, pleased to meet you
MAIL FROM:<sender@example.com>
250 OK, sender is <sender@example.com>
RCPT TO:<recipient@example.com>
250 OK, recipient is <recipient@example.com>
DATA
354 End data with <CRLF>.<CRLF>
Subject: Test Email
Hello, this is a test.
.
250 OK, message queued for delivery
QUIT
221 Goodbye
```

## Key Concepts

- **TCP persistent connection** — one socket handles the full multi-command session
- **State machine** — commands must come in the correct order (real servers enforce this strictly)
- **CRLF line endings** — SMTP requires `\r\n`, not just `\n`
- **DATA termination** — the `.` on a line by itself signals end of message body

## CCNA Relevance

SMTP uses TCP port 25 (or 587 for submission). Understanding application-layer protocols and their port numbers, plus how TCP provides reliable delivery for email, is part of the CCNA curriculum.
