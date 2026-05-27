#!/usr/bin/env bash
# capture.sh — capture MQTT, CoAP, and AMQP traffic for Task 4
# Requires: dumpcap/tshark (installed with Wireshark)

set -e

DURATION=30
IFACE="${IFACE:-}"   # set IFACE explicitly to override auto-detection
OUTDIR="captures"

if [ -x "/mnt/c/Program Files/Wireshark/dumpcap.exe" ]; then
	DUMPCAP="/mnt/c/Program Files/Wireshark/dumpcap.exe"
else
	DUMPCAP=$(command -v dumpcap)
fi

if [ -z "$DUMPCAP" ]; then
	echo "ERROR: dumpcap not found. Install Wireshark first."
	exit 1
fi

if [ -z "$IFACE" ]; then
	IFACE=$(dumpcap -D 2>/dev/null | awk 'BEGIN{IGNORECASE=1} /loopback|adapter for loopback traffic capture/ {print $1; exit}')
fi

if [ -z "$IFACE" ]; then
	echo "ERROR: could not auto-detect a loopback interface."
	echo "Run 'dumpcap -D' and set IFACE to the loopback interface number, e.g.:"
	echo "  IFACE=8 bash scripts/capture.sh"
	exit 1
fi

mkdir -p "$OUTDIR"

echo "Starting $DURATION-second packet capture on interface $IFACE..."
echo "Make sure your publisher/server/producer is running in another terminal."
echo ""

# Capture all three protocols simultaneously in the background
echo "[1/3] Capturing MQTT (port 1883)..."
"$DUMPCAP" -i "$IFACE" -f "port 1883" -w "$OUTDIR/mqtt.pcap" -a duration:"$DURATION" &
PID_MQTT=$!

echo "[2/3] Capturing CoAP (port 5683 UDP)..."
"$DUMPCAP" -i "$IFACE" -f "udp port 5683" -w "$OUTDIR/coap.pcap" -a duration:"$DURATION" &
PID_COAP=$!

echo "[3/3] Capturing AMQP (port 5672)..."
"$DUMPCAP" -i "$IFACE" -f "port 5672" -w "$OUTDIR/amqp.pcap" -a duration:"$DURATION" &
PID_AMQP=$!

echo ""
echo "Capturing for $DURATION seconds... (Ctrl-C to stop early)"
wait $PID_MQTT $PID_COAP $PID_AMQP

echo ""
echo "Captures saved:"
ls -lh "$OUTDIR/"*.pcap 2>/dev/null || echo "  (no pcap files found — is tshark installed?)"

echo ""
echo "Quick check (first 5 MQTT packets):"
tshark -r "$OUTDIR/mqtt.pcap" -Y mqtt 2>/dev/null | head -5 || true
