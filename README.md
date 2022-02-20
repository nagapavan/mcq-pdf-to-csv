Code to read MCQs ebook PDF to CSV files.

Code is customized to specific PDF file. May need to update as required for other MCQ files

## How to execute

Update `file_name` - absolute path and `page_ranges_map` - from index/TOC page as required from `process_texdata.py`
file

```python
if __name__ == '__main__':
    source_file = './10,000+ GK MCQs Ebook.pdf'
    # process_test_file(source_file)
    page_ranges_map = dict({'Physics': (2, 218),
                            'Chemistry': (218, 435),
                            'Biology': (435, 735),
                            'History': (735, 997),
                            'Geography': (997, 1282),
                            'Economics': (1282, 1416),
                            'Indian_Polity': (1416, 1726),
                            'Railway': (1726, 1750)})
    process_pdf_file_extended(file_path=source_file, skip_pages=2, page_map=page_ranges_map)
```

Execute from `bash` with following command:

```shell
python process_texdata.py
```
