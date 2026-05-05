"""Tests for document data classes and factory functions."""

from unittest.mock import patch

from jinja2.sandbox import SandboxedEnvironment

from jinjareportpy.document import (
    DeliveryNoteData,
    Document,
    InvoiceData,
    PartyInfo,
    QuoteData,
    ReceiptData,
    _party_dict,
    create_delivery_note,
    create_invoice,
    create_quote,
    create_receipt,
)


class TestPartyInfo:
    """Tests for the PartyInfo dataclass."""

    def test_defaults(self) -> None:
        party = PartyInfo()
        assert party.name == ""
        assert party.tax_id == ""

    def test_to_dict_only_truthy(self) -> None:
        party = PartyInfo(name="Acme", tax_id="GB123")
        d = party.to_dict()
        assert d == {"name": "Acme", "tax_id": "GB123"}
        assert "address" not in d

    def test_to_dict_all_fields(self) -> None:
        party = PartyInfo(
            name="Co", tax_id="X", address="123 St",
            city="Madrid", postal_code="28001", country="ES",
            phone="555", email="a@b.com", logo="logo.png",
        )
        d = party.to_dict()
        assert len(d) == 9


class TestInvoiceData:
    """Tests for InvoiceData dataclass."""

    def test_defaults(self) -> None:
        data = InvoiceData()
        assert data.tax_rate == 21.0
        assert data.currency == "€"
        assert data.items == []

    def test_party_dict_from_party_info(self) -> None:
        party = PartyInfo(name="Test Co")
        result = _party_dict(party)
        assert result == {"name": "Test Co"}

    def test_party_dict_from_raw_dict(self) -> None:
        result = _party_dict({"name": "Raw"})
        assert result == {"name": "Raw"}


class TestFactoryFunctions:
    """Tests for create_invoice, create_quote, create_receipt, create_delivery_note."""

    def test_create_invoice_with_dicts(self) -> None:
        invoice = create_invoice(
            invoice_number="INV-001",
            company={"name": "Company"},
            client={"name": "Client"},
            items=[{"description": "Svc", "quantity": 1, "unit_price": 100}],
        )
        assert invoice.title == "Invoice INV-001"

    def test_create_invoice_with_dataclass(self) -> None:
        data = InvoiceData(
            number="INV-002",
            company=PartyInfo(name="Company"),
            client=PartyInfo(name="Client"),
            items=[{"description": "Svc", "quantity": 1, "unit_price": 100}],
        )
        invoice = create_invoice(data)
        assert invoice.title == "Invoice INV-002"

    def test_create_quote_with_dicts(self) -> None:
        quote = create_quote(
            quote_number="QT-001",
            company={"name": "Company"},
            client={"name": "Client"},
            items=[{"description": "Dev", "quantity": 1, "unit_price": 5000}],
        )
        assert quote.title == "Quote QT-001"

    def test_create_quote_with_dataclass(self) -> None:
        data = QuoteData(
            number="QT-002",
            company=PartyInfo(name="Company"),
            client=PartyInfo(name="Client"),
            items=[{"description": "Dev", "quantity": 1, "unit_price": 5000}],
            validity_days=15,
        )
        quote = create_quote(data)
        assert quote.title == "Quote QT-002"

    def test_create_receipt_with_dicts(self) -> None:
        receipt = create_receipt(
            receipt_number="REC-001",
            company={"name": "Company"},
            client={"name": "Client"},
            amount=500.0,
            concept="Payment",
        )
        assert receipt.title == "Receipt REC-001"

    def test_create_receipt_with_dataclass(self) -> None:
        data = ReceiptData(
            number="REC-002",
            company=PartyInfo(name="Company"),
            client=PartyInfo(name="Client"),
            amount=750.0,
            concept="Service payment",
        )
        receipt = create_receipt(data)
        assert receipt.title == "Receipt REC-002"

    def test_create_delivery_note_with_dicts(self) -> None:
        note = create_delivery_note(
            delivery_number="DN-001",
            company={"name": "Company"},
            client={"name": "Client"},
            items=[{"description": "Item", "quantity": 1}],
        )
        assert note.title == "Delivery Note DN-001"

    def test_create_delivery_note_with_dataclass(self) -> None:
        data = DeliveryNoteData(
            number="DN-002",
            company=PartyInfo(name="Company"),
            client=PartyInfo(name="Client"),
            items=[{"description": "Item", "quantity": 2}],
        )
        note = create_delivery_note(data)
        assert note.title == "Delivery Note DN-002"


class TestDocumentSandboxedRendering:
    """Verify Document.render_content uses SandboxedEnvironment."""

    def test_inline_template_uses_sandboxed_env(self) -> None:
        """Inline templates must render through SandboxedEnvironment."""
        doc = Document(
            title="Test",
            template="<p>{{ name }}</p>",
            data={"name": "Safe"},
        )
        with patch(
            "jinjareportpy.document.SandboxedEnvironment",
            wraps=SandboxedEnvironment,
        ) as mock_env:
            result = doc.render_content()
            assert mock_env.called
        assert "Safe" in result

    def test_file_template_uses_sandboxed_env(self) -> None:
        """File-based templates must also use SandboxedEnvironment."""
        doc = Document(
            title="Test",
            template="invoice",
            data={
                "invoice_number": "TST-001",
                "company": {"name": "Co"},
                "client": {"name": "Client"},
                "items": [],
                "subtotal": 0,
                "tax_rate": 0,
                "tax_amount": 0,
                "total": 0,
            },
        )
        with patch(
            "jinjareportpy.document.SandboxedEnvironment",
            wraps=SandboxedEnvironment,
        ) as mock_env:
            doc.render_content()
            assert mock_env.called
