#!/usr/bin/env python3
"""
Test output directory configuration.

Demonstrates how to customize the output directory for generated files.
"""

from pathlib import Path
import ninjareportpy as nr
from ninjareportpy import Report, ReportConfig, create_invoice, PageSize, Orientation

def test_custom_output_dir():
    """Test custom output directory configuration."""
    print("🧪 Testing Output Directory Configuration")
    print("=" * 60)
    
    # Test 1: Custom output directory via ReportConfig
    print("\n✓ Test 1: Custom output directory via ReportConfig")
    custom_dir = Path("./custom_reports")
    config = ReportConfig(
        output_dir=custom_dir,
        page_size=PageSize.A4,
        orientation=Orientation.PORTRAIT,
    )
    
    report = Report(title="Test Report", config=config)
    page = report.add_page()
    page.add_section(name="test", template="<h1>Test Content</h1>")
    
    output_path = report.export_html()
    print(f"   Generated: {output_path}")
    print(f"   Directory exists: {output_path.parent.exists()}")
    assert output_path.parent == custom_dir
    
    # Test 2: Default output directory (portable, application root / output)
    print("\n✓ Test 2: Default output directory")
    report2 = Report(title="Default Test")
    page2 = report2.add_page()
    page2.add_section(name="test2", template="<h1>Default Output</h1>")

    output_path2 = report2.export_html(filename="default_test.html")
    default_output = Path(nr.__file__).resolve().parent / "output"
    print(f"   Generated: {output_path2}")
    print(f"   Default dir: {output_path2.parent}")
    assert output_path2.parent == default_output

    # Test 3: Per-export custom path
    print("\n✓ Test 3: Per-export custom path")
    invoice = create_invoice(
        invoice_number="TEST-001",
        company={"name": "Test Company"},
        client={"name": "Test Client"},
        items=[{"description": "Test Item", "quantity": 1, "unit_price": 100}],
    )
    
    custom_path = Path("./exports/invoices")
    if custom_path.exists() and custom_path.is_file():
        custom_path.unlink()
    custom_path.mkdir(parents=True, exist_ok=True)
    output_path3 = invoice.export_html(custom_path, filename="test_invoice.html")
    print(f"   Generated: {output_path3}")
    print(f"   Directory exists: {output_path3.parent.exists()}")
    assert output_path3.parent == custom_path
    
    # Test 4: Full custom path
    print("\n✓ Test 4: Full custom path")
    full_path = Path("./temp_reports/full_path_test.html")
    output_path4 = invoice.export_html(full_path)
    print(f"   Generated: {output_path4}")
    assert output_path4 == full_path
    
    print("\n" + "=" * 60)
    print("✨ All tests passed!")
    print(f"\n📂 Generated directories:")
    print(f"   • {custom_dir}")
    print(f"   • {Path('./output')}")
    print(f"   • {Path('./exports/invoices')}")
    print(f"   • {Path('./temp_reports')}")


if __name__ == "__main__":
    test_custom_output_dir()
