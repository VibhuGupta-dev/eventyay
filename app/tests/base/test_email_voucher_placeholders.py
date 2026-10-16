"""Unit tests for voucher_urls and redeem_url email placeholders."""

from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BASE = 'https://tickets.example.com/my-org/demo/redeem'


def _make_placeholder(name):
    """Return the callable (3rd arg) for the named placeholder from base_placeholders()."""
    from eventyay.base.email import base_placeholders

    event = MagicMock()
    # base_placeholders() is a signal receiver – call it directly
    for ph in base_placeholders(sender=event):
        if ph.identifier == name:
            return ph.func
    raise KeyError(f'Placeholder {name!r} not found')


def _fake_uri(event, viewname, kwargs=None):
    return BASE


# ---------------------------------------------------------------------------
# voucher_urls
# ---------------------------------------------------------------------------


class TestVoucherUrlsPlaceholder:
    """Tests for the {voucher_urls} placeholder."""

    def _render(self, monkeypatch, voucher_list):
        monkeypatch.setattr(
            'eventyay.base.email.build_absolute_uri',
            _fake_uri,
        )
        func = _make_placeholder('voucher_urls')
        event = MagicMock()
        return func(event, voucher_list)

    def test_single_code_produces_one_url(self, monkeypatch):
        result = self._render(monkeypatch, ['ABC123'])
        assert result == f'{BASE}?voucher=ABC123'

    def test_multiple_codes_joined_with_newline(self, monkeypatch):
        result = self._render(monkeypatch, ['AAA', 'BBB'])
        lines = result.split('  \n')
        assert len(lines) == 2
        assert lines[0] == f'{BASE}?voucher=AAA'
        assert lines[1] == f'{BASE}?voucher=BBB'

    def test_empty_list_returns_empty_string(self, monkeypatch):
        result = self._render(monkeypatch, [])
        assert result == ''

    def test_none_voucher_list_does_not_raise(self, monkeypatch):
        """voucher_list=None must not raise TypeError."""
        result = self._render(monkeypatch, None)
        assert result == ''

    def test_code_with_ampersand_is_url_encoded(self, monkeypatch):
        result = self._render(monkeypatch, ['A&B'])
        assert '?voucher=A%26B' in result
        assert '&B' not in result.split('?voucher=')[1]

    def test_code_with_hash_is_url_encoded(self, monkeypatch):
        result = self._render(monkeypatch, ['C#D'])
        assert '?voucher=C%23D' in result

    def test_code_with_space_is_url_encoded(self, monkeypatch):
        result = self._render(monkeypatch, ['VOUCHER CODE'])
        assert '?voucher=VOUCHER%20CODE' in result or '?voucher=VOUCHER+CODE' in result


# ---------------------------------------------------------------------------
# redeem_url
# ---------------------------------------------------------------------------


class TestRedeemUrlPlaceholder:
    """Tests for the {redeem_url} placeholder."""

    def _render(self, monkeypatch, voucher_list):
        monkeypatch.setattr(
            'eventyay.base.email.build_absolute_uri',
            _fake_uri,
        )
        func = _make_placeholder('redeem_url')
        event = MagicMock()
        return func(event, voucher_list)

    def test_single_code_included_in_url(self, monkeypatch):
        result = self._render(monkeypatch, ['XYZ789'])
        assert result == f'{BASE}?voucher=XYZ789'

    def test_multiple_codes_uses_first(self, monkeypatch):
        result = self._render(monkeypatch, ['FIRST', 'SECOND'])
        assert '?voucher=FIRST' in result
        assert 'SECOND' not in result

    def test_empty_list_returns_base_url(self, monkeypatch):
        result = self._render(monkeypatch, [])
        assert result == BASE
        assert '?voucher=' not in result

    def test_none_voucher_list_returns_base_url(self, monkeypatch):
        result = self._render(monkeypatch, None)
        assert result == BASE
        assert '?voucher=' not in result

    def test_code_with_ampersand_is_url_encoded(self, monkeypatch):
        result = self._render(monkeypatch, ['A&B'])
        assert '?voucher=A%26B' in result
        assert result.count('&') == 0  # no raw & in query string

    def test_code_with_hash_is_url_encoded(self, monkeypatch):
        result = self._render(monkeypatch, ['C#D'])
        assert '?voucher=C%23D' in result

    def test_code_with_space_is_url_encoded(self, monkeypatch):
        result = self._render(monkeypatch, ['MY CODE'])
        assert '?voucher=MY%20CODE' in result or '?voucher=MY+CODE' in result
