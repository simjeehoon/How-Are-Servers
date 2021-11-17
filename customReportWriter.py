from styleframe import StyleFrame
from styleframe import Styler

import reportWriter

header = ["서버명", "hostname", "cpu", "total", "used", "상태", "파일시스템", "에러로그", "DB 상태확인"]


class ReportWriter(reportWriter.ReportWriter):
    def __init__(self, size, file_path, encoding):
        super().__init__(size, file_path, encoding, header)

    def save(self):
        stf = StyleFrame(self.data_frame, styler_obj=Styler(font='맑은 고딕', font_size=11))
        size = self.data_frame.shape
        for c in range(size[1]):
            max_len = len(str(self.data_frame.columns[c]).encode(self.encoding))
            for r in range(size[0]):
                length = len(str(self.data_frame.iat[r, c]).encode(self.encoding))
                if max_len < length:
                    max_len = length
            stf.set_column_width(columns=[self.data_frame.columns[c]], width=max_len + 3)
        stf.apply_column_style(cols_to_style=self.data_frame.columns[size[1] - 1],
                               styler_obj=Styler(font='맑은 고딕', font_size=10))
        stf.apply_column_style(cols_to_style=self.data_frame.columns[0:2],
                               styler_obj=Styler(font='맑은 고딕', font_size=10, bg_color="#DDDDDD"))
        stf.apply_headers_style(styler_obj=Styler(font='맑은 고딕', font_size=11, bg_color="#BBBBFF"))
        stf.to_excel(self.file_path, index=False).save()


if __name__ == '__main__':
    interpreter_report_file_name = 'result_report.xlsx'
    e = ReportWriter(5, interpreter_report_file_name, 'utf-8')
    e.insert(0, "a")
    e.insert(0, "b")
    e.save()
