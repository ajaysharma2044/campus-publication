"""Message Batches API wrapper (specs/bulk-mode.md §2-3): build requests with a cached shared prefix, submit, poll, iterate results,
price usage from the API's usage fields (batch prices are 50% of standard), and a deterministic fake for tests and dry runs.
The real client is used only when ANTHROPIC_API_KEY is present; nothing here reads worker/.env."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Callable, Iterator

from ..budget import MODEL_PRICE_PER_MTOK_MINOR

BATCH_DISCOUNT = 0.5          # Message Batches API: 50% of standard prices
CACHE_WRITE_MULT = 1.25       # prompt caching: cache writes cost 1.25× input, reads 0.1× input
CACHE_READ_MULT = 0.10
POLL_SECONDS = 30


@dataclass
class BatchRequest:
    custom_id: str
    model: str
    system: str                      # the shared prefix, sent as one cached text block
    user: str
    max_tokens: int
    temperature: float = 0.2

    def params(self) -> dict:
        return {"model": self.model, "max_tokens": self.max_tokens, "temperature": self.temperature,
                "system": [{"type": "text", "text": self.system, "cache_control": {"type": "ephemeral"}}],
                "messages": [{"role": "user", "content": self.user}]}

    def est_input_tokens(self) -> int:
        return est_tokens(self.system) + est_tokens(self.user)


@dataclass
class BatchResult:
    custom_id: str
    ok: bool
    text: str | None
    usage: dict = field(default_factory=dict)
    error: str | None = None
    model: str | None = None


def est_tokens(text: str) -> int:
    return max(1, len(text or "") // 4)


def price_minor(model: str, *, input_tokens: int, output_tokens: int, cache_write: int = 0, cache_read: int = 0, batch: bool = True) -> int:
    """Cents for one request. Models without a price entry are refused by the spend cap (never silently free)."""
    if model not in MODEL_PRICE_PER_MTOK_MINOR:
        raise KeyError(f"no price entry for model {model}")
    cin, cout = MODEL_PRICE_PER_MTOK_MINOR[model]
    cents = (input_tokens * cin + output_tokens * cout + cache_write * cin * CACHE_WRITE_MULT + cache_read * cin * CACHE_READ_MULT) / 1_000_000
    if batch:
        cents *= BATCH_DISCOUNT
    return int(cents + 0.999)


def estimate_minor(requests: list[BatchRequest], *, cached_prefix: bool = True) -> int:
    """Upper-bound cents for a batch: full input + max output per request; with caching, the shared prefix is counted once as a
    write and then as cache reads (the API bills reads at 10% when the prefix is cached)."""
    if not requests:
        return 0
    total = 0
    prefix_tokens = est_tokens(requests[0].system)
    for i, r in enumerate(requests):
        if cached_prefix and i > 0 and r.system == requests[0].system:
            total += price_minor(r.model, input_tokens=est_tokens(r.user), output_tokens=r.max_tokens, cache_read=prefix_tokens)
        elif cached_prefix and i == 0:
            total += price_minor(r.model, input_tokens=est_tokens(r.user), output_tokens=r.max_tokens, cache_write=prefix_tokens)
        else:
            total += price_minor(r.model, input_tokens=r.est_input_tokens(), output_tokens=r.max_tokens)
    return total


def usage_minor(model: str, usage: dict) -> int:
    return price_minor(model, input_tokens=int(usage.get("input_tokens") or 0), output_tokens=int(usage.get("output_tokens") or 0),
                       cache_write=int(usage.get("cache_creation_input_tokens") or 0), cache_read=int(usage.get("cache_read_input_tokens") or 0))


class AnthropicBatchClient:
    """The real Message Batches API (anthropic SDK). Constructed only when the key is present."""

    name = "anthropic"

    def __init__(self):
        import anthropic  # local import: tests never need the SDK

        self._c = anthropic.Anthropic()

    def submit(self, requests: list[BatchRequest]) -> str:
        batch = self._c.messages.batches.create(requests=[{"custom_id": r.custom_id, "params": r.params()} for r in requests])
        return batch.id

    def status(self, batch_id: str) -> dict:
        b = self._c.messages.batches.retrieve(batch_id)
        counts = b.request_counts.model_dump() if hasattr(b.request_counts, "model_dump") else dict(b.request_counts)
        return {"status": b.processing_status, "counts": counts, "ended_at": str(b.ended_at) if b.ended_at else None}

    def results(self, batch_id: str) -> Iterator[BatchResult]:
        for item in self._c.messages.batches.results(batch_id):
            res = item.result
            if res.type == "succeeded":
                msg = res.message
                text = "".join(getattr(b, "text", "") for b in msg.content if getattr(b, "type", "") == "text")
                usage = msg.usage.model_dump() if hasattr(msg.usage, "model_dump") else dict(msg.usage)
                yield BatchResult(item.custom_id, True, text, usage, None, msg.model)
            else:
                err = getattr(getattr(res, "error", None), "message", None) or res.type
                yield BatchResult(item.custom_id, False, None, {}, str(err), None)

    def wait(self, batch_id: str, *, poll_seconds: int = POLL_SECONDS, timeout_seconds: int = 24 * 3600, sleep=time.sleep, log=print) -> dict:
        start = time.monotonic()
        while True:
            st = self.status(batch_id)
            if st["status"] == "ended":
                return st
            if time.monotonic() - start > timeout_seconds:
                raise TimeoutError(f"batch {batch_id} still {st['status']} after {timeout_seconds}s")
            log(f"batch {batch_id}: {st['status']} {st['counts']}")
            sleep(poll_seconds)


class FakeBatchClient:
    """Deterministic stand-in for tests and the no-key dry run: `responder(request) -> str` makes each reply; results are immediate
    and usage is estimated from lengths, so cost accounting runs through the same code as the real client."""

    name = "fake"

    def __init__(self, responder: Callable[[BatchRequest], str] | None = None):
        self.responder = responder or (lambda r: json.dumps({"claims": []}))
        self._batches: dict[str, list[BatchRequest]] = {}
        self.submitted: list[list[BatchRequest]] = []

    def submit(self, requests: list[BatchRequest]) -> str:
        import uuid

        bid = f"fake:{len(self._batches) + 1}:{uuid.uuid4().hex[:8]}"
        self._batches[bid] = list(requests)
        self.submitted.append(list(requests))
        return bid

    def status(self, batch_id: str) -> dict:
        n = len(self._batches.get(batch_id, []))
        return {"status": "ended", "counts": {"succeeded": n, "errored": 0, "processing": 0, "canceled": 0, "expired": 0}, "ended_at": "now"}

    def results(self, batch_id: str) -> Iterator[BatchResult]:
        for r in self._batches.get(batch_id, []):
            text = self.responder(r)
            yield BatchResult(r.custom_id, True, text, {"input_tokens": est_tokens(r.user), "output_tokens": est_tokens(text), "cache_read_input_tokens": est_tokens(r.system)}, None, r.model)

    def wait(self, batch_id: str, **_) -> dict:
        return self.status(batch_id)


def client_for(settings, *, fake_responder=None):
    """The real client when the key is present, else None (callers fall back to a dry run or the fake)."""
    if fake_responder is not None:
        return FakeBatchClient(fake_responder)
    if getattr(settings, "anthropic_api_key_present", False):
        return AnthropicBatchClient()
    return None
