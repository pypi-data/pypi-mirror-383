import logging


def quiet_docling(level=logging.ERROR):
    for name in (
        "docling",
        "docling.backend.html_backend",
        "pdfminer",
        "pikepdf",
        "fitz",
        "PIL",
        "unstructured",
    ):
        lg = logging.getLogger(name)
        lg.setLevel(level)
        lg.propagate = False
        # Optional: nuke any pre-attached handlers
        if lg.handlers:
            lg.handlers.clear()
