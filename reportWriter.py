import sys
import pandas as pd
from styleframe import StyleFrame
from styleframe import Styler

if sys.version_info >= (3, 3):
    import collections.abc as collections_abc
else:
    import collections as collections_abc


class ReportWriter:
    def __init__(self, size, file_path, encoding, header):
        self.encoding = encoding
        self.file_path = file_path
        self.data_frame = pd.DataFrame(index=range(size), columns=header)
        self.column_count = len(header)
        self.cur_idx = dict()
        self.rows = [l for l in range(self.column_count)]

    def save(self):
        stf = StyleFrame(self.data_frame, styler_obj=Styler(font='맑은 고딕', font_size=11))
        stf.to_excel(self.file_path, index=False).save()

    def insert(self, index: int, data):
        if not (index in self.cur_idx):
            self.cur_idx[index] = 0

        if data is None:
            none_value = "None"
            self.data_frame.iloc[index, self.cur_idx[index]] = none_value
            self.cur_idx[index] += 1
        elif type(data) is str:  # str is also iterable
            self.data_frame.iloc[index, self.cur_idx[index]] = data
            self.cur_idx[index] += 1
        elif isinstance(data, collections_abc.Iterable):
            for element in data:
                self.data_frame.iloc[index, self.cur_idx[index]] = element
                self.cur_idx[index] += 1
        else:
            self.data_frame.iloc[index, self.cur_idx[index]] = data
            self.cur_idx[index] += 1
