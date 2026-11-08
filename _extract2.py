import os, sys, docx
d = os.path.expanduser("~/Downloads")
doc = docx.Document(os.path.join(d, "Major Project - Synopsis report.docx"))
t = doc.tables[0]
print("style", t.style.name if t.style else None, "cols widths", [c.width for c in t.columns])
for ri in (0, 1, 2, 15):
    row = t.rows[ri]
    for c in row.cells:
        p = c.paragraphs[0]
        r = p.runs[0] if p.runs else None
        print(ri, repr(c.text[:30]), "align", p.alignment, "bold", r.bold if r else None, "size", r.font.size if r else None)
print(t._tbl.xml[:2500])
try:
    import win32com.client
    print("WIN32COM yes")
except Exception as e:
    print("WIN32COM no", e)
for p in ("C:/Program Files/Microsoft Office/root/Office16/WINWORD.EXE", "C:/Program Files (x86)/Microsoft Office/root/Office16/WINWORD.EXE"):
    print(p, os.path.exists(p))
