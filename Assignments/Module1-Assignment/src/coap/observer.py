"""
Module 1 Assignment — Task 2.2
CoAP Observer Client

Complete all TODO sections.

Run with:  python -m src.coap.observer
"""

import asyncio
import json
import logging
from datetime import datetime, timezone

import aiocoap
from aiocoap import Message, Code

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
log = logging.getLogger(__name__)

SERVER_BASE = "coap://localhost"
OBSERVE_DURATION = 60   # seconds before clean deregister


class FactoryObserver:
    """Observes CoAP sensor resources and reassembles Block2 transfers."""

    def __init__(self):
        self._ctx = None
        self._last_seq: dict[str, int] = {}     # uri -> last observe sequence number
        self._stale_count: dict[str, int] = {}  # uri -> stale notification count

    # ── Setup ──────────────────────────────────────────────────────────────────

    async def start(self) -> None:
        """Create the aiocoap client context."""
        self._ctx = await aiocoap.Context.create_client_context()

    async def stop(self) -> None:
        """Clean up the context."""
        if self._ctx:
            await self._ctx.shutdown()

    # ── Observation ────────────────────────────────────────────────────────────

    async def observe_resource(self, uri: str) -> None:
        """
        TODO 1: Subscribe to a single observable CoAP resource.
        Requirements:
          - Build a GET request with observe=0 (register)
          - Use self._ctx.request(request_obj) to get a RequestObservation
          - Iterate over the observation using `async for response in pr.observation:`
          - For each notification, call _handle_notification(uri, response)
          - After OBSERVE_DURATION seconds, cancel the observation (pr.observation.cancel())
          - Log "Deregistered from {uri}" after cancellation
        Hint: wrap the observation loop in asyncio.wait_for or use asyncio.create_task
              to run both line1 and line2 observations concurrently.
        """
        request = Message(code=Code.GET, uri=uri)
        request.opt.observe = 0
        protocol_request = self._ctx.request(request)
        await protocol_request.response

        async def consume() -> None:
            async for response in protocol_request.observation:
                self._handle_notification(uri, response)

        consumer_task = asyncio.create_task(consume())
        try:
            await asyncio.sleep(OBSERVE_DURATION)
        finally:
            protocol_request.observation.cancel()
            await asyncio.gather(consumer_task, return_exceptions=True)
            log.info("Deregistered from %s", uri)

    def _handle_notification(self, uri: str, response: Message) -> None:
        """
        TODO 2: Process a single Observe notification.
        Requirements:
          - Extract the Observe option sequence number from response.opt.observe
          - Check for stale notification:
              * If the sequence number <= last seen (accounting for wrap-around at 2^24):
                  - Increment self._stale_count[uri]
                  - Log "STALE notification on {uri}: seq={seq} <= last={last}"
                  - RETURN (do not process the stale value)
          - Update self._last_seq[uri]
          - Parse response.payload as JSON
          - Log:
              [OBSERVE] {uri}  seq={seq}  val={value} {unit}  @ {timestamp}
        """
        seq = int(response.opt.observe or 0)
        last = self._last_seq.get(uri)
        if last is not None:
            delta = (seq - last) % (1 << 24)
            if delta == 0 or delta > (1 << 23):
                self._stale_count[uri] = self._stale_count.get(uri, 0) + 1
                log.warning("STALE notification on %s: seq=%s <= last=%s", uri, seq, last)
                return

        self._last_seq[uri] = seq
        payload = json.loads(response.payload)
        value = payload.get("value")
        unit = payload.get("unit", "")
        timestamp = payload.get("ts") or payload.get("timestamp") or datetime.now(timezone.utc).isoformat()
        log.info("[OBSERVE] %s  seq=%s  val=%s %s  @ %s", uri, seq, value, unit, timestamp)

    # ── Block2 Transfer ────────────────────────────────────────────────────────

    async def fetch_manifest(self) -> None:
        """
        TODO 3: Perform a GET on /factory/manifest and reassemble Block2.
        Requirements:
          - aiocoap handles Block2 reassembly automatically — just await the response
          - Log: "Manifest received: {len(payload)} bytes"
          - Parse as JSON and count the number of top-level items
          - Log: "Firmware entries in manifest: {count}"
          - Log: "Block2 transfer complete"

        Bonus: manually track how many Block2 blocks were received by
               checking response.opt.block2 if available.
        """
        request = Message(code=Code.GET, uri=f"{SERVER_BASE}/factory/manifest")
        response = await self._ctx.request(request).response
        payload = response.payload
        log.info("Manifest received: %s bytes", len(payload))
        data = json.loads(payload)
        count = len(data.get("firmware", data)) if isinstance(data, dict) else len(data)
        log.info("Firmware entries in manifest: %s", count)
        block2 = getattr(response.opt, "block2", None)
        block_count = (getattr(block2, "block_number", 0) + 1) if block2 else 1
        log.info("Block2 transfer complete")
        log.info("Block2 blocks received: %s", block_count)

    # ── Run ────────────────────────────────────────────────────────────────────

    async def run(self) -> None:
        """
        TODO 4: Run all observations concurrently, then fetch the manifest.
        Requirements:
          - Start observe_resource for both:
              coap://localhost/factory/line1/temperature
              coap://localhost/factory/line2/temperature
          - Run them concurrently using asyncio.gather
          - After both complete (OBSERVE_DURATION seconds), call fetch_manifest
          - Print a final summary: stale notification counts per URI
        """
        await self.start()
        try:
            await asyncio.gather(
                self.observe_resource(f"{SERVER_BASE}/factory/line1/temperature"),
                self.observe_resource(f"{SERVER_BASE}/factory/line2/temperature"),
            )
            await self.fetch_manifest()
            print("Final stale counts:")
            for uri, count in sorted(self._stale_count.items()):
                print(f"{uri}: {count}")
        finally:
            await self.stop()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    observer = FactoryObserver()
    asyncio.run(observer.run())
