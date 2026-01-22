"""
Document - Template-based document generator.

For documents such as invoices, quotes, receipts, delivery notes, contracts, etc.

This module provides:
- Document class: Base class for template-based documents
- Factory functions: create_invoice, create_quote, create_receipt, create_delivery_note

Custom templates can be added in two ways:
1. Via directory: Place .html files in the templates/ directory
2. Via code: Pass inline template string to the template parameter
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, BaseLoader

from .base import BaseDocument
from .config import ReportConfig
from .filters import register_default_filters
from .exceptions import TemplateNotFoundError


# Document-specific CSS
DOCUMENT_CSS = """
/* Document-specific styles */
.document {
    width: var(--page-width);
    min-height: var(--page-height);
    padding: var(--page-margin);
    margin: 0 auto;
    background: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.document-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 3px solid var(--primary-color);
}

.document-header .logo {
    max-width: 150px;
    max-height: 60px;
}

.document-header .title-block {
    text-align: right;
}

.document-header h1 {
    font-size: 24pt;
    color: var(--primary-color);
    margin-bottom: 5px;
}

.document-header .doc-number {
    font-size: 14pt;
    color: var(--text-muted);
}

.document-footer {
    position: absolute;
    bottom: var(--page-margin);
    left: var(--page-margin);
    right: var(--page-margin);
    padding-top: 15px;
    border-top: 1px solid var(--border-color);
    font-size: 8pt;
    color: var(--text-muted);
}

/* Invoice-specific */
.invoice-parties {
    display: flex;
    gap: 20px;
    margin-bottom: 25px;
}

.invoice-parties .party {
    flex: 1;
    padding: 15px;
    background: var(--bg-light);
    border-radius: 4px;
}

.invoice-parties .party-label {
    font-size: 8pt;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 8px;
}

.invoice-parties .party-name {
    font-size: 12pt;
    font-weight: 600;
    margin-bottom: 5px;
}

.invoice-meta {
    display: flex;
    justify-content: space-between;
    margin-bottom: 25px;
    padding: 15px;
    background: var(--bg-light);
    border-radius: 4px;
}

.invoice-meta .meta-item {
    text-align: center;
}

.invoice-meta .meta-label {
    font-size: 8pt;
    text-transform: uppercase;
    color: var(--text-muted);
}

.invoice-meta .meta-value {
    font-size: 11pt;
    font-weight: 600;
}

.invoice-items {
    margin-bottom: 25px;
}

.invoice-items table {
    width: 100%;
}

.invoice-items thead th {
    background: var(--primary-color);
    color: white;
    padding: 10px 12px;
}

.invoice-items tbody td {
    padding: 10px 12px;
}

.invoice-items tbody tr:nth-child(even) {
    background: var(--bg-light);
}

.invoice-totals {
    width: 300px;
    margin-left: auto;
}

.invoice-totals table {
    width: 100%;
}

.invoice-totals td {
    padding: 8px 0;
}

.invoice-totals .total-row {
    font-size: 14pt;
    font-weight: 700;
    border-top: 2px solid var(--primary-color);
}

.invoice-totals .total-row td {
    padding-top: 12px;
}

/* Quote-specific */
.quote-validity {
    background: #fef3c7;
    border-left: 4px solid #f59e0b;
    padding: 10px 15px;
    margin: 20px 0;
    font-size: 9pt;
}

/* Contract-specific */
.contract-clause {
    margin-bottom: 20px;
    page-break-inside: avoid;
}

.contract-clause h3 {
    font-size: 11pt;
    margin-bottom: 8px;
}

.contract-signature {
    display: flex;
    justify-content: space-between;
    margin-top: 50px;
    padding-top: 20px;
}

.signature-block {
    width: 45%;
    text-align: center;
}

.signature-line {
    border-top: 1px solid var(--text-color);
    margin-top: 60px;
    padding-top: 10px;
}

/* Receipt-specific */
.receipt-header {
    text-align: center;
    margin-bottom: 20px;
}

.receipt-header h1 {
    font-size: 18pt;
}

.receipt-details {
    border: 2px dashed var(--border-color);
    padding: 15px;
    margin: 20px 0;
}
"""


@dataclass
class Document(BaseDocument):
    """Template-based document generator.
    
    For creating invoices, quotes, contracts, receipts, delivery notes, etc.
    
    Attributes:
        title: Document title.
        template: Template name (file) or inline template string.
        data: Data dictionary for template rendering.
        css: Additional CSS styles for the document.
        config: Document configuration settings.
    
    Custom templates can be added in two ways:
        1. Via directory: Place .html files in templates/ directory
        2. Via code: Pass inline template string to template parameter
    
    Example with file template:
        >>> doc = Document(
        ...     title="Invoice #001",
        ...     template="invoice",  # Uses templates/invoice.html
        ...     data={
        ...         "invoice_number": "INV-2026-001",
        ...         "company": {"name": "My Company"},
        ...         "client": {"name": "Client Corp"},
        ...         "items": [...],
        ...         "total": 1000.00,
        ...     }
        ... )
        >>> doc.export_pdf("invoice.pdf")
    
    Example with inline template:
        >>> doc = Document(
        ...     title="Custom Contract",
        ...     template=\"\"\"
        ...     <div class="contract">
        ...         <h1>{{ title }}</h1>
        ...         <p>Between {{ company }} and {{ client }}</p>
        ...     </div>
        ...     \"\"\",
        ...     data={"title": "Agreement", "company": "A", "client": "B"},
        ...     css=".contract { font-family: serif; }",
        ... )
        >>> doc.export_html("contract.html")
    """
    
    template: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    css: str = ""
    
    # Template directories
    _templates_dir: Path = field(
        default_factory=lambda: Path(__file__).parent / "templates",
        repr=False,
    )
    
    def render_css(self) -> str:
        """Generate the document CSS.
        
        Returns:
            Document-specific CSS styles.
        """
        css_parts = [DOCUMENT_CSS]
        
        if self.css:
            css_parts.append(self.css)
        
        return "\n".join(css_parts)
    
    def render_content(self) -> str:
        """Render the document content using the template.
        
        Returns:
            Rendered HTML content.
        
        Raises:
            TemplateNotFoundError: If template file is not found.
        """
        if not self.template:
            return "<div class='document'><p>No template specified</p></div>"
        
        # Setup Jinja environment
        env = Environment(
            loader=FileSystemLoader(str(self._templates_dir)),
            autoescape=True,
        )
        register_default_filters(env)
        
        # Check if template is inline or file reference
        if "<" in self.template:
            # Inline template
            from jinja2 import DictLoader
            env = Environment(
                loader=DictLoader({"inline": self.template}),
                autoescape=True,
            )
            register_default_filters(env)
            template = env.get_template("inline")
        else:
            # File template
            template_name = self.template
            if not template_name.endswith(".html"):
                template_name += ".html"
            
            try:
                template = env.get_template(template_name)
            except Exception as e:
                raise TemplateNotFoundError(
                    f"Template '{template_name}' not found in {self._templates_dir}"
                ) from e
        
        return template.render(**self.data)
    
    def __repr__(self) -> str:
        return f"Document(title='{self.title}', template='{self.template}')"


# =============================================================================
# DOCUMENT FACTORIES - Convenient functions to create common documents
# =============================================================================

def create_invoice(
    invoice_number: str,
    company: dict[str, Any],
    client: dict[str, Any],
    items: list[dict[str, Any]],
    issue_date: datetime | str | None = None,
    due_date: datetime | str | None = None,
    notes: str = "",
    payment_info: dict[str, Any] | None = None,
    tax_rate: float = 21.0,
    currency: str = "€",
    css: str = "",
) -> Document:
    """Create an invoice document.
    
    Creates a professional invoice with automatic calculations for subtotals,
    taxes, and totals. Supports multiple VAT rates per item.
    
    Args:
        invoice_number: Unique invoice identifier (e.g., "INV-2026-001").
        company: Issuer/seller information dictionary containing:
            - name (str): Company name (required)
            - tax_id (str): Tax identification number
            - address (str): Street address
            - city (str): City
            - postal_code (str): Postal/ZIP code
            - country (str): Country
            - phone (str): Contact phone
            - email (str): Contact email
            - logo (str): Path to logo image (optional)
        client: Customer/buyer information dictionary containing:
            - name (str): Client name (required)
            - tax_id (str): Tax identification number
            - address (str): Street address
            - city (str): City
            - postal_code (str): Postal/ZIP code
        items: List of invoice line items, each containing:
            - description (str): Item description (required)
            - quantity (int|float): Quantity (default: 1)
            - unit_price (float): Price per unit (required)
            - vat_rate (float): VAT percentage (default: tax_rate)
            - total (float): Line total (auto-calculated if not provided)
        issue_date: Invoice issue date. Defaults to today if None.
        due_date: Payment due date. Defaults to 30 days from issue if None.
        notes: Additional notes or observations to display on invoice.
        payment_info: Payment information dictionary containing:
            - method (str): Payment method (e.g., "Bank Transfer")
            - bank (str): Bank name
            - iban (str): IBAN account number
            - swift (str): SWIFT/BIC code
        tax_rate: Default VAT rate percentage (default: 21.0).
        currency: Currency symbol (default: "€").
        css: Additional custom CSS styles.
    
    Returns:
        Document: Configured invoice document ready for export.
    
    Automatic Calculations:
        - Line totals: quantity × unit_price
        - Subtotal: Sum of all line totals
        - VAT amount: Grouped by VAT rate
        - Total: subtotal + VAT amounts
    
    Example:
        >>> invoice = create_invoice(
        ...     invoice_number="INV-2026-001",
        ...     company={
        ...         "name": "My Company Ltd.",
        ...         "tax_id": "GB123456789",
        ...         "address": "123 Business St",
        ...         "city": "London",
        ...     },
        ...     client={
        ...         "name": "Client Corporation",
        ...         "tax_id": "GB987654321",
        ...     },
        ...     items=[
        ...         {"description": "Consulting", "quantity": 10, "unit_price": 150},
        ...         {"description": "Software License", "quantity": 1, "unit_price": 500},
        ...     ],
        ...     tax_rate=20.0,
        ...     currency="£",
        ...     payment_info={"method": "Bank Transfer", "iban": "GB82WEST..."},
        ... )
        >>> invoice.export_pdf("invoice.pdf")
    """
    from datetime import timedelta
    
    if issue_date is None:
        issue_date = datetime.now()
    if due_date is None:
        if isinstance(issue_date, datetime):
            due_date = issue_date + timedelta(days=30)
        else:
            due_date = datetime.now() + timedelta(days=30)
    
    # Calculate totals for items
    processed_items = []
    for item in items:
        qty = item.get("quantity", 1)
        price = item.get("unit_price", 0)
        vat = item.get("vat_rate", tax_rate)
        total = item.get("total", qty * price)
        
        processed_items.append({
            **item,
            "quantity": qty,
            "unit_price": price,
            "vat_rate": vat,
            "total": total,
        })
    
    # Calculate subtotal and VAT
    subtotal = sum(item["total"] for item in processed_items)
    
    # Group by VAT rate
    vat_totals: dict[float, float] = {}
    for item in processed_items:
        rate = item["vat_rate"]
        amount = item["total"] * (rate / 100)
        vat_totals[rate] = vat_totals.get(rate, 0) + amount
    
    vat_lines = [
        {"rate": rate, "amount": amount}
        for rate, amount in sorted(vat_totals.items())
    ]
    
    total = subtotal + sum(vat_totals.values())
    
    return Document(
        title=f"Invoice {invoice_number}",
        template="invoice",
        data={
            "invoice_number": invoice_number,
            "company": company,
            "client": client,
            "items": processed_items,
            "issue_date": issue_date,
            "due_date": due_date,
            "notes": notes,
            "payment_info": payment_info,
            "subtotal": subtotal,
            "vat_lines": vat_lines,
            "total": total,
            "currency": currency,
        },
        css=css,
    )


def create_quote(
    quote_number: str,
    company: dict[str, Any],
    client: dict[str, Any],
    items: list[dict[str, Any]],
    validity_days: int = 30,
    notes: str = "",
    terms: str = "",
    tax_rate: float = 21.0,
    currency: str = "€",
    discount: float = 0.0,
    css: str = "",
) -> Document:
    """Create a quote/estimate document.
    
    Creates a professional quote with automatic validity date calculation
    and optional discount support.
    
    Args:
        quote_number: Unique quote identifier (e.g., "QT-2026-015").
        company: Issuer information dictionary (see create_invoice for fields).
        client: Customer information dictionary (see create_invoice for fields).
        items: List of quoted items, each containing:
            - description (str): Item description (required)
            - quantity (int|float): Quantity (default: 1)
            - unit_price (float): Price per unit (required)
            - total (float): Line total (auto-calculated if not provided)
        validity_days: Number of days the quote is valid (default: 30).
        notes: Additional notes or observations.
        terms: Terms and conditions text.
        tax_rate: VAT rate percentage (default: 21.0).
        currency: Currency symbol (default: "€").
        discount: Discount percentage to apply (e.g., 10.0 for 10%).
        css: Additional custom CSS styles.
    
    Returns:
        Document: Configured quote document ready for export.
    
    Example:
        >>> quote = create_quote(
        ...     quote_number="QT-2026-015",
        ...     company={"name": "My Company Ltd."},
        ...     client={"name": "Potential Client"},
        ...     items=[
        ...         {"description": "Web Development", "quantity": 1, "unit_price": 5000},
        ...         {"description": "Hosting (12 months)", "quantity": 12, "unit_price": 50},
        ...     ],
        ...     validity_days=30,
        ...     discount=10.0,  # 10% discount
        ...     terms="50% upfront, 50% on completion.",
        ... )
        >>> quote.export_pdf("quote.pdf")
    """
    # Calculate totals
    subtotal = sum(
        item.get("total", item.get("quantity", 1) * item.get("unit_price", 0))
        for item in items
    )
    
    discount_amount = subtotal * (discount / 100) if discount else 0
    subtotal_after_discount = subtotal - discount_amount
    vat_amount = subtotal_after_discount * (tax_rate / 100)
    total = subtotal_after_discount + vat_amount
    
    validity_date = datetime.now() + __import__("datetime").timedelta(days=validity_days)
    
    return Document(
        title=f"Quote {quote_number}",
        template="quote",
        data={
            "quote_number": quote_number,
            "company": company,
            "client": client,
            "items": items,
            "issue_date": datetime.now(),
            "validity_date": validity_date,
            "validity_days": validity_days,
            "notes": notes,
            "terms": terms,
            "subtotal": subtotal,
            "discount": discount,
            "discount_amount": discount_amount,
            "vat_rate": tax_rate,
            "vat_amount": vat_amount,
            "total": total,
            "currency": currency,
        },
        css=css,
    )


def create_receipt(
    receipt_number: str,
    company: dict[str, Any],
    client: dict[str, Any],
    amount: float,
    concept: str,
    payment_method: str = "Cash",
    payment_date: datetime | None = None,
    notes: str = "",
    currency: str = "€",
    css: str = "",
) -> Document:
    """Create a payment receipt document.
    
    Creates a receipt confirming payment has been received.
    
    Args:
        receipt_number: Unique receipt identifier (e.g., "REC-2026-042").
        company: Issuer information dictionary (see create_invoice for fields).
        client: Payer information dictionary (see create_invoice for fields).
        amount: Amount received.
        concept: Payment description or reference (e.g., "Payment for INV-2025-089").
        payment_method: Method of payment (default: "Cash").
            Common values: "Cash", "Bank Transfer", "Credit Card", "Check"
        payment_date: Date payment was received. Defaults to today if None.
        notes: Additional notes or observations.
        currency: Currency symbol (default: "€").
        css: Additional custom CSS styles.
    
    Returns:
        Document: Configured receipt document ready for export.
    
    Use Cases:
        - Payment confirmations
        - Cash receipts
        - Refund documentation
        - Donation receipts
    
    Example:
        >>> receipt = create_receipt(
        ...     receipt_number="REC-2026-042",
        ...     company={"name": "My Company Ltd."},
        ...     client={"name": "Client Name"},
        ...     amount=1500.00,
        ...     concept="Payment for invoice INV-2025-089",
        ...     payment_method="Bank Transfer",
        ...     currency="£",
        ... )
        >>> receipt.export_html("receipt.html")
    """
    if payment_date is None:
        payment_date = datetime.now()
    
    return Document(
        title=f"Receipt {receipt_number}",
        template="receipt",
        data={
            "receipt_number": receipt_number,
            "company": company,
            "client": client,
            "amount": amount,
            "concept": concept,
            "payment_method": payment_method,
            "date": payment_date,
            "notes": notes,
            "currency": currency,
        },
        css=css,
    )


def create_delivery_note(
    delivery_number: str,
    company: dict[str, Any],
    client: dict[str, Any],
    items: list[dict[str, Any]],
    delivery_date: datetime | None = None,
    shipping_address: str = "",
    carrier: str = "",
    tracking_number: str = "",
    notes: str = "",
    css: str = "",
) -> Document:
    """Create a delivery note/shipping document.
    
    Creates a delivery note for goods dispatch and tracking.
    
    Args:
        delivery_number: Unique delivery note identifier (e.g., "DN-2026-007").
        company: Sender/shipper information dictionary:
            - name (str): Company name (required)
            - address (str): Warehouse/shipping address
            - city (str): City
            - postal_code (str): Postal code
        client: Recipient information dictionary:
            - name (str): Recipient name (required)
            - address (str): Delivery address
            - city (str): City
            - postal_code (str): Postal code
        items: List of items being delivered, each containing:
            - code (str): Product/SKU code (optional)
            - description (str): Item description (required)
            - quantity (int|float): Quantity (required)
        delivery_date: Shipping date. Defaults to today if None.
        shipping_address: Delivery address if different from client address.
        carrier: Shipping carrier name (e.g., "Express Logistics").
        tracking_number: Package tracking number.
        notes: Special handling instructions or notes.
        css: Additional custom CSS styles.
    
    Returns:
        Document: Configured delivery note document ready for export.
    
    Features:
        - Product codes and descriptions
        - Quantity tracking
        - Carrier and tracking information
        - Separate shipping address support
        - Special handling notes
    
    Example:
        >>> delivery = create_delivery_note(
        ...     delivery_number="DN-2026-007",
        ...     company={
        ...         "name": "My Company Ltd.",
        ...         "address": "123 Warehouse Lane",
        ...     },
        ...     client={
        ...         "name": "Client Corp",
        ...         "address": "456 Delivery Street",
        ...         "city": "Manchester",
        ...     },
        ...     items=[
        ...         {"code": "HW-001", "description": "Server Unit", "quantity": 2},
        ...         {"code": "HW-002", "description": "Network Switch", "quantity": 5},
        ...     ],
        ...     carrier="Express Logistics",
        ...     tracking_number="TRK-123456789",
        ...     notes="Handle with care - Fragile equipment",
        ... )
        >>> delivery.export_html("delivery_note.html")
    """
    if delivery_date is None:
        delivery_date = datetime.now()
    
    return Document(
        title=f"Delivery Note {delivery_number}",
        template="delivery_note",
        data={
            "delivery_number": delivery_number,
            "company": company,
            "client": client,
            "items": items,
            "delivery_address": shipping_address or client.get("address", ""),
            "date": delivery_date,
            "carrier": carrier,
            "tracking_number": tracking_number,
            "notes": notes,
        },
        css=css,
    )
