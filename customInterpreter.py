from typing import Optional

from interpreter import *
import re
import datetime


class TestPlus(CustomInterpreter):

    def __init__(self, status: Status = Status.UNFINISHED):
        super().__init__(status)
        self.result = -1

    def interpret_single_line(self, one_line: str):
        r = re.compile(r"result = (\d*).*")
        m = r.match(one_line)
        if m:
            self.status = Status.DONE
            self.result = m.group(1)

    def get_status(self) -> Status:
        return super().get_status()

    def values(self):
        return (self.result)


class EasyExtractException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class _EasyExtract(CustomInterpreter):

    def __init__(self):
        super().__init__(Status.UNFINISHED)
        self.variable_list = None

    def insert_trigger_line(self, one_line: str, variable_count: Optional[int] = None):
        if variable_count is not None:
            self.variable_list = one_line.split(maxsplit=variable_count - 1)
        else:
            self.variable_list = one_line.split()

    def extract_value(self, one_line, variable: Optional[str] = None, index: Optional[int] = None):
        values = one_line.split()

        if variable is not None:
            idx = self.variable_list.index(variable) - len(self.variable_list)
        elif index is not None:
            idx = index
        else:
            raise EasyExtractException("variable = None and index = None is not allowed.")

        try:
            return values[idx]
        except (ValueError, IndexError):
            raise EasyExtractException('output line is not formatted.')


class LinuxCpu(_EasyExtract):

    def __init__(self):
        super().__init__()
        self.max_value = -1
        self.temp_value = -1
        self.trigger_string = "us sy id wa st"
        self.trigger_appeared = False

    def interpret_single_line(self, one_line: str):
        if not self.trigger_appeared:
            if self.trigger_string in one_line:
                self.insert_trigger_line(one_line)
                self.trigger_appeared = True
        else:
            try:
                us = int(self.extract_value(one_line, 'us'))
                sy = int(self.extract_value(one_line, 'sy'))
                idle = int(self.extract_value(one_line, 'id'))
                if us + sy + idle == 100 and us + sy > self.max_value:
                    self.max_value = us + sy
                    self.status = Status.VALID_AND_CONTINUABLE
                if us + sy > self.temp_value:
                    self.temp_value = us + sy
                    self.status = Status.VALID_AND_CONTINUABLE
            except:
                pass

    def values(self):
        if self.max_value != -1:
            return f"{self.max_value}%"
        elif self.temp_value != -1:
            return f"{self.temp_value}%"
        else:
            return "ERROR"


class LinuxMem(_EasyExtract):
    def __init__(self):
        super().__init__()
        self.trigger_string = "buff/cache"
        self.trigger_appeared = False

    def interpret_single_line(self, one_line: str):
        if not self.trigger_appeared:
            if self.trigger_string in one_line:
                self.insert_trigger_line(one_line)
                self.trigger_appeared = True
        else:
            try:
                total = self.extract_value(one_line, 'total')
                used = self.extract_value(one_line, 'used')
                if total and used:
                    self.result = total, used
                    self.status = Status.DONE
            except:
                pass

    def values(self):
        try:
            total = float(self.result[0][:-1])
            used = float(self.result[1][:-1])
            if self.result[0][-1] != self.result[1][-1]:
                total *= 1000
            if (used / total) >= 0.8:
                status = '비정상'
            else:
                status = '정상'
            return self.result[0], self.result[1], status
        except:
            return self.result[0], self.result[1], "."


class LinuxFileSys(_EasyExtract):
    def __init__(self):
        super().__init__()
        self.trigger_string = "Mounted on"
        self.variable_count = 6
        self.trigger_appeared = False
        self.result = []

    def interpret_single_line(self, one_line: str):
        if not self.trigger_appeared:
            if self.trigger_string in one_line:
                self.insert_trigger_line(one_line, variable_count=self.variable_count)
                self.trigger_appeared = True
                self.status = Status.VALID_AND_CONTINUABLE
        else:
            try:
                per = self.extract_value(one_line, 'Use%')
                per = float(per.rstrip('%'))
                if per >= 80.0:
                    path = self.extract_value(one_line, 'Mounted on')
                    if path.find('NAS') == -1 and path.find('/home/tmax/app') == -1:
                        self.result.append(path)
            except:
                pass

    def values(self):
        if not self.result:
            return '-'
        else:
            path_list = ''
            for path in self.result:
                path_list += f"{path}\n"
            return path_list


class LinuxErrorLog(CustomInterpreter):
    def __init__(self):
        super().__init__(Status.VALID_AND_CONTINUABLE)
        today = datetime.datetime.today()
        self.ref_dates = [
            today,  # 오늘
            today - datetime.timedelta(days=1)  # 어제
        ]
        self.error = False

    def interpret_single_line(self, one_line: str):
        try:
            for refDate in self.ref_dates:
                words_in_line = one_line.split()
                try:
                    if words_in_line[0] == '[' + refDate.strftime('%a') and \
                            words_in_line[1] == refDate.strftime('%b') and \
                            words_in_line[2] == refDate.strftime('%d').lstrip('0') and \
                            words_in_line[4] == refDate.strftime('%Y') + ']':
                        self.status = Status.DONE
                        self.error = True
                except:
                    continue
        except:
            pass

    def values(self):
        if self.error:
            return "비정상"
        else:
            return "정상"


class UnixCpu(_EasyExtract):
    def __init__(self):
        super().__init__()
        self.trigger_string = "%idle"
        self.trigger_appeared = False
        self.result = -1

    def interpret_single_line(self, one_line: str):
        if not self.trigger_appeared:
            if self.trigger_string in one_line:
                self.insert_trigger_line(one_line)
                self.trigger_appeared = True
        else:
            try:
                if one_line.split()[0] == 'Average':
                    us = int(self.extract_value(one_line, '%usr'))
                    sy = int(self.extract_value(one_line, '%sys'))
                    self.result = us + sy
                    self.status = Status.DONE
            except:
                pass

    def values(self):
        return f"{self.result}%"


class UnixMem(_EasyExtract):
    def __init__(self):
        super().__init__()
        self.trigger_string = "mmode"
        self.trigger_appeared = False

    def interpret_single_line(self, one_line: str):
        if not self.trigger_appeared:
            if self.trigger_string in one_line:
                self.insert_trigger_line(one_line)
                self.trigger_appeared = True
        else:
            try:
                total = float(self.extract_value(one_line, 'size'))
                used_memory = total - float(self.extract_value(one_line, 'available'))
                if total is not None and used_memory is not None:
                    self.result = round(total, 1), round(used_memory, 1)
                    self.status = Status.DONE
            except:
                pass

    def values(self):
        try:
            if (self.result[1] / self.result[0]) >= 0.8:
                status = '비정상'
            else:
                status = '정상'
            return f"{self.result[0]}G", f"{self.result[1]}G", status
        except:
            return f"{self.result[0]}G", f"{self.result[1]}G", "."


class UnixFileSys(_EasyExtract):
    def __init__(self):
        super().__init__()
        self.trigger_string = "Mounted on"
        self.trigger_appeared = False
        self.result = []

    def interpret_single_line(self, one_line: str):
        if not self.trigger_appeared:
            if self.trigger_string in one_line:
                self.insert_trigger_line(one_line)
                self.trigger_appeared = True
                self.status = Status.VALID_AND_CONTINUABLE
        else:
            try:
                per = self.extract_value(one_line, index=-2)
                per = float(per.rstrip('%'))
                if per >= 80.0:
                    path = self.extract_value(one_line, index=-1)
                    if path.find('NAS') == -1:
                        self.result.append(path)
            except:
                pass

    def values(self):
        if not self.result:
            return '-'
        else:
            path_list = ''
            for path in self.result:
                path_list += f"{path}\n"
            return path_list


class UnixErrorLog(_EasyExtract):
    def __init__(self):
        super().__init__()
        self.trigger_string = "errpt"
        self.trigger_appeared = False
        self.error = False

    def interpret_single_line(self, one_line: str):
        if not self.trigger_appeared:
            if self.trigger_string in one_line:
                self.insert_trigger_line(one_line)
                self.trigger_appeared = True
                self.status = Status.VALID_AND_CONTINUABLE
        else:
            try:
                if one_line.find(':root] / >') != -1:
                    self.status = Status.DONE
                elif len(one_line) > 2:
                    self.error = True
                    self.status = Status.DONE
            except:
                pass

    def values(self):
        if self.error:
            return "비정상"
        else:
            return "정상"


class IiccmdbMem(LinuxMem):
    def __init__(self):
        super().__init__()
        self.total_unit = ''
        self.used_unit = ''

    def interpret_single_line(self, one_line: str):
        if not self.trigger_appeared:
            if self.trigger_string in one_line:
                self.insert_trigger_line(one_line)
                self.trigger_appeared = True
        else:
            try:
                total = int(self.extract_value(one_line, index=-6)[:-1])
                self.total_unit = self.extract_value(one_line, index=-6)[-1:]
                used = total - int(self.extract_value(one_line, index=-4)[:-1])
                self.used_unit = self.extract_value(one_line, index=-4)[-1:]
                if total is not None and used is not None:
                    self.result = total, used
                    self.status = Status.DONE
            except:
                pass

    def values(self):
        try:
            total = self.result[0]
            used = self.result[1]
            if self.total_unit != self.used_unit:
                total *= 1000
            if (used / total) >= 0.8:
                status = '비정상'
            else:
                status = '정상'
            return f"{self.result[0]}{self.total_unit}", f"{self.result[1]}{self.used_unit}", status
        except:
            return f"{self.result[0]}{self.total_unit}", f"{self.result[1]}{self.used_unit}", "."


class WebDb(CustomInterpreter):
    def __init__(self):
        super().__init__()
        self.line_count = 0

    def interpret_single_line(self, one_line: str):
        try:
            if one_line.find('ps -ef | grep webtob') != -1:
                pass
            elif len(one_line.split()) >= 8:
                self.line_count += 1
        except:
            pass

    def values(self):
        if self.line_count >= 4:
            return "WEB ( O )"
        else:
            return "WEB ( X )"


class WasDb(CustomInterpreter):
    def __init__(self):
        super().__init__()
        self.line_count = 0

    def interpret_single_line(self, one_line: str):
        try:
            if one_line.find('ps -ef | grep jeus') != -1:
                pass
            elif len(one_line.split()) >= 8:
                self.line_count += 1
        except:
            pass

    def values(self):
        if self.line_count >= 3:
            return "WAS ( O )"
        else:
            return "WAS ( X )"


class TiberoDb(CustomInterpreter):
    def __init__(self):
        super().__init__()
        self.line_count = 0

    def interpret_single_line(self, one_line: str):
        try:
            if one_line.find('ps -ef | grep tibero') != -1:
                pass
            elif one_line.find('tibero') != -1:
                self.status = Status.DONE
        except:
            pass

    def values(self):
        if self.status == Status.DONE:
            return "Tibero DB ( O )"
        else:
            return "Tibero DB ( X )"


class MySQLDb(CustomInterpreter):
    def __init__(self):
        super().__init__()
        self.line_count = 0

    def interpret_single_line(self, one_line: str):
        try:
            if one_line.find('running') != -1:
                self.status = Status.DONE
        except:
            pass

    def values(self):
        if self.status == Status.DONE:
            return "MySQL DB ( O )"
        else:
            return "MySQL DB ( X )"


class GoldiroxDb(CustomInterpreter):
    def __init__(self):
        super().__init__()
        self.line_count = 0

    def interpret_single_line(self, one_line: str):
        try:
            if one_line.find('Listener is running.') != -1:
                self.status = Status.DONE
        except:
            pass

    def values(self):
        if self.status == Status.DONE:
            return "골디락스 DB ( O )"
        else:
            return "골디락스 DB ( X )"


class NotRelated(CustomInterpreter):
    def __init__(self):
        super().__init__()

    def interpret_single_line(self, one_line: str):
        self.status = Status.DONE

    def values(self):
        return "해당사항 없음"


class Pass(CustomInterpreter):
    def __init__(self):
        super().__init__()

    def interpret_single_line(self, one_line: str):
        self.status = Status.PASS
