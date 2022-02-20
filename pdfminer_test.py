'''
### Read in PDF complicated text using Pdfminer
'''

from io import StringIO
from typing import List

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage


def pdf_text_reader(pdf_file_name, pages=None) -> str:
    if pages:
        page_nums = set(pages)
    else:
        page_nums = set()

    ## 1) Initiate the Pdf text converter and interpreter
    textOutput = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, textOutput, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    ## 2) Extract text from file using the interpreter
    infile = open(pdf_file_name, 'rb')
    for page in PDFPage.get_pages(infile, page_nums, caching=True, check_extractable=True):
        interpreter.process_page(page)
    infile.close()

    ## 3) Extract the paragraphs and close the connections
    paras = textOutput.getvalue()
    converter.close()
    textOutput.close()
    return paras


def get_text_lines(file_name, pages) -> List[str]:
    paras = pdf_text_reader(file_name, pages)
    lines = [i for i in paras.split('\n') if i]
    return lines


if __name__ == '__main__':
    file_path = '/home/pavan/Downloads/10,000+ GK MCQs Ebook.pdf'
    out = pdf_text_reader(file_path, pages=range(2, 5))
    print([i for i in out.split('\n') if i])
