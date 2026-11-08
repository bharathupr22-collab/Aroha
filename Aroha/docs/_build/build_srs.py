"""Builds docs/AROHA_SRS.docx from the college SRS template.

Run (from docs/_build):  python build_srs.py
"""
import copy
import os
import shutil

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt

import srs_content as C
from docx_helpers import (Builder, add_field, add_marked_runs, enable_update_fields_on_open, set_paragraph_text,
                          style_run, trim_body)

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
TEMPLATE = os.path.expanduser("~/Downloads/Major_Project_SRS_AI_Hallucination_Detection .docx")
OUT = os.path.join(HERE, "..", "AROHA_SRS.docx")

STUDENT, USN = "KARTHIK PAI", "(4MT25MC041)"
GUIDE, DESIG = "Dr. Chandrakantha T S", "Assistant Professor"

SECTIONS = [
    ("s1", "Introduction"),
    ("s2", "Overall Description"),
    ("s3", "System Features and Functional Requirements"),
    ("s4", "External Interface Requirements"),
    ("s5", "Non-Functional Requirements"),
    ("s6", "System Models and Diagrams"),
    ("s7", "Data Requirements and Database Design"),
    ("s8", "System Constraints and Limitations"),
    ("s9", "Testing and Acceptance Criteria"),
    ("s10", "Requirement Traceability Matrix"),
    ("s11", "References"),
]


def rebuild_toc(doc):
    """Reuse the template's TOC paragraphs (they carry the dotted tab leader) for 11 entries."""
    body = doc.element.body
    toc_els = list(body)[14:24]  # after the subtitle paragraph was inserted on the cover
    clone = copy.deepcopy(toc_els[-1])
    toc_els[-1].addnext(clone)
    toc_els.append(clone)
    for el, (key, title) in zip(toc_els, SECTIONS):
        p = docx.text.paragraph.Paragraph(el, doc._body)
        for child in list(el):
            if child.tag != qn("w:pPr"):
                el.remove(child)
        n = key[1:]
        r = p.add_run(f"{n}.  {title}\t")
        style_run(r, 12)
        add_field(p, f"PAGEREF _Toc_{key} \\h", "1", size=12)


def main():
    work = os.path.join(HERE, "_srs_template_copy.docx")
    shutil.copy(TEMPLATE, work)
    doc = docx.Document(work)
    paras = doc.paragraphs

    # cover page
    set_paragraph_text(paras[3], C.TITLE)
    paras[3].alignment = WD_ALIGN_PARAGRAPH.CENTER
    paras[3].runs[0].font.size = Pt(18)
    paras[3].runs[0].bold = True
    set_paragraph_text(paras[6], STUDENT)
    paras[6].alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_text(paras[7], USN)
    set_paragraph_text(paras[9], GUIDE)
    set_paragraph_text(paras[10], DESIG)
    # subtitle under the title
    sub = copy.deepcopy(paras[3]._p)
    paras[3]._p.addnext(sub)
    sp = docx.text.paragraph.Paragraph(sub, paras[3]._parent)
    set_paragraph_text(sp, C.SUBTITLE)
    sp.runs[0].font.size = Pt(13)
    sp.runs[0].bold = False

    rebuild_toc(doc)
    trim_body(doc, 26)  # cover (incl. subtitle) + TOC heading + 11 TOC entries + section break

    b = Builder(doc, line_spacing=1.3, base_size=12, toc_prefix="_Toc")

    def H1(key, text, page_break=False):
        n = key[1:]
        b.heading(f"{n}.  {text}", 1, key=key, page_break=page_break)

    def H2(num, text):
        b.heading(f"{num}  {text}", 2)

    # ----------------------------------------------------------------- 1
    H1("s1", "Introduction", page_break=False)
    H2("1.1", "Purpose")
    b.para(C.PURPOSE)
    H2("1.2", "Scope")
    for t in C.SCOPE:
        b.para(t)
    H2("1.3", "Definitions, Acronyms and Abbreviations")
    b.table(["Term", "Meaning"], [list(r) for r in C.DEFINITIONS], [4.2, 12.8], size=10.5, bold_first_col=True)
    H2("1.4", "Overview of the Document")
    b.para(C.OVERVIEW)

    # ----------------------------------------------------------------- 2
    H1("s2", "Overall Description")
    H2("2.1", "Product Perspective")
    for t in C.PERSPECTIVE:
        b.para(t)
    H2("2.2", "Product Functions")
    b.bullets(C.FUNCTIONS)
    H2("2.3", "User Classes and Characteristics")
    b.table(["User Class", "Description", "Technical Skill"], [list(r) for r in C.USER_CLASSES],
            [3.8, 10.2, 3.0], size=10.5, bold_first_col=True)
    H2("2.4", "Operating Environment")
    b.bullets(C.ENVIRONMENT)
    H2("2.5", "Assumptions and Dependencies")
    b.bullets(C.ASSUMPTIONS)

    # ----------------------------------------------------------------- 3
    H1("s3", "System Features and Functional Requirements")
    b.para("The system is divided into the features below. Each feature has a short description and a table of "
           "numbered requirements. Priority shows how important a requirement is for the project: High "
           "requirements are essential, Medium requirements are important, and Low requirements are desirable.")
    fr_no = 0
    fr_ranges = {}
    for i, sec in enumerate(C.FR_SECTIONS, 1):
        H2(f"3.{i}", sec["title"])
        b.para(sec["desc"])
        rows = []
        first = fr_no + 1
        for text, pr in sec["reqs"]:
            fr_no += 1
            rows.append([f"FR-{fr_no:02d}", text, pr])
        fr_ranges[sec["key"]] = (first, fr_no)
        b.table(["ID", "Requirement", "Priority"], rows, [2.0, 12.5, 2.5], size=10.5, center_cols=(0, 2))

    # ----------------------------------------------------------------- 4
    H1("s4", "External Interface Requirements")
    H2("4.1", "User Interface")
    b.bullets(C.UI_REQS)
    H2("4.2", "Hardware Interfaces")
    b.table(["Component", "Minimum Requirement", "Recommended"], [list(r) for r in C.HARDWARE], [3.4, 6.8, 6.8],
            size=10.5, bold_first_col=True)
    H2("4.3", "Software Interfaces")
    b.table(["Software / Service", "Purpose"], [list(r) for r in C.SOFTWARE], [6.0, 11.0], size=10.5,
            bold_first_col=True)
    H2("4.4", "Communication Interfaces")
    b.bullets(C.COMMS)
    H2("4.5", "REST API Summary")
    b.para("The suggested endpoints below form the interface between the client and the backend. Names and methods "
           "may be adjusted consistently during design.")
    b.table(["Group", "Endpoints"], [list(r) for r in C.API_SUMMARY], [3.4, 13.6], size=10, bold_first_col=True)

    # ----------------------------------------------------------------- 5
    H1("s5", "Non-Functional Requirements")
    rows = [[f"NFR-{i:02d}", cat, text] for i, (cat, text) in enumerate(C.NFRS, 1)]
    b.table(["ID", "Category", "Requirement"], rows, [2.2, 3.2, 11.6], size=10.5, center_cols=(0,))

    # ----------------------------------------------------------------- 6
    H1("s6", "System Models and Diagrams")
    H2("6.1", "Data Flow Diagram \u2013 Level 0 (Context Diagram)")
    b.para(C.DIAGRAM_TEXT["dfd0"])
    b.figure(os.path.join(IMG, "dfd_level0.png"), 14.0, ("6.1", "DFD Level 0: context diagram of AROHA"))
    H2("6.2", "Data Flow Diagram \u2013 Level 1 (Process Diagram)")
    b.para(C.DIAGRAM_TEXT["dfd1"])
    b.figure(os.path.join(IMG, "dfd_level1.png"), 13.0, ("6.2", "DFD Level 1: main processes and data stores"))
    H2("6.3", "System Architecture")
    b.para(C.DIAGRAM_TEXT["arch"])
    b.figure(os.path.join(IMG, "architecture.png"), 13.0, ("6.3", "Layered system architecture"))
    H2("6.4", "Use Case Diagram")
    b.para(C.DIAGRAM_TEXT["usecase"])
    b.figure(os.path.join(IMG, "usecase.png"), 13.0, ("6.4", "Use case diagram"))

    # ----------------------------------------------------------------- 7
    H1("s7", "Data Requirements and Database Design")
    H2("7.1", "Data Requirements")
    b.bullets(C.DATA_REQS)
    H2("7.2", "Database Design")
    b.para("The database is relational (PostgreSQL) and normalised. Every user-owned table references `users`, and "
           "analytics history references the connected account. News articles are shared and independent of users. "
           "Figure 7.1 shows the entities and their one-to-many relationships.")
    b.figure(os.path.join(IMG, "er_diagram.png"), 14.5, ("7.1", "Entity-relationship diagram of AROHA"))
    H2("7.3", "Table Structure")
    b.table(["Table", "Fields"], [list(r) for r in C.TABLES], [3.8, 13.2], size=10, bold_first_col=True)
    b.para("**Constraints, indexes and migrations:**", align="left", after=2, keep_next=True)
    b.bullets(C.DB_NOTES)

    # ----------------------------------------------------------------- 8
    H1("s8", "System Constraints and Limitations")
    H2("8.1", "Constraints")
    b.bullets(C.CONSTRAINTS)
    H2("8.2", "Limitations")
    b.bullets(C.LIMITATIONS)

    # ----------------------------------------------------------------- 9
    H1("s9", "Testing and Acceptance Criteria")
    H2("9.1", "Testing Approach")
    b.bullets(C.TEST_APPROACH)
    H2("9.2", "Test Cases")
    b.para("The table lists the planned test cases and the expected results. Actual results and pass/fail status "
           "will be recorded in the test report when each module is tested; no result is claimed here.")
    tc_ids = {}
    rows = []
    for i, (key, case, expected) in enumerate(C.TESTS, 1):
        tid = f"TC-{i:02d}"
        tc_ids.setdefault(key, []).append(tid)
        rows.append([tid, case, expected])
    b.table(["ID", "Test Case", "Expected Result"], rows, [1.8, 7.4, 7.8], size=10, center_cols=(0,))
    H2("9.3", "Acceptance Criteria")
    b.bullets(C.ACCEPTANCE)

    # ----------------------------------------------------------------- 10
    H1("s10", "Requirement Traceability Matrix")
    b.para("The matrix links each objective to the functional requirements that realise it, the module that "
           "implements it and the test cases that verify it.")

    def rng(ids, prefix):
        return ids

    rows = []
    for obj, fr_keys, module, tc_keys in C.RTM:
        frs = []
        for k in fr_keys:
            a, z = fr_ranges[k]
            frs.append(f"FR-{a:02d} to FR-{z:02d}")
        tcs = []
        for k in tc_keys:
            ids = tc_ids[k]
            tcs.append(f"{ids[0]} to {ids[-1]}" if len(ids) > 1 else ids[0])
        rows.append([obj, ", ".join(frs), module, ", ".join(tcs)])
    b.table(["Objective", "Requirements", "Module", "Test Cases"], rows, [6.4, 3.6, 3.8, 3.2], size=10)
    b.para("Non-functional requirements NFR-01 to NFR-%02d apply to all modules and are verified through the "
           "performance, security and usability tests." % len(C.NFRS), after=6)

    # ----------------------------------------------------------------- 11
    H1("s11", "References")
    for r in C.REFERENCES:
        p = b.para("", align="left", after=4, left_cm=1.0, first_cm=-1.0, line=1.15)
        add_marked_runs(p, r, 11)

    enable_update_fields_on_open(doc)
    out = os.path.abspath(OUT)
    doc.save(out)
    os.remove(work)
    print("saved", out, "| functional requirements:", fr_no, "| test cases:", len(C.TESTS), "| NFRs:", len(C.NFRS))


if __name__ == "__main__":
    main()
