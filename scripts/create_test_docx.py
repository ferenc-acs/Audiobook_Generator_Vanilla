from docx import Document

if __name__ == "__main__":
    doc = Document()
    doc.add_paragraph('Sample audiobook text for integration testing')
    doc.save('test.docx')
    print("Test document created successfully")