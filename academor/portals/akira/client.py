"""The only place that talks to the Claude API.

Configuration comes from the environment (``.env`` is loaded by settings):

    ANTHROPIC_API_KEY          required; without it AKIRA stays silent and the pages show only numbers
    AKIRA_MODEL                optional, default claude-opus-5-5
    AKIRA_MONTHLY_BUDGET_USD   optional, default 80
    AKIRA_STUDENT_MONTHLY_LIMIT optional, default 30 reports per student per month
    AKIRA_ENABLED              optional, "0" switches AKIRA off without removing the key
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from decimal import Decimal

logger = logging.getLogger(__name__)

DEFAULT_MODEL = 'claude-opus-5-5'
DEFAULT_MONTHLY_BUDGET_USD = 80
DEFAULT_STUDENT_MONTHLY_LIMIT = 30
REQUEST_TIMEOUT_SEC = 45.0

# USD per million tokens: input, output, cache read, cache write (5 minutes).
PRICES = {
    'claude-opus-5-5': (4.0, 20.0, 0.20, 5.0),
    'claude-sonnet-5-5': (2.0, 10.0, 0.10, 2.5),
    'claude-haiku-5-5': (0.10, 0.50, 0.01, 0.125),
}


class AkiraError(Exception):
    """The AI call did not give a usable answer (the page falls back to numbers only).

    ``completion`` is set when the request was billed even though the answer is unusable.
    """

    def __init__(self, message: str, completion: 'Completion | None' = None):
        super().__init__(message)
        self.completion = completion


@dataclass
class Completion:
    text: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0

    @property
    def cost_usd(self) -> Decimal:
        price_in, price_out, price_read, price_write = PRICES.get(self.model, PRICES[DEFAULT_MODEL])
        cost = (
            self.input_tokens * price_in
            + self.output_tokens * price_out
            + self.cache_read_tokens * price_read
            + self.cache_write_tokens * price_write
        ) / 1_000_000
        return Decimal(str(round(cost, 5)))


def _env_number(name: str, default: float) -> float:
    try:
        return float(os.getenv(name) or default)
    except ValueError:
        return float(default)


def api_key() -> str:
    return (os.getenv('ANTHROPIC_API_KEY') or '').strip()


def model_name() -> str:
    return (os.getenv('AKIRA_MODEL') or DEFAULT_MODEL).strip()


def monthly_budget_usd() -> Decimal:
    return Decimal(str(_env_number('AKIRA_MONTHLY_BUDGET_USD', DEFAULT_MONTHLY_BUDGET_USD)))


def student_monthly_limit() -> int:
    return int(_env_number('AKIRA_STUDENT_MONTHLY_LIMIT', DEFAULT_STUDENT_MONTHLY_LIMIT))


def is_configured() -> bool:
    switched_off = (os.getenv('AKIRA_ENABLED') or '1').strip().lower() in {'0', 'false', 'no', 'off'}
    return bool(api_key()) and not switched_off


def complete(system: str, user: str, *, max_tokens: int = 3000, effort: str = 'low') -> Completion:
    """One request to Claude. Raises ``AkiraError`` on any failure."""
    if not is_configured():
        raise AkiraError('not configured')
    try:
        import anthropic
    except ImportError as exc:  # the dependency is in pyproject; this only fires on a stale image
        raise AkiraError('anthropic package missing') from exc

    model = model_name()
    client = anthropic.Anthropic(api_key=api_key(), timeout=REQUEST_TIMEOUT_SEC, max_retries=1)
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=[{'type': 'text', 'text': system, 'cache_control': {'type': 'ephemeral'}}],
            messages=[{'role': 'user', 'content': user}],
            output_config={'effort': effort},
        )
    except anthropic.APIError as exc:
        logger.warning('AKIRA: API call failed: %s', exc.__class__.__name__)
        raise AkiraError(exc.__class__.__name__) from exc

    usage = getattr(response, 'usage', None)
    completion = Completion(
        text='',
        model=model,
        input_tokens=getattr(usage, 'input_tokens', 0) or 0,
        output_tokens=getattr(usage, 'output_tokens', 0) or 0,
        cache_read_tokens=getattr(usage, 'cache_read_input_tokens', 0) or 0,
        cache_write_tokens=getattr(usage, 'cache_creation_input_tokens', 0) or 0,
    )
    if response.stop_reason == 'refusal':
        raise AkiraError('refusal', completion)
    completion.text = ''.join(
        block.text for block in response.content if getattr(block, 'type', '') == 'text'
    ).strip()
    if not completion.text:
        raise AkiraError(f'empty answer ({response.stop_reason})', completion)
    return completion
