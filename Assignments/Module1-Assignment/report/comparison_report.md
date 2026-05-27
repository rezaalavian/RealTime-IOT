# Module 1 Assignment — Protocol Comparison Report

**Student Name:** ___________________________
**Student ID:**   ___________________________
**Date:**         ___________________________

---

## 5.1 QoS Comparison Results Table

> Run `pytest tests/mqtt/test_qos_loss.py -v -s` and paste the output table here.

| Protocol / QoS | Sent | Received | Lost (%) | Duplicates | Avg Latency (ms) |
|----------------|------|----------|----------|------------|-----------------|
| MQTT QoS 0 | 100 | 100 | 0.0% | 0 | 0.0 |
| MQTT QoS 1 | 100 | 100 | 0.0% | 0 | 0.1 |
| MQTT QoS 2 | 100 | 100 | 0.0% | 0 | 0.3 |
| CoAP NON | — | — | — | — | — |
| CoAP CON | — | — | — | — | — |
| AMQP (confirms off) | — | — | — | — | — |

**Analysis Questions:**

1. **Why does QoS 0 lose messages while QoS 1 and 2 do not?** *(2–3 sentences)*

   QoS 0 is fire-and-forget, so the broker gives no delivery guarantee and dropped packets are never retried. QoS 1 adds PUBACK-based retry, and QoS 2 adds a two-phase handshake, so both survive transient loss better.

2. **QoS 1 may show duplicates. Under what circumstances does this happen, and is it a problem for sensor telemetry?** *(2–3 sentences)*

   Duplicates happen when a PUBLISH or PUBACK is lost and the sender retransmits before it sees the acknowledgment. For telemetry, duplicates are usually tolerable because downstream consumers can de-duplicate by sequence number or timestamp.

3. **QoS 2 has higher latency than QoS 1. What causes this, and when is the trade-off worth it?** *(2–3 sentences)*

   QoS 2 adds an extra handshake to guarantee exactly-once delivery, so each message needs more round trips and state tracking. The trade-off is worth it for command, control, or billing data where duplicates are unacceptable.

---

## 5.2 CoAP–HTTP Proxy Mapping

> Run `pytest tests/coap/test_proxy.py -v -s` and record the observed HTTP headers.

| HTTP Header | CoAP Option | Your Observed Value |
|-------------|-------------|---------------------|
| Content-Type | — | Not available in this workspace |
| Cache-Control: max-age | — | Not available in this workspace |
| ETag | — | Not available in this workspace |
| Location | — | Not available in this workspace |

The proxy test file is not present in this workspace, so no verified header mapping could be recorded here.

---

## 5.3 Protocol Selection Recommendation

The best protocol depends on whether the path is telemetry, control, or bulk transfer.

### Data Path Recommendations

| Data Path | Recommended Protocol | Justification |
|-----------|---------------------|---------------|
| Sensor → Cloud (high frequency, <100 ms latency) | MQTT QoS 0/1 | Lowest overhead, small topic frames, and easy fan-out for many consumers. |
| Actuator commands (safety-critical, exactly-once) | MQTT QoS 2 or CoAP CON | QoS 2 prevents duplicates; CoAP CON gives reliable delivery on constrained links. |
| Backend service-to-service routing | AMQP | Better routing semantics and queueing for services than pure telemetry protocols. |
| OTA firmware delivery to constrained MCU (Class 2) | CoAP Block2 | Fits constrained devices and supports block-wise transfer for large payloads. |

### Detailed Justification

MQTT is the strongest fit for sensor telemetry because the packets are compact and the topic model maps cleanly to factory lines and sensor types. In the live capture, the publisher sent repeated JSON readings on `factory/line1/temperature` and `factory/line2/temperature`, which is exactly the kind of high-frequency stream that benefits from a lightweight broker.

For commands that must not be duplicated, QoS 2 is the safest MQTT choice because it adds the extra acknowledgment handshake needed for exactly-once delivery. CoAP CON is also appropriate when the receiver is constrained, because it keeps the protocol small while still acknowledging each message. In this project, the CoAP observer/server pair was more complex to coordinate on Windows than MQTT, which is a practical sign that MQTT is easier to operate for everyday telemetry.

AMQP is better suited to backend routing than device telemetry because it is designed around exchanges, queues, and delivery semantics rather than simple topic fan-out. That makes it a stronger fit for service-to-service pipelines where messages need to be buffered, routed, and consumed by multiple workers.

For OTA firmware, CoAP Block2 is the clearest recommendation. The server-side manifest resource already demonstrates a large JSON response, and CoAP’s block-wise transfer model is a natural match for constrained MCUs that cannot comfortably handle large TCP-centric payloads. In short: MQTT for fast telemetry, CoAP for constrained device interactions, AMQP for backend orchestration, and CoAP Block2 for firmware distribution.

---

## 5.4 Reflection

The hardest part was getting the Windows capture pipeline to work consistently. The main issue was not the code itself but the environment: PowerShell, Bash, loopback capture, and the CoAP server all had to agree on the same interface and port. Once I switched to the Windows Wireshark `dumpcap.exe` and the loopback adapter, the captures became reliable.

### Technical Challenge

The biggest technical challenge was the Windows asyncio and capture setup for CoAP. I resolved it by using the selector event loop policy, binding the server to `::1`, and stopping stray server processes that were holding port `5683`.

### Most Surprising Protocol Difference

The most surprising difference was how much more visible the MQTT application data was in the capture compared with CoAP. MQTT’s topic and JSON payload were easy to read immediately, while CoAP’s observe flow required careful packet pairing and block-wise thinking.

### Most Complex Protocol to Implement

CoAP was the most complex to implement correctly because it combined asyncio, observe notifications, and Windows networking quirks. MQTT was simpler because the broker handled most of the delivery behavior, while CoAP required the server, observer, and capture workflow to line up precisely.

---

*Module 1 Assignment — Real-Time Data Analytics for IoT*
