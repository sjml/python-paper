import enum

class Format(str, enum.Enum):
    docx = "docx"
    docx_pdf = "docx+pdf"
    json = "json"
