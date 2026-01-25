"""Entry point for running jinjareportpy as a module."""

from .report import Report
from .sections import Section, TableSection, KPISection


def main() -> None:
    """Demo: Genera un informe de ventas con la API programática."""
    print("=" * 60)
    print("  JinjaReportPy - Generador de Informes Programático")
    print("=" * 60)
    print()

    # Crear informe
    report = Report(title="Informe de Ventas Q4 2025")

    # === PÁGINA 1: Resumen ===
    page1 = report.add_page()

    # Cabecera
    page1.set_header(
        title="Informe de Ventas",
        subtitle="Cuarto Trimestre 2025",
    )

    # Pie de página
    page1.set_footer(
        left_text="Generado con JinjaReportPy",
        right_text="Página 1",
    )

    # Sección: KPIs
    page1.add_section(KPISection(
        name="kpis",
        title="Indicadores Clave",
        kpis=[
            {"label": "Ventas Totales", "value": "€ 125.430"},
            {"label": "Clientes Nuevos", "value": "48"},
            {"label": "Crecimiento", "value": "+15%"},
        ],
    ))

    # Sección: Tabla de productos
    page1.add_section(TableSection(
        name="productos",
        title="Ventas por Producto",
        headers=["Producto", "Unidades", "Precio Unit.", "Total"],
        rows=[
            ["Producto A", "150", "€ 29,99", "€ 4.498,50"],
            ["Producto B", "320", "€ 49,99", "€ 15.996,80"],
            ["Producto C", "85", "€ 199,99", "€ 16.999,15"],
        ],
        footer_row=["Total", "555", "", "€ 37.494,45"],
    ))

    # Sección personalizada: Notas
    page1.add_section(Section(
        name="notas",
        template="""
        <div class="info-box">
            <strong>{{ titulo }}</strong><br>
            {{ contenido }}
        </div>
        """,
        data={
            "titulo": "Notas:",
            "contenido": "Los datos incluyen todas las regiones. Pendiente de auditoría final.",
        },
        css="""
        .info-box {
            background: #f8fafc;
            border-left: 4px solid #2563eb;
            padding: 10px 15px;
            margin-top: 20px;
        }
        """,
    ))

    # === PÁGINA 2: Detalle ===
    page2 = report.add_page()
    page2.set_header(title="Detalle por Región", subtitle="Q4 2025")
    page2.set_footer(left_text="Confidencial", right_text="Página 2")

    page2.add_section(TableSection(
        name="regiones",
        title="Ventas por Región",
        headers=["Región", "Ventas", "% del Total"],
        rows=[
            ["Norte", "€ 45.200", "36%"],
            ["Sur", "€ 32.100", "26%"],
            ["Este", "€ 28.500", "23%"],
            ["Oeste", "€ 19.630", "15%"],
        ],
    ))

    # Renderizar
    html = report.render()
    print(f"✓ Informe renderizado: {len(html):,} caracteres")

    # Exportar HTML
    html_path = report.export_html(filename="demo_ventas.html")
    print(f"✓ HTML guardado en: {html_path}")

    # Intentar exportar PDF
    try:
        pdf_path = report.export_pdf(filename="demo_ventas.pdf")
        print(f"✓ PDF guardado en: {pdf_path}")
    except Exception as e:
        print(f"⚠ PDF no disponible: {e}")

    print()
    print("¡Demo completado! Revisa la carpeta 'output'.")


if __name__ == "__main__":
    main()
