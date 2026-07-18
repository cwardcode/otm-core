# -*- coding: utf-8 -*-


import csv
import io


def _clean_string(s):
    if isinstance(s, bytes):
        s = s.decode('utf-8')
    return s.strip()


def clean_row_data(h):
    h2 = {}
    for (k, v) in h.items():
        k = clean_field_name(k)
        if k != 'ignore':
            if isinstance(v, (str, bytes)):
                v = _clean_string(v)

            h2[k] = v

    return h2


def clean_field_name(name):
    return name.lower().strip()


def _as_utf8(f):
    if hasattr(f, 'read') and not isinstance(f, io.TextIOBase):
        # We need a text stream for Python 3 csv module
        # but django's uploaded files might be byte streams
        if hasattr(f, 'file'):
            f = getattr(f, 'file')
        if not isinstance(f, io.TextIOBase):
            return io.TextIOWrapper(f, encoding='utf-8', errors='replace')
    return f


def _guess_dialect_and_reset_read_pointer(f):
    wrapped = _as_utf8(f)
    sample = wrapped.read(4096)
    if not sample:
        raise ValueError("File is empty")
    dialect = csv.Sniffer().sniff(sample, delimiters=',\t')
    f.seek(0)
    return dialect


def utf8_file_to_csv_dictreader(f):
    dialect = _guess_dialect_and_reset_read_pointer(f)
    dialect.doublequote = True
    return csv.DictReader(_as_utf8(f), dialect=dialect)
