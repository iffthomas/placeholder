def read_pdf(file_path):
    """Reads the content of a PDF file and returns it as a string
    Parameters:
    ------------
    file_path: str
        path to the PDF file to be read
    Returns:
    ------------
    text: str
        content of the PDF file
    """ 
       
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        num_pages = pdf_reader.numPages

        text = ''
        for page_num in range(num_pages):
            page = pdf_reader.getPage(page_num)
            text += page.extractText()

    return text

