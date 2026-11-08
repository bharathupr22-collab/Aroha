import sys, os, docx
d = os.path.expanduser("~/Downloads")
f = sys.argv[1]
mode = sys.argv[2]
doc = docx.Document(os.path.join(d, f))
s = doc.sections[0]
print("PAGE", s.page_width.cm, s.page_height.cm, "margins", s.left_margin.cm, s.right_margin.cm, s.top_margin.cm, s.bottom_margin.cm)
st = doc.styles["Normal"]
print("NORMAL FONT", st.font.name, st.font.size)
if mode == "outline":
    for p in doc.paragraphs:
        t = p.text.strip()
        if not t:
            continue
        if p.style.name.lower().startswith("heading") or (len(t) < 80 and p.runs and p.runs[0].bold):
            r = p.runs[0] if p.runs else None
            print(f"[{p.style.name}] {t[:90]} | font={r.font.name if r else None} size={r.font.size.pt if r and r.font.size else None}")
    print("TABLES", len(doc.tables))
else:
    start, end = int(sys.argv[3]), int(sys.argv[4])
    ps = [p.text for p in doc.paragraphs if p.text.strip()]
    print("\n".join(ps[start:end]))
