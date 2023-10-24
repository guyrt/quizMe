from typing import Literal

DocFormat = Literal['pdf', 'docx', 'zip']


def docformat_to_contenttype(data_type : DocFormat):
    if data_type == 'pdf':
        return 'application/pdf'
    elif data_type == 'docx':
        return "application/msword"
    elif data_type == 'zip':
        return 'application/zip'
    else:
        raise ValueError(f"Unexpected data type {data_type}")
