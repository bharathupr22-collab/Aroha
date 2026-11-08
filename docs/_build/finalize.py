"""Removes the 'update fields on open' flag after Word has refreshed the TOC page numbers.

Usage: python finalize.py <file.docx> [<file.docx> ...]
"""
import sys

import docx
from docx.oxml.ns import qn

for path in sys.argv[1:]:
    d = docx.Document(path)
    settings = d.settings.element
    removed = 0
    for el in settings.findall(qn("w:updateFields")):
        settings.remove(el)
        removed += 1
    d.save(path)
    print(path, "- removed updateFields flags:", removed)
