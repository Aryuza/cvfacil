# -*- coding: utf-8 -*-
"""
cv_dividers_only.py — versión optimizada (espaciado mejorado)
Genera un único PDF estilo "DIVIDERS" listo para ATS (Argentina).
"""

import os, re
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PIL import Image as PILImage, ImageOps, ImageDraw

def create_circular_image_with_border(image_path: str, output_path: str, border_color: str = "#4f81bd", border_width: int = 2):
    try:
        img = PILImage.open(image_path).convert("RGBA")
        
        # Crop to square
        w, h = img.size
        min_dim = min(w, h)
        left = (w - min_dim)/2
        top = (h - min_dim)/2
        right = (w + min_dim)/2
        bottom = (h + min_dim)/2
        img = img.crop((left, top, right, bottom))
        
        # Create mask
        mask = PILImage.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + img.size, fill=255)
        
        # Fit image to mask
        output = Ops_fit = PILImage.new('RGBA', img.size, (0, 0, 0, 0))
        output.paste(img, (0, 0), mask=mask)

        # Draw border
        draw = ImageDraw.Draw(output)
        w, h = img.size
        # draw.ellipse expects (x0, y0, x1, y1)
        draw.ellipse((0, 0, w-1, h-1), outline=border_color, width=border_width)

        output.save(output_path, format="PNG")
        return output_path
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def _norm(s: Any) -> str:
    if s is None:
        return ""
    return str(s).strip()

def _has(x: Any) -> bool:
    if x is None:
        return False
    if isinstance(x, str):
        return _norm(x) != ""
    if isinstance(x, (list, tuple, set)):
        return any(_has(i) for i in x)
    if isinstance(x, dict):
        return any(_has(v) for v in x.values())
    return True

def _styles(fonts: Dict[str,int]):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='NameCenter', fontSize=fonts['name'], leading=fonts['name']+2,
                              fontName='Helvetica-Bold', alignment=1, textColor=colors.HexColor("#4f81bd")))
    styles.add(ParagraphStyle(name='ContactCenter', fontSize=fonts['body'], leading=fonts['body']+2,
                              alignment=1, textColor=colors.black))
    styles.add(ParagraphStyle(name='Section', fontSize=fonts['heading'], leading=fonts['heading']+2,
                              fontName='Helvetica-Bold', textTransform='uppercase', textColor=colors.HexColor("#4f81bd")))
    styles.add(ParagraphStyle(name='Body', fontSize=fonts['body'], leading=fonts['body']+3, textColor=colors.black))
    styles.add(ParagraphStyle(name='Subtle', fontSize=fonts['body'], leading=fonts['body']+2, textColor=colors.HexColor("#333333")))
    return styles

FONTS_LARGER  = dict(name=26, heading=14, body=12)
FONTS_MEDIUM  = dict(name=22, heading=12, body=10)
FONTS_SMALLER = dict(name=18, heading=10.5, body=8.5)
FONTS_TINY    = dict(name=16, heading=8.5, body=6.5)

class HR(Flowable):
    def __init__(self, up=6, down=6, width=0.8, color=colors.black):
        Flowable.__init__(self)
        self.up = up; self.down = down; self.width = width; self.color = color
        self.height = self.up + self.down + 1
    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.width)
        self.canv.line(0, self.down, self._aw, self.down)
    def wrap(self, aw, ah):
        self._aw = aw
        return aw, self.height

def _section(title: str, styles):
    return [
        Spacer(1, 10),
        HR(up=6, down=6),
        Spacer(1, 10),
        Paragraph(title, styles['Section']),
        Spacer(1, 6)
    ]

def _safe_name(s: str) -> str:
    s = _norm(s) or "CV"
    return re.sub(r'[^A-Za-z0-9_\-]+','_', s)

def _story_dividers(data: Dict[str,Any], styles, fonts, image_path: Optional[str]):
    story = []

    if image_path and os.path.exists(image_path):
        try:
            img = Image(image_path)
            iw, ih = img.wrap(0,0)
            max_w = 2.8*cm
            if iw > max_w:
                scale = max_w/iw
                img._restrictSize(max_w, ih*scale)
            img.hAlign = 'CENTER'
            story += [img, Spacer(1, 6)]
        except Exception:
            pass

    if _has(data.get("nombre")):
        story.append(Paragraph(_norm(data["nombre"]), styles['NameCenter']))
    contact = " | ".join([v for v in [
        _norm(data.get("telefono","")), _norm(data.get("email","")),
        _norm(data.get("ciudad","")), _norm(data.get("linkedin",""))
    ] if v])
    if _norm(contact):
        story.append(Paragraph(contact, styles['ContactCenter']))

    story += _section("Perfil profesional", styles)
    if _has(data.get("perfil")):
        story.append(Paragraph(_norm(data["perfil"]), styles['Body']))

    # EXPERIENCIA LABORAL (con espacio entre cada experiencia)
    story += _section("Experiencia laboral", styles)
    experiencias = data.get("experiencia", [])
    for idx, e in enumerate(experiencias):
        header = " – ".join([p for p in [_norm(e.get('puesto','')), _norm(e.get('empresa',''))] if p])
        if header:
            story.append(Paragraph(header, styles['Body']))
        sub = " | ".join([p for p in [_norm(e.get('fechas','')), _norm(e.get('ubicacion',''))] if p])
        if sub:
            story.append(Paragraph(sub, styles['Subtle']))
        logs = [l for l in (e.get('logros') or []) if _has(l)]
        for l in logs:
            story.append(Paragraph(f"• {l}", styles['Body']))
        if idx < len(experiencias) - 1:
            story.append(Spacer(1, 8))  # Espacio entre experiencias

    # EDUCACIÓN Y FORMACIÓN (con espacio entre cada formación)
    story += _section("Educación y formación", styles)
    educaciones = data.get("educacion", [])
    for idx, ed in enumerate(educaciones):
        title_line = " – ".join([p for p in [_norm(ed.get('titulo','')), _norm(ed.get('institucion',''))] if p])
        if title_line:
            story.append(Paragraph(title_line, styles['Body']))
        sub = " | ".join([p for p in [_norm(ed.get('fechas','')), _norm(ed.get('ubicacion',''))] if p])
        if sub:
            story.append(Paragraph(sub, styles['Subtle']))
        if idx < len(educaciones) - 1:
            story.append(Spacer(1, 8))  # Espacio entre formaciones

    skills = [s for s in (data.get('habilidades') or []) if _has(s)]
    if skills:
        story += _section("Habilidades", styles)
        story.append(Paragraph(" | ".join(skills), styles['Body']))

    langs = [i for i in (data.get('idiomas') or []) if _has(i.get('idioma'))]
    if langs:
        story += _section("Idiomas", styles)
        for i in langs:
            lvl = f" – {_norm(i.get('nivel'))}" if _has(i.get('nivel')) else ""
            story.append(Paragraph(f"{_norm(i['idioma'])}{lvl}", styles['Body']))

    lic = [l for l in (data.get('licencias') or []) if _has(l)]
    if lic:
        story += _section("Licencias / Información adicional", styles)
        story.append(Paragraph(" | ".join(lic), styles['Body']))

    return story

def build_dividers_pdf(data: Dict[str,Any], out_path: str, image_path: Optional[str]=None, font_mode: str="medium"):
    if font_mode == "tiny":
        fonts = FONTS_TINY
    elif font_mode == "smaller":
        fonts = FONTS_SMALLER
    elif font_mode == "larger":
        fonts = FONTS_LARGER
    else:
        fonts = FONTS_MEDIUM
    styles = _styles(fonts)
    doc = SimpleDocTemplate(out_path, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=1.0*cm, bottomMargin=1.0*cm)
    story = _story_dividers(data, styles, fonts, image_path=image_path)
    # Ensure dir exists
    out_dir = os.path.dirname(out_path)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    doc.build(story)
    return out_path

def generate_divider(data: Dict[str,Any], out_dir: str="/mnt/data", image_path: Optional[str]=None) -> str:
    base = _safe_name(data.get("nombre","CV"))
    out_path = os.path.join(out_dir, f"CV_{base}_normal.pdf")
    return build_dividers_pdf(data, out_path, image_path=image_path, font_mode="medium")

def generate_divider_smaller(data: Dict[str,Any], out_dir: str="/mnt/data", image_path: Optional[str]=None) -> str:
    base = _safe_name(data.get("nombre","CV"))
    out_path = os.path.join(out_dir, f"CV_{base}_small.pdf")
    return build_dividers_pdf(data, out_path, image_path=image_path, font_mode="smaller")

def generate_divider_larger(data: Dict[str,Any], out_dir: str="/mnt/data", image_path: Optional[str]=None) -> str:
    base = _safe_name(data.get("nombre","CV"))
    out_path = os.path.join(out_dir, f"CV_{base}_large.pdf")
    return build_dividers_pdf(data, out_path, image_path=image_path, font_mode="larger")

def generate_divider_tiny(data: Dict[str,Any], out_dir: str="/mnt/data", image_path: Optional[str]=None) -> str:
    base = _safe_name(data.get("nombre","CV"))
    out_path = os.path.join(out_dir, f"CV_{base}_tiny.pdf")
    return build_dividers_pdf(data, out_path, image_path=image_path, font_mode="tiny")

def apply_updates(data: Dict[str,Any], updates: Dict[str,Any]) -> Dict[str,Any]:
    newd = dict(data)
    newd.update(updates or {})
    return newd

def optimize_text(data: Dict[str,Any]) -> Dict[str,Any]:
    """
    Corrige bullets cortos sin añadir frases genéricas.
    - Mantiene el texto original del bullet.
    - Asegura capitalización inicial y punto final.
    - NO agrega 'cumpliendo estándares de calidad y plazos establecidos.'.
    """
    newd = dict(data)
    exp = []
    for e in (data.get("experiencia") or []):
        e2 = dict(e)
        logs = []
        for l in (e.get('logros') or []):
            t = _norm(l)
            if not t:
                continue
            # Solo normalizar formato (capitalización + punto final). No añadir frases genéricas.
            t_fmt = t[0].upper() + t[1:] if t else t
            if not t_fmt.endswith('.'):
                t_fmt += '.'
            logs.append(t_fmt)
        e2["logros"] = logs
        exp.append(e2)
    newd["experiencia"] = exp

    # Mantener el resto del comportamiento original
    perf = _norm(data.get("perfil",""))
    if 0 < len(perf) < 180:
        perf += " Me caracterizan la responsabilidad, la comunicación clara y la capacidad de adaptación."
    newd["perfil"] = perf or data.get("perfil","")
    return newd
