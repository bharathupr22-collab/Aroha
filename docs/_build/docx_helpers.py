"""Shared python-docx helpers used by build_synopsis.py and build_srs.py."""
import copy
import re

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

FONT = "Times New Roman"
ALIGN = {
    "left": WD_ALIGN_PARAGRAPH.LEFT,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
    "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
    "right": WD_ALIGN_PARAGRAPH.RIGHT,
}

_bookmark_id = [1000]


def style_run(run, size=12, bold=None, italic=None, color=None):
    run.font.name = FONT
    rpr = run._r.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), FONT)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color:
        from docx.shared import RGBColor

        run.font.color.rgb = RGBColor.from_string(color)


def add_marked_runs(paragraph, text, size=12, bold=False, italic=False):
    """Adds runs to a paragraph; segments wrapped in ** ** are bold, segments in __ __ italic."""
    parts = re.split(r"(\*\*.+?\*\*|__.+?__|`.+?`)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("`") and part.endswith("`") and len(part) > 2:
            r = paragraph.add_run(part[1:-1])
            style_run(r, max(size - 1, 8), bold, italic)
            r.font.name = "Courier New"
            rpr = r._r.get_or_add_rPr()
            for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
                rpr.find(qn("w:rFonts")).set(qn(attr), "Courier New")
        elif part.startswith("**") and part.endswith("**"):
            r = paragraph.add_run(part[2:-2])
            style_run(r, size, True, italic)
        elif part.startswith("__") and part.endswith("__"):
            r = paragraph.add_run(part[2:-2])
            style_run(r, size, bold, True)
        else:
            r = paragraph.add_run(part)
            style_run(r, size, bold, italic)


def add_field(paragraph, instr, cached="", size=12, bold=False):
    def fld(kind):
        r = paragraph.add_run()
        el = OxmlElement("w:fldChar")
        el.set(qn("w:fldCharType"), kind)
        r._r.append(el)
        style_run(r, size, bold)
        return r

    fld("begin")
    r = paragraph.add_run()
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = f" {instr} "
    r._r.append(it)
    style_run(r, size, bold)
    fld("separate")
    r = paragraph.add_run(cached)
    style_run(r, size, bold)
    fld("end")


def add_bookmark(paragraph, name):
    _bookmark_id[0] += 1
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(_bookmark_id[0]))
    start.set(qn("w:name"), name)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(_bookmark_id[0]))
    p = paragraph._p
    ppr = p.find(qn("w:pPr"))
    idx = list(p).index(ppr) + 1 if ppr is not None else 0
    p.insert(idx, start)
    p.append(end)


def set_cell_shading(cell, fill):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcpr.append(shd)


def set_cell_margins(table, top=40, bottom=40, left=80, right=80):
    tblpr = table._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for side, val in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tblpr.append(mar)


def set_table_borders(table):
    tblpr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "404040")
        borders.append(el)
    tblpr.append(borders)


def trim_body(doc, keep_count):
    """Remove every body element after the first `keep_count` ones (keeps the final sectPr)."""
    body = doc.element.body
    for el in list(body)[keep_count:]:
        if el.tag == qn("w:sectPr"):
            continue
        body.remove(el)


def set_paragraph_text(paragraph, text):
    """Replace the text of a paragraph while keeping the formatting of its first run."""
    runs = paragraph.runs
    if not runs:
        paragraph.add_run(text)
        return
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


def enable_update_fields_on_open(doc):
    settings = doc.settings.element
    for el in settings.findall(qn("w:updateFields")):
        settings.remove(el)
    uf = OxmlElement("w:updateFields")
    uf.set(qn("w:val"), "true")
    settings.append(uf)


class Builder:
    def __init__(self, doc, line_spacing=1.5, base_size=12, toc_prefix="_Toc"):
        self.doc = doc
        self.ls = line_spacing
        self.size = base_size
        self.toc_prefix = toc_prefix
        self.headings = []  # (key, text, level)
        self.fig_no = 0
        self.tab_no = 0

    # ----------------------------------------------------------------- text
    def para(self, text="", align="justify", bold=False, italic=False, size=None, after=6, before=0,
             keep_next=False, left_cm=None, first_cm=None, line=None):
        p = self.doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_after = Pt(after)
        pf.space_before = Pt(before)
        pf.line_spacing = line if line else self.ls
        pf.keep_with_next = keep_next
        if left_cm is not None:
            pf.left_indent = Cm(left_cm)
        if first_cm is not None:
            pf.first_line_indent = Cm(first_cm)
        p.alignment = ALIGN[align]
        if text:
            add_marked_runs(p, text, size or self.size, bold, italic)
        return p

    def heading(self, text, level=1, key=None, center=False, page_break=False):
        size = {1: 14, 2: 12, 3: 12}[level]
        p = self.doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_before = Pt(12 if level == 1 else 8)
        pf.space_after = Pt(6)
        pf.keep_with_next = True
        pf.line_spacing = 1.15
        if page_break:
            pf.page_break_before = True
        p.alignment = ALIGN["center" if center else "left"]
        r = p.add_run(text)
        style_run(r, size, True, italic=(level == 3))
        ppr = p._p.get_or_add_pPr()
        ol = OxmlElement("w:outlineLvl")
        ol.set(qn("w:val"), str(level - 1))
        ppr.append(ol)
        if key:
            add_bookmark(p, f"{self.toc_prefix}_{key}")
            self.headings.append((key, text, level))
        return p

    def bullets(self, items, marker="\u2022", size=None, after=3, left_cm=1.0, hang_cm=0.6, align="justify"):
        for i, it in enumerate(items, 1):
            p = self.para("", align=align, after=after, left_cm=left_cm, first_cm=-hang_cm)
            p.paragraph_format.tab_stops.add_tab_stop(Cm(left_cm))
            mk = marker if marker else f"{i}."
            add_marked_runs(p, f"{mk}\t{it}", size or self.size)
        self.doc.paragraphs[-1].paragraph_format.space_after = Pt(8)

    def numbered(self, items, **kw):
        self.bullets(items, marker=None, **kw)

    def page_break(self):
        from docx.enum.text import WD_BREAK

        p = self.doc.add_paragraph()
        p.add_run().add_break(WD_BREAK.PAGE)
        p.paragraph_format.space_after = Pt(0)

    # ----------------------------------------------------------------- figures
    def figure(self, path, width_cm, caption):
        self.fig_no += 1
        if self.doc.paragraphs:
            self.doc.paragraphs[-1].paragraph_format.keep_with_next = True
            self.doc.paragraphs[-1].paragraph_format.keep_together = True
        p = self.doc.add_paragraph()
        p.alignment = ALIGN["center"]
        p.paragraph_format.keep_with_next = True
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.0
        p.add_run().add_picture(path, width=Cm(width_cm))
        c = self.para(f"Figure {caption[0]}: {caption[1]}", align="center", italic=True, size=10.5, after=10, line=1.15)
        return c

    # ----------------------------------------------------------------- tables
    def table(self, headers, rows, widths_cm, size=10.5, header_fill="D9E8E5", center_cols=(), caption=None,
              bold_first_col=False):
        if self.doc.paragraphs:
            self.doc.paragraphs[-1].paragraph_format.keep_with_next = True
            self.doc.paragraphs[-1].paragraph_format.keep_together = True
        if caption:
            self.para(f"Table {caption[0]}: {caption[1]}", align="left", bold=True, size=10.5, after=3, keep_next=True,
                      line=1.15)
        t = self.doc.add_table(rows=1 + len(rows), cols=len(headers))
        t.autofit = False
        set_table_borders(t)
        set_cell_margins(t)
        tblpr = t._tbl.tblPr
        lay = OxmlElement("w:tblLayout")
        lay.set(qn("w:type"), "fixed")
        tblpr.append(lay)
        all_rows = [headers] + rows
        for ri, row in enumerate(all_rows):
            tr = t.rows[ri]
            trpr = tr._tr.get_or_add_trPr()
            cs = OxmlElement("w:cantSplit")
            trpr.append(cs)
            if ri == 0:
                th = OxmlElement("w:tblHeader")
                trpr.append(th)
            for ci, val in enumerate(row):
                cell = tr.cells[ci]
                cell.width = Cm(widths_cm[ci])
                if ri == 0:
                    set_cell_shading(cell, header_fill)
                self.fill_cell(cell, str(val), size, bold=(ri == 0) or (bold_first_col and ci == 0),
                               center=(ci in center_cols) or ri == 0 and ci in center_cols)
        # spacer after table
        sp = self.para("", after=6, line=1.0)
        return t

    @staticmethod
    def fill_cell(cell, text, size=10.5, bold=False, center=False):
        lines = text.split("\n")
        first = True
        for line in lines:
            p = cell.paragraphs[0] if first else cell.add_paragraph()
            first = False
            pf = p.paragraph_format
            pf.space_after = Pt(1)
            pf.space_before = Pt(1)
            pf.line_spacing = 1.1
            p.alignment = ALIGN["center" if center else "left"]
            add_marked_runs(p, line, size, bold)
