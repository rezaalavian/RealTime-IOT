# Module 1 Assignment — Packet Analysis
## Task 4: Wire-Level Protocol Annotation

---

## 4.2 MQTT Packet Annotations

The live capture shows MQTT publishes on the loopback broker connection. The publisher uses client ID `smartfactory-publisher-001`, a persistent session, and per-sensor QoS values from `src/mqtt/publisher.py`.

### CONNECT Packet

| Field | Offset (bytes) | Raw Hex | Decoded Value |
|-------|---------------|---------|---------------|
| Frame type + flags (byte 1) | 0 | `10` | Type=CONNECT (0001), flags=0000 |
| Remaining length | 1 | `45` | 69 bytes |
| Protocol name | 4–7 | `4D 51 54 54` | `MQTT` |
| Protocol version | 8 | `04` | MQTT 3.1.1 |
| Connect flags | 9 | `2C` | Will flag + Will QoS 1 + Will retain |
| Keep-alive | 10–11 | `00 3C` | 60 seconds |
| Client ID | 14–… | `smartfactory-publisher-001` | Persistent publisher identity |

**Connect flags:** LWT is enabled, retained, and published at QoS 1; the session is persistent (`clean_session=False`).

### QoS 1 PUBLISH Packet

| Field | Offset (bytes) | Raw Hex | Decoded Value |
|-------|---------------|---------|---------------|
| Fixed header byte 1 | 0 | `32` | PUBLISH, QoS 1 |
| Topic | 4–… | `factory/line1/temperature` | Temperature topic |
| Packet Identifier | after topic | `21 61` / `21 6?` | Variable per publish |
| Payload | rest | JSON | `{"line": "line1", "sensor": "temperature", "value": 73.348, ...}` |

The capture also shows the alternating `factory/line2/temperature` publishes and their JSON payloads. The payload contains `line`, `sensor`, `value`, `unit`, `timestamp`, and `seq` fields.

### PUBACK Packet

| Field | Offset | Raw Hex | Decoded Value |
|-------|--------|---------|---------------|
| Fixed header | 0 | `40` | PUBACK |
| Remaining length | 1 | `02` | 2 bytes |
| Packet Identifier | 2–3 | matches PUBLISH | Ack for the QoS 1 publish |

---

## 4.3 CoAP Packet Annotations

The live CoAP trace shows confirmable observe notifications and their acknowledgements on `::1:5683`.

### CON Observe Notification

| Field | Value |
|-------|-------|
| Message type | CON |
| Code | 2.05 Content (69) |
| Message ID | e.g. `13462`, `13463`, ... |
| Observe sequence | `3`, `4`, `5`, `6` |
| Payload | JSON sensor reading |

The trace shows paired ACKs with the same message IDs, which confirms the server is using confirmable notifications for observe delivery.

### ACK Response

| Field | Value |
|-------|-------|
| Message type | ACK |
| Code | 0.00 Empty |
| Message ID | Matches the preceding CON |

### Manifest Fetch

| Field | Value |
|-------|-------|
| URI | `/factory/manifest` |
| Response code | 2.05 Content |
| Payload | Large JSON manifest |
| Transfer mode | Block2-capable |

---

## 4.4 AMQP Frame Annotations

AMQP source files are not implemented in this workspace, so there is no faithful live frame capture to annotate here. The frame layout below is kept as the protocol reference for the assignment.

### basic.publish Method Frame

| Field | Bytes | Raw Hex | Decoded Value |
|-------|-------|---------|---------------|
| Frame Type | 0 | `01` | Method frame |
| Channel | 1–2 | varies | Delivery channel |
| Class ID | 7–8 | `00 3C` | `basic` |
| Method ID | 9–10 | `00 28` | `basic.publish` |
| Frame End | last | `CE` | Frame terminator |

### Content Header Frame

| Field | Bytes | Raw Hex | Decoded Value |
|-------|-------|---------|---------------|
| Frame Type | 0 | `02` | Header frame |
| Class ID | 7–8 | `00 3C` | `basic` |
| Body Size | 11–18 | varies | Message body length |
| delivery_mode | property | varies | Transient or persistent |

### Heartbeat Frame

| Field | Value |
|-------|-------|
| Frame Type | 8 |
| Channel | 0 |
| Payload | empty |

*Module 1 Assignment — Real-Time Data Analytics for IoT*
