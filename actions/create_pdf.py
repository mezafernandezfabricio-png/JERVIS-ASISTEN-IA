# -*- coding: utf-8 -*-
"""
create_pdf.py — Generador profesional de documentos PDF para JARVIS.
Crea documentos completos, extensos, estructurados y de alta calidad.
Guarda SIEMPRE en el Escritorio del usuario con apertura automática.
"""

import os
import sys
import re
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
API_FILE = BASE_DIR / "config" / "api_keys.json"

def _get_desktop_dir() -> Path:
    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        onedrive_desktop = Path.home() / "OneDrive" / "Desktop"
        if onedrive_desktop.exists():
            return onedrive_desktop
        desktop.mkdir(parents=True, exist_ok=True)
    return desktop

def _get_api_key() -> str:
    try:
        if API_FILE.exists():
            return json.loads(API_FILE.read_text(encoding="utf-8")).get("gemini_api_key", "")
    except Exception:
        pass
    return ""

def _sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name).strip()
    return cleaned if cleaned else f"Documento_JARVIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def _enrich_content_if_needed(title: str, content: str, subtitle: str) -> str:
    """Si el contenido es corto o es solo un tema, genera un documento extenso y completo con IA."""
    words = content.strip().split()
    if len(words) >= 40 and "\n" in content:
        return content

    api_key = _get_api_key()
    if not api_key:
        return content

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        prompt = (
            f"Actúa como un redactor y analista profesional de JARVIS. Genera el contenido COMPLETO, EXTENSO, PROFUNDO y PROFESIONAL para un documento PDF.\n"
            f"Título del documento: '{title}'\n"
            f"Tema / Indicación del usuario: '{content}'\n"
            f"Subtítulo / Contexto: '{subtitle}'\n\n"
            "REQUISITOS OBLIGATORIOS:\n"
            "1. Redacta en español formal, elegante y claro.\n"
            "2. Estructura el documento con títulos de sección usando '# ' para títulos principales y '## ' para subtítulos.\n"
            "3. Incluye: Introducción detallada, Desarrollo exhaustivo con al menos 4 a 6 secciones temáticas profundas, puntos clave con viñetas ('- '), análisis de datos relevantes, y una Conclusión sólida.\n"
            "4. Escribe contenido 100% real, informativo, rico en hechos y conocimientos. No uses textos de relleno ni placeholders.\n"
            "5. Longitud: mínimo 400 a 700 palabras bien explicadas."
        )
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        if resp.text and len(resp.text.strip()) > 100:
            return resp.text.strip()
    except Exception:
        pass
    return content

def create_pdf(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    """
    Crea un archivo PDF formateado, completo y estructurado en el Escritorio.
    Parámetros:
        - title / titulo: Título del documento
        - content / texto / body: Contenido o indicación del tema
        - filename / nombre_archivo: Nombre del archivo PDF (opcional)
        - subtitle / subtitulo: Subtítulo (opcional)
        - author / autor: Autor del documento (opcional)
        - open_file / abrir: Si debe abrir el PDF al crearlo (default True)
    """
    params = parameters or {}
    title = params.get("title") or params.get("titulo") or "Informe JARVIS"
    content = params.get("content") or params.get("texto") or params.get("body") or params.get("text") or "Documento generado automáticamente por JARVIS."
    subtitle = params.get("subtitle") or params.get("subtitulo") or ""
    author = params.get("author") or params.get("autor") or "JARVIS Asistente Inteligente"
    open_file = params.get("open_file", params.get("abrir", True))
    
    if player:
        try: player.write_log(f"📄 Redactando y generando PDF profesional: '{title}'...")
        except: pass

    # Enriquecer y desarrollar el contenido completo si viene resumido
    content = _enrich_content_if_needed(title, content, subtitle)

    filename = params.get("filename") or params.get("nombre_archivo") or params.get("output_path") or ""
    if not filename:
        filename = f"{_sanitize_filename(title)}.pdf"
    elif not filename.lower().endswith(".pdf"):
        filename = f"{_sanitize_filename(filename)}.pdf"
    else:
        filename = _sanitize_filename(filename[:-4]) + ".pdf"

    desktop = _get_desktop_dir()
    pdf_path = desktop / filename

    success = False
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle

        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )

        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'JarvisTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0f172a'),
            spaceAfter=6
        )
        
        subtitle_style = ParagraphStyle(
            'JarvisSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#475569'),
            spaceAfter=10
        )
        
        meta_style = ParagraphStyle(
            'JarvisMeta',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#94a3b8'),
            spaceAfter=12
        )

        h1_style = ParagraphStyle(
            'JarvisH1',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=15,
            leading=19,
            textColor=colors.HexColor('#0f172a'),
            spaceBefore=14,
            spaceAfter=6
        )

        h2_style = ParagraphStyle(
            'JarvisH2',
            parent=styles['Heading3'],
            fontName='Helvetica-Bold',
            fontSize=12.5,
            leading=16,
            textColor=colors.HexColor('#1e293b'),
            spaceBefore=10,
            spaceAfter=4
        )

        body_style = ParagraphStyle(
            'JarvisBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10.5,
            leading=15.5,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=8
        )

        bullet_style = ParagraphStyle(
            'JarvisBullet',
            parent=body_style,
            leftIndent=16,
            bulletIndent=6,
            spaceAfter=4
        )

        story = []
        
        # Cabecera
        story.append(Paragraph(title, title_style))
        if subtitle:
            story.append(Paragraph(subtitle, subtitle_style))
        
        now_str = datetime.now().strftime('%d/%m/%Y %H:%M')
        story.append(Paragraph(f"Autor: {author}  •  Fecha de emisión: {now_str}", meta_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#d97706'), spaceAfter=14, spaceBefore=2))

        # Procesar contenido
        lines = str(content).split("\n")
        for line in lines:
            line_str = line.strip()
            if not line_str:
                story.append(Spacer(1, 6))
                continue
            
            if line_str.startswith("# "):
                story.append(Paragraph(line_str[2:], h1_style))
            elif line_str.startswith("## "):
                story.append(Paragraph(line_str[3:], h2_style))
            elif line_str.startswith("### "):
                story.append(Paragraph(line_str[4:], h2_style))
            elif line_str.startswith("- ") or line_str.startswith("* "):
                safe_bullet = line_str[2:].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                safe_bullet = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', safe_bullet)
                story.append(Paragraph(f"• {safe_bullet}", bullet_style))
            elif re.match(r'^\d+\.\s', line_str):
                safe_num = line_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                safe_num = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', safe_num)
                story.append(Paragraph(safe_num, bullet_style))
            else:
                safe_text = line_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                safe_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', safe_text)
                story.append(Paragraph(safe_text, body_style))

        # Pie de página
        story.append(Spacer(1, 16))
        story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#e2e8f0'), spaceAfter=6, spaceBefore=8))
        story.append(Paragraph("Documento generado con éxito por el Asistente Inteligente JARVIS.", meta_style))

        doc.build(story)
        success = True
    except Exception:
        try:
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(str(pdf_path), pagesize=letter)
            c.setFont("Helvetica-Bold", 18)
            c.drawString(54, 730, title)
            c.setFont("Helvetica", 10)
            c.drawString(54, 710, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Autor: {author}")
            c.setStrokeColorRGB(0.85, 0.5, 0.0)
            c.line(54, 700, 558, 700)
            c.setFont("Helvetica", 10)
            y = 680
            for line in str(content).split("\n"):
                if y < 60:
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y = 730
                c.drawString(54, y, line[:90])
                y -= 15
            c.save()
            success = True
        except Exception:
            pass

    if not success:
        return f"Error al generar el PDF '{filename}'."

    if player:
        try: player.write_log(f"📄 PDF creado en Escritorio: {pdf_path.name}")
        except: pass

    if open_file and pdf_path.exists():
        try: os.startfile(str(pdf_path))
        except: pass

    return f"Documento PDF creado exitosamente en tu Escritorio: '{pdf_path.name}' con toda la información solicitada."

def create_pdf_tool(parameters: dict = None, player=None, speak=None, **kwargs) -> str:
    return create_pdf(parameters, player, speak, **kwargs)
