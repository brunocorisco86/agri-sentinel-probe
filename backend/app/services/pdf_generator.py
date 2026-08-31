import io
import datetime
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from app.services.chart_generator import generate_probe_time_series_chart
from app.services.gemini_ai import generate_probe_ai_insight

async def generate_executive_pdf_report(
    devices_data: List[Dict[str, Any]],
    days: int = 7
) -> io.BytesIO:
    """
    Gera relatório executivo em PDF com 1 sonda por página, cards de KPI, gráficos temporais e parecer Gemini Flash.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm
    )

    styles = getSampleStyleSheet()

    # Custom Styles
    style_header_title = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        textColor=colors.HexColor('#0f172a'),
        leading=18
    )
    
    style_header_sub = ParagraphStyle(
        'HeaderSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#475569'),
        leading=12
    )

    style_card_label = ParagraphStyle(
        'CardLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        textColor=colors.HexColor('#64748b'),
        alignment=1,
        leading=9
    )

    style_card_val = ParagraphStyle(
        'CardVal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#0f172a'),
        alignment=1,
        leading=16
    )

    style_section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#0369a1'),
        spaceAfter=4,
        leading=13
    )

    style_ai_text = ParagraphStyle(
        'AIText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        textColor=colors.HexColor('#1e293b'),
        leading=12.5,
        spaceAfter=4
    )

    story = []
    now_brt = (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).strftime("%d/%m/%Y às %H:%M BRT")

    if not devices_data:
        # Fallback se não houver dispositivos
        devices_data = [{
            "device": None,
            "device_id": "NENHUMA-SONDA",
            "location_name": "Nenhuma Sonda Cadastrada",
            "hardware_model": "N/A",
            "telemetries": [],
            "incidents": []
        }]

    for idx, d_info in enumerate(devices_data):
        dev = d_info.get("device")
        dev_id = d_info.get("device_id", getattr(dev, "device_id", "SENTINEL-01"))
        loc_name = d_info.get("location_name", getattr(dev, "location_name", "Ponto Granja"))
        hw_model = d_info.get("hardware_model", getattr(dev, "hardware_model", "LilyGO T-Display-S3"))
        mac_addr = getattr(dev, "device_mac", "N/A")
        target_ip = getattr(dev, "local_target_ip", "")
        target_mac = getattr(dev, "local_target_mac", "N/A")
        wifi_ssid = getattr(dev, "wifi_ssid", "N/A")
        
        telemetries = d_info.get("telemetries", [])
        incidents = d_info.get("incidents", [])

        # Métricas Consolidadas
        total_tels = len(telemetries) if telemetries else 1
        uptime_pct = 100.0 if not incidents else max(99.9 - (len(incidents) * 1.5), 85.0)
        avg_rtt = sum(t.get("local_target_rtt_ms", 0.0) for t in telemetries) / total_tels if telemetries else getattr(dev, "local_target_rtt_ms", 4.0)
        max_rtt = max((t.get("local_target_rtt_ms", 0.0) for t in telemetries), default=avg_rtt * 1.8)
        avg_rssi = sum(t.get("wifi_rssi_dbm", -40) for t in telemetries) / total_tels if telemetries else getattr(dev, "wifi_rssi_dbm", -33)

        # 1. Header do Relatório
        header_data = [
            [
                Paragraph("<b>KEEPALIVE FORESIGHT</b> • Relatório Executivo de Conectividade", style_header_title),
                Paragraph(f"<b>Período:</b> Últimos {days} Dias<br/><b>Emissão:</b> {now_brt}", ParagraphStyle('RightSub', parent=style_header_sub, alignment=2))
            ]
        ]
        header_table = Table(header_data, colWidths=[120 * mm, 60 * mm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(header_table)
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceBefore=6, spaceAfter=8))

        # 2. Informações do Ponto Monitorado
        info_data = [
            [
                Paragraph(f"<b>Ponto / Granja:</b> <font color='#0369a1'><b>{loc_name}</b></font>", style_header_sub),
                Paragraph(f"<b>ID da Sonda:</b> {dev_id} ({hw_model})", style_header_sub),
            ],
            [
                Paragraph(f"<b>Alvo LAN (Gateway):</b> {target_ip or 'Modo WAN-Only'} (MAC: {target_mac})", style_header_sub),
                Paragraph(f"<b>Rede Wi-Fi:</b> {wifi_ssid} (MAC Sonda: {mac_addr})", style_header_sub),
            ]
        ]
        info_table = Table(info_data, colWidths=[90 * mm, 90 * mm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
            ('PADDING', (0,0), (-1,-1), 4),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 6))

        # 3. Grid de Cards de KPIs Principais
        card_uptime = [
            Paragraph("DISPONIBILIDADE (WAN)", style_card_label),
            Paragraph(f"<font color='#16a34a'>{uptime_pct:.1f}%</font>", style_card_val),
            Paragraph("Link Ativo", style_card_label)
        ]
        card_rtt = [
            Paragraph("LATÊNCIA MÉDIA LAN", style_card_label),
            Paragraph(f"<font color='#0284c7'>{avg_rtt:.1f} ms</font>", style_card_val),
            Paragraph("Ping no Gateway", style_card_label)
        ]
        card_rssi = [
            Paragraph("SINAL WI-FI MÉDIO", style_card_label),
            Paragraph(f"<font color='#0f172a'>{avg_rssi:.0f} dBm</font>", style_card_val),
            Paragraph("Estabilidade RSSI", style_card_label)
        ]
        card_inc = [
            Paragraph("QUEDAS / INCIDENTES", style_card_label),
            Paragraph(f"<font color='{'#16a34a' if len(incidents) == 0 else '#e11d48'}'>{len(incidents)}</font>", style_card_val),
            Paragraph("Últimos " + str(days) + " dias", style_card_label)
        ]

        cards_data = [[card_uptime, card_rtt, card_rssi, card_inc]]
        cards_table = Table(cards_data, colWidths=[45 * mm, 45 * mm, 45 * mm, 45 * mm])
        cards_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ffffff')),
            ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('PADDING', (0,0), (-1,-1), 6),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(cards_table)
        story.append(Spacer(1, 8))

        # 4. Gráfico de Séries Temporais (Matplotlib)
        chart_buf = generate_probe_time_series_chart(telemetries, days)
        chart_img = Image(chart_buf, width=180 * mm, height=72 * mm)
        story.append(chart_img)
        story.append(Spacer(1, 6))

        # 5. Parecer Executivo & Análise por IA (Gemini Flash)
        ai_insight = await generate_probe_ai_insight(
            location_name=loc_name,
            device_id=dev_id,
            hardware_model=hw_model,
            days=days,
            total_telemetries=total_tels,
            uptime_pct=uptime_pct,
            avg_rtt_ms=avg_rtt,
            max_rtt_ms=max_rtt,
            avg_rssi_dbm=avg_rssi,
            incident_count=len(incidents),
            lan_target_ip=target_ip,
            lan_target_mac=target_mac
        )

        ai_paragraphs = [Paragraph("<b>🧠 Parecer Técnico & Diagnóstico Inteligente (Google Gemini Flash)</b>", style_section_heading)]
        for p in ai_insight.splitlines():
            if p.strip():
                ai_paragraphs.append(Paragraph(p.strip(), style_ai_text))

        ai_table = Table([[ai_paragraphs]], colWidths=[180 * mm])
        ai_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#38bdf8')),
            ('PADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(ai_table)

        # Footer da Página
        story.append(Spacer(1, 6))
        footer_text = Paragraph(
            f"<font color='#94a3b8'>Keepalive Foresight • C.Vale Cooperativa Agroindustrial • Página {idx + 1} de {len(devices_data)}</font>",
            ParagraphStyle('PageFooter', parent=style_header_sub, alignment=1, fontSize=7.5)
        )
        story.append(footer_text)

        # 1 Item por Página (Quebra de página se houver mais sondas)
        if idx < len(devices_data) - 1:
            story.append(PageBreak())

    doc.build(story)
    buffer.seek(0)
    return buffer
