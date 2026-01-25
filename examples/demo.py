#!/usr/bin/env python3
"""
📄 JinjaReportPy - Complete Demo

Demonstrates all project features:
- Documents: Invoices, Quotes, Receipts, Delivery Notes
- Reports: Multi-page with dynamic sections
- Formats: default, corporate, minimal
- Sections: KPIs, Tables, Text, Custom

To run:
    uv run python examples/demo.py
"""

from datetime import datetime
from pathlib import Path

from jinjareportpy import (
    # Base
    BaseDocument,
    # Documents
    Document,
    create_invoice,
    create_quote,
    create_receipt,
    create_delivery_note,
    # Reports
    Report,
    Section,
    TableSection,
    KPISection,
    TextSection,
    # Formats
    set_default_format,
    get_available_formats,
)


def main():
    """Generate a complete demo showing all capabilities."""
    
    print("📄 JinjaReportPy - Complete Demo")
    print("=" * 50)
    
    formats = get_available_formats()
    print(f"📁 Available formats: {', '.join(formats)}")
    
    # Use default portable output directory (jinjareportpy/output)
    # No need to create it manually - ReportConfig does it automatically
    from jinjareportpy.config import ReportConfig
    output_dir = ReportConfig().output_dir
    
    # =========================================================================
    # CREATE MULTI-PAGE REPORT
    # =========================================================================
    set_default_format("corporate")
    report = Report(title="📄 JinjaReportPy - Complete Demo")
    
    # =========================================================================
    # PAGE 1: Simplified API (ReportBuilder)
    # =========================================================================
    print("\n📊 Page 1: Simplified API...")
    
    page1 = report.add_page()
    page1.set_header(
        title="Simplified API",
        subtitle="ReportBuilder & quick_report",
        date=datetime.now().strftime("%Y-%m-%d"),
    )
    page1.set_footer(
        left_text="JinjaReportPy Demo",
        center_text="Confidential",
        right_text="Page 1 of 4",
    )
    
    page1.add_section(TextSection(
        name="intro_simple",
        title="ReportBuilder: Reports in Few Lines",
        content="""
        <p>The <strong>Simplified API</strong> allows creating professional reports
        with very few lines of code using the <em>builder</em> pattern:</p>
        
        <pre><code>builder = (
    ReportBuilder("Report", format_name="corporate")
    .header(title="Title", subtitle="Subtitle")
    .footer(left="Company", center="Confidential", right="Page 1")
    .add_kpis("kpis", [...])
    .add_table("table", headers=[...], rows=[...])
)
builder.export_html("output.html")</code></pre>
        """,
    ))
    
    page1.add_section(KPISection(
        name="kpis_example",
        title="Example: KPIs",
        kpis=[
            {"label": "Revenue", "value": "$125K", "change": "+12%"},
            {"label": "Customers", "value": "1,542", "change": "+8%"},
            {"label": "Conversion", "value": "4.2%", "change": "+0.5%"},
        ],
    ))
    
    page1.add_section(TableSection(
        name="table_example",
        title="Example: Table",
        headers=["Product", "Units", "Revenue"],
        rows=[
            ["Product A", "450", "$45,000"],
            ["Product B", "320", "$32,000"],
            ["Product C", "280", "$48,000"],
        ],
        footer_row=["Total", "1,050", "$125,000"],
    ))
    
    # =========================================================================
    # PAGE 2: Full Control API (Report + Sections)
    # =========================================================================
    print("📊 Page 2: Full Control API...")
    
    set_default_format("default")
    page2 = report.add_page()
    page2.set_header(
        title="Full Control API",
        subtitle="Report, Page & Sections",
    )
    page2.set_footer(
        left_text="JinjaReportPy Demo",
        right_text="Page 2 of 4",
    )
    
    page2.add_section(TextSection(
        name="intro_full",
        title="Total Control with Report + Sections",
        content="""
        <p>The <strong>Full Control API</strong> offers complete control over every aspect
        of the report, ideal for advanced use cases:</p>
        
        <ul>
            <li><code>Report</code> - Container for pages</li>
            <li><code>Page</code> - Header + Footer + Sections</li>
            <li><code>Section</code> - Custom Template + CSS + Data</li>
            <li><code>TableSection</code>, <code>KPISection</code>, <code>TextSection</code></li>
        </ul>
        """,
    ))
    
    page2.add_section(KPISection(
        name="sales_kpis",
        title="Q4 2025 Sales Metrics",
        kpis=[
            {"label": "Total Sales", "value": "$1,245,890", "change": 15.3},
            {"label": "New Customers", "value": "487", "change": 8.2},
            {"label": "Avg Ticket", "value": "$2,558", "change": -2.1},
            {"label": "Conversion", "value": "23.4%", "change": 4.5},
        ],
    ))
    
    page2.add_section(TableSection(
        name="product_sales",
        title="Sales by Product Line",
        headers=["Product", "Units", "Revenue", "% Total", "vs Q3"],
        rows=[
            ["Premium Line", "1,245", "$498,000", "40%", "+25%"],
            ["Standard", "3,890", "$389,000", "31%", "+12%"],
            ["Basic", "5,670", "$226,800", "18%", "+5%"],
            ["Accessories", "8,900", "$132,090", "11%", "+18%"],
        ],
        footer_row=["TOTAL", "19,705", "$1,245,890", "100%", "+15%"],
    ))
    
    # =========================================================================
    # PAGE 3: Custom Sections
    # =========================================================================
    print("📊 Page 3: Custom Sections...")
    
    set_default_format("minimal")
    page3 = report.add_page()
    page3.set_header(
        title="Custom Sections",
        subtitle="Custom Templates and CSS",
    )
    page3.set_footer(
        left_text="JinjaReportPy Demo",
        right_text="Page 3 of 4",
    )
    
    page3.add_section(TextSection(
        name="intro_custom",
        title="Section: Custom Template + CSS",
        content="""
        <p>Create fully customized sections with your own
        <strong>Jinja2 template</strong> and <strong>CSS</strong>:</p>
        """,
    ))
    
    # Custom section with own template and CSS
    page3.add_section(Section(
        name="achievements",
        template="""
        <h2>🏆 Key Achievements</h2>
        <div class="achievements-grid">
            {% for item in achievements %}
            <div class="achievement-item">
                <span class="achievement-icon">{{ item.icon }}</span>
                <div class="achievement-content">
                    <strong>{{ item.title }}</strong>
                    <p>{{ item.description }}</p>
                </div>
            </div>
            {% endfor %}
        </div>
        """,
        data={
            "achievements": [
                {"icon": "📈", "title": "Sales Record", "description": "Highest quarterly revenue in company history"},
                {"icon": "🤝", "title": "New Partners", "description": "5 new strategic partnerships signed"},
                {"icon": "⭐", "title": "Customer Satisfaction", "description": "NPS score of 72 points (+8 vs previous)"},
                {"icon": "🚀", "title": "Efficiency", "description": "15% reduction in average sales cycle"},
            ]
        },
        css="""
        .achievements-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 15px;
        }
        .achievement-item {
            display: flex;
            gap: 12px;
            padding: 15px;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 8px;
            border-left: 4px solid #0ea5e9;
        }
        .achievement-icon { font-size: 24pt; }
        .achievement-content strong { color: #0369a1; }
        .achievement-content p { margin: 5px 0 0 0; font-size: 9pt; color: #64748b; }
        """,
    ))
    
    page3.add_section(TableSection(
        name="tasks",
        title="Sprint Status",
        headers=["Task", "Assigned", "Status"],
        rows=[
            ["Implement OAuth login", "Ana", "✓ Completed"],
            ["Dashboard v2 design", "Carlos", "✓ Completed"],
            ["User API endpoints", "Laura", "✓ Completed"],
            ["E2E testing", "Pedro", "🔄 In progress"],
        ],
    ))
    
    # =========================================================================
    # PAGE 4: Corporate Format + Action Plan
    # =========================================================================
    print("📊 Page 4: Corporate Format...")
    
    set_default_format("corporate")
    page4 = report.add_page()
    page4.set_header(
        title="Financial Report",
        subtitle="Q4 2025 Results",
        data={"reference": "FIN-2025-Q4-001"},
    )
    page4.set_footer(
        left_text="Finance Department",
        center_text="CONFIDENTIAL",
        right_text="Page 4 of 4",
    )
    
    page4.add_section(KPISection(
        name="finance",
        title="Financial Indicators",
        kpis=[
            {"label": "EBITDA", "value": "$3.2M", "change": 18},
            {"label": "Net Margin", "value": "24.5%", "change": 3},
            {"label": "ROI", "value": "156%", "change": 12},
        ],
    ))
    
    page4.add_section(TableSection(
        name="balance",
        title="Income Statement",
        headers=["Concept", "Q4 2025", "Q4 2024", "Change"],
        rows=[
            ["Operating Revenue", "$12,450,000", "$10,890,000", "+14.3%"],
            ["Direct Costs", "$6,230,000", "$5,670,000", "+9.9%"],
            ["Gross Margin", "$6,220,000", "$5,220,000", "+19.2%"],
            ["Operating Expenses", "$3,020,000", "$2,890,000", "+4.5%"],
            ["EBITDA", "$3,200,000", "$2,330,000", "+37.3%"],
        ],
        footer_row=["Net Income", "$2,560,000", "$1,820,000", "+40.7%"],
    ))
    
    page4.add_section(TableSection(
        name="action_plan",
        title="Q1 2026 Action Plan",
        headers=["Initiative", "Owner", "Date", "Priority"],
        rows=[
            ["Expand South sales team", "HR", "2026-01-15", "High"],
            ["Launch Premium Line v2 campaign", "Marketing", "2026-02-01", "High"],
            ["Implement advanced CRM", "IT", "2026-02-28", "Medium"],
            ["Gold loyalty program", "Sales", "2026-03-15", "Medium"],
        ],
    ))
    
    page4.add_section(TextSection(
        name="final_note",
        title="Director's Note",
        content="""
        <blockquote>
        "This has been an exceptional quarter that demonstrates the commitment and talent 
        of our entire team. We look forward to 2026 with optimism and ambitious goals."
        </blockquote>
        <p style="text-align: right; font-style: italic;">— Maria Gonzalez, Sales Director</p>
        """,
    ))
    
    # =========================================================================
    # EXPORT REPORT
    # =========================================================================
    output_file = output_dir / "demo_report.html"
    path = report.export_html(output_file)
    print(f"   ✓ Report: {path}")
    
    # =========================================================================
    # DOCUMENTS: Invoices, Quotes, Receipts, Delivery Notes
    # =========================================================================
    print("\n📄 Generating Documents...")
    
    # Common data
    company = {
        "name": "TechSolutions Inc.",
        "address": "123 Innovation Street",
        "city": "San Francisco",
        "postal_code": "94102",
        "tax_id": "12-3456789",
    }
    
    client = {
        "name": "Example Corp.",
        "address": "456 Main Avenue",
        "city": "New York",
        "postal_code": "10001",
        "tax_id": "98-7654321",
    }
    
    # 1. INVOICE
    invoice = create_invoice(
        invoice_number="INV-2026-001",
        company=company,
        client=client,
        items=[
            {"description": "Web Development - React Frontend", "quantity": 40, "unit_price": 75},
            {"description": "Web Development - Python Backend", "quantity": 60, "unit_price": 85},
            {"description": "Cloud Server Configuration", "quantity": 1, "unit_price": 500},
            {"description": "Monthly Support", "quantity": 3, "unit_price": 200},
        ],
        notes="Project completed per contract CT-2025-089 specifications.",
        payment_info={
            "method": "Wire Transfer",
            "iban": "US12 3456 7890 1234 5678 9012",
        },
    )
    invoice_path = invoice.export_html(output_dir / "invoice.html")
    print(f"   ✓ Invoice: {invoice_path}")
    
    # 2. QUOTE
    quote = create_quote(
        quote_number="QT-2026-015",
        company=company,
        client=client,
        items=[
            {"description": "Mobile App UX/UI Design", "quantity": 1, "unit_price": 3500},
            {"description": "Native iOS Development", "quantity": 1, "unit_price": 8000},
            {"description": "Native Android Development", "quantity": 1, "unit_price": 8000},
            {"description": "REST API Backend", "quantity": 1, "unit_price": 5000},
            {"description": "Testing & QA", "quantity": 1, "unit_price": 2000},
        ],
        validity_days=30,
        notes="Includes 3 months post-launch maintenance.",
        terms="Payment: 50% upfront, 50% on delivery. Estimated timeline: 4 months.",
    )
    quote_path = quote.export_html(output_dir / "quote.html")
    print(f"   ✓ Quote: {quote_path}")
    
    # 3. RECEIPT
    receipt = create_receipt(
        receipt_number="REC-2026-042",
        company=company,
        client=client,
        amount=1500.00,
        concept="Partial payment for invoice INV-2025-089",
        payment_method="Wire Transfer",
        notes="Second payment of 3 agreed.",
    )
    receipt_path = receipt.export_html(output_dir / "receipt.html")
    print(f"   ✓ Receipt: {receipt_path}")
    
    # 4. DELIVERY NOTE
    delivery = create_delivery_note(
        delivery_number="DN-2026-007",
        company=company,
        client=client,
        items=[
            {"code": "HW-001", "description": "Dell PowerEdge R750 Server", "quantity": 2, "unit": "pcs"},
            {"code": "HW-002", "description": "Cisco Catalyst 9300 Switch", "quantity": 1, "unit": "pcs"},
            {"code": "HW-003", "description": "Cat6 Cable (meters)", "quantity": 100, "unit": "m"},
            {"code": "SW-001", "description": "Windows Server 2022 License", "quantity": 2, "unit": "lic"},
        ],
        shipping_address="Data Center - 10 Server Street, New York 10001",
        notes="Urgent delivery. Contact John Smith (ext. 234) for access.",
    )
    delivery_path = delivery.export_html(output_dir / "delivery_note.html")
    print(f"   ✓ Delivery Note: {delivery_path}")
    
    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print("\n" + "=" * 50)
    print("✨ Everything generated successfully!")
    print(f"\n📂 Files in: {output_dir.absolute()}")
    print("   • demo_report.html   - Multi-page report")
    print("   • invoice.html       - Invoice")
    print("   • quote.html         - Quote")
    print("   • receipt.html       - Receipt")
    print("   • delivery_note.html - Delivery Note")
    
    # Open in browser
    import webbrowser
    print("\n🌐 Opening invoice in browser...")
    webbrowser.open(f"file://{invoice_path.absolute()}")


if __name__ == "__main__":
    main()
