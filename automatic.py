import json
import sys
from typing import Optional
import pandas as pd
from abc import *
import sshConnector
import os
import threading
import interpreter
import logManager as log
from typing import List
from functools import cmp_to_key
import reportWriter

thread_lock = threading.Lock()

result_directory_path = './result'
print_directory_path = result_directory_path + '/print'
config_file_path = './config.json'
server_info_list_file_name = "serverInfoList"
command_directory_path = "./cmdset"
report_file_path = result_directory_path + '/result_report.xlsx'
interpreter_py_path = 'customInterpreter.py'
reportwriter_py_path = "customReportWriter.py"

server_info_list_column = ['name', 'hostname', 'id', 'password', 'port', 'command_file', 'login_term']
server_info_list_types = ['str', 'str', 'str', 'str', 'int', 'str', 'float']
command_list_column = ['command', 'stdout_term', 'to_do_keyword', 'encoding']
command_list_types = ['str', 'float', 'str', 'str']


class InitException(Exception):

    def __init__(self, *args) -> None:
        super().__init__(*args)


class Config:
    def __init__(self):
        self.default_port = None
        self.default_login_term = None
        self.default_stdout_term = None
        self.default_encoding = None
        self.ssh_timeout = None
        self.maximum_number_of_recollections = None
        self.recollection_delay_time = None
        self.info_list_extension = None
        self.debug_mode = False
        self.file_instead_hostname = False
        self.thread_count = 0
        self.forbidden_word_list = []

    def __str__(self):
        out = ''
        for key, values in self.__dict__.items():
            out += f"{key}:{values}, "
        out = f"{out.rstrip(', ')}"
        out = "{" + out + "}"
        return out

    @staticmethod
    def get_default():
        default_config = Config()
        default_config.default_port = 22
        default_config.default_login_term = 0.5
        default_config.default_stdout_term = 1
        default_config.default_encoding = "utf-8"
        default_config.ssh_timeout = 5
        default_config.maximum_number_of_recollections = 3
        default_config.recollection_delay_time = 1
        default_config.info_list_extension = ".xlsx"
        default_config.debug_mode = False
        default_config.file_instead_hostname = False
        default_config.thread_count = 8
        default_config.forbidden_word_list = ['if command includes the word in forbidden word list',
                                              'the command won\'t be executed.']

        return default_config

    def available(self):
        try:
            if not 0 < int(self.default_port) < 65536:
                raise InitException("port_error")
            if not 0.0 <= float(self.default_login_term):
                raise InitException("login_term_error")
            if not 0.0 <= float(self.default_stdout_term):
                raise InitException("stdout_term_error")
            try:
                "abc".encode(self.default_encoding)
            except:
                raise InitException("default_encoding_error")
            if not 0.0 <= float(self.ssh_timeout):
                raise InitException("ssh_timeout_error")
            if not 0 <= int(self.maximum_number_of_recollections):
                raise InitException("maximum_number_of_recollections_error")
            if not 0.0 <= float(self.recollection_delay_time):
                raise InitException("recollection_delay_time_error")
            if not (self.info_list_extension == ".xlsx" or self.info_list_extension == ".csv"):
                raise InitException("extension_error")
            if type(self.debug_mode) != bool:
                raise InitException("debug_mode_setting_error")
            if type(self.file_instead_hostname) != bool:
                raise InitException("test_mode_setting_error")
            if not self.thread_count > 0:
                raise InitException("thread_count_error")
            if type(self.forbidden_word_list) != list:
                raise InitException("forbidden_word_list_error")
        except:
            raise InitException(sys.exc_info())

    def save(self, path):
        with open(path, 'w') as f:
            json.dump(self.__dict__, f, indent=2)

    def load(self, path):
        with open(path) as f:
            json_object = json.load(f)
            for key, value in json_object.items():
                exec(f"self.{key} = value")


class ServerInfoList:
    def __init__(self, config: Config):
        self.config = config
        self.server_df = None

    def read_excel(self, path: str):
        df = pd.read_excel(path, engine='openpyxl')
        df[server_info_list_column[4]].fillna(self.config.default_port, inplace=True)
        df[server_info_list_column[6]].fillna(self.config.default_login_term, inplace=True)
        df.fillna('', inplace=True)
        self.server_df = df.astype(dict(zip(server_info_list_column, server_info_list_types)))

    def read_csv(self, path: str):
        pass

    def __len__(self):
        if self.server_df is None:
            return 0
        else:
            return len(self.server_df)

    def iter_servers(self):
        for row in self.server_df.itertuples():
            index, server_name, ip, user_id, pwd, port, cmd_list_name, login_term = tuple(row)
            port, login_term = int(port), float(login_term)
            yield ServerInfo(index=index, server_name=server_name, hostname=ip, user_id=user_id, user_password=pwd,
                             port=port, command_list_name=cmd_list_name, login_term=login_term)


class ServerInfo:
    def __init__(self, index: int, server_name: str, hostname: str, user_id: str, user_password: str, port: int,
                 login_term, command_list_name: Optional[str] = None):
        self.index = index
        self.server_name, self.hostname, self.user_id, self.password = server_name, hostname, user_id, user_password
        self.port, self.login_term = int(port), float(login_term)
        if command_list_name is None:
            self.command_list_name = ''
        else:
            self.command_list_name = command_list_name

    def __str__(self):
        res = ""
        for key, item in self.__dict__.items():
            res += f"{key}={item}, "
        return res


class CommandList:
    def __init__(self, config: Config):
        self.config = config
        self.command_df = None

    def read_excel(self, file_path: str):
        self.command_df = pd.read_excel(file_path, engine='openpyxl')
        self.command_df[command_list_column[1]].fillna(self.config.default_stdout_term, inplace=True)
        self.command_df[command_list_column[3]].fillna(self.config.default_encoding, inplace=True)
        self.command_df.fillna('', inplace=True)
        self.command_df = self.command_df.astype(dict(zip(command_list_column, command_list_types)))

    def read_csv(self, file_path: str):
        pass

    def __len__(self):
        if self.command_df is None:
            return 0
        else:
            return len(self.command_df)

    def iter_commands(self):
        for row in self.command_df.itertuples():
            index, command, stdout_term, to_do_keyword, encoding = tuple(row)
            stdout_term = float(stdout_term)
            yield CommandInfo(command=command, stdout_term=stdout_term, to_do_keyword=to_do_keyword, encoding=encoding)


class CommandInfo:
    def __init__(self, command, stdout_term, encoding, to_do_keyword: Optional[str] = None):
        self.command = command
        self.stdout_term = stdout_term
        if to_do_keyword is not None:
            self.to_do_keyword = to_do_keyword
        else:
            self.to_do_keyword = ''
        self.encoding = encoding

    def __str__(self):
        res = ""
        for key, item in self.__dict__.items():
            res += f"{key}={item}, "
        return res


class InitialSetter:
    class _Checker(metaclass=ABCMeta):
        def __init__(self):
            pass

        @abstractmethod
        def exist(self):
            return False

        @abstractmethod
        def make(self):
            pass

    class _DirectoryChecker(_Checker):
        def __init__(self, path: str):
            super().__init__()
            self.path = path

        def exist(self):
            return os.path.isdir(self.path)

        def make(self):
            os.makedirs(self.path)

    class _ServerInfoListChecker(_Checker):
        def __init__(self, path: str):
            super().__init__()
            self.path = path
            self.columns = server_info_list_column

        def exist(self):
            return os.path.isfile(self.path)

        def make(self):
            if self.path.endswith('.xlsx'):
                df = pd.DataFrame(columns=self.columns)
                df.to_excel(self.path, index=False)
            elif self.path.endswith('.csv'):
                log.warning("csv 미구현.")

    class _SampleCommandListChecker(_Checker):
        def __init__(self, directory_path: str, file_name: str):
            super().__init__()
            self.file_name = file_name
            self.directory_path = directory_path
            self.columns = command_list_column

        def exist(self):
            return os.path.isdir(self.directory_path)

        def make(self):
            os.makedirs(self.directory_path)
            if self.file_name.endswith('.xlsx'):
                df = pd.DataFrame(columns=self.columns)
                df.to_excel(os.path.join(self.directory_path, self.file_name), index=False)
            elif self.file_name.endswith('.csv'):
                log.warning("csv 미구현.")

    class _ConfigFileChecker(_Checker):
        def __init__(self, path: str):
            super().__init__()
            self.path = path
            self._config: Optional[Config] = None

        def exist(self):
            existence = os.path.isfile(self.path)
            if existence:
                self._config = Config()
                self._config.load(self.path)
            return existence

        def make(self):
            self._config = Config.get_default()
            self._config.save(self.path)

        def get_config(self):
            return self._config

    def __init__(self, command_directory_path: str, interpreter_py_path: str, report_py_path: str):
        self.report_py_path = report_py_path
        self.interpreter_py_path = interpreter_py_path
        log.debug(f"interpreter_py_path : {interpreter_py_path}")

        self._configFile = self._ConfigFileChecker(config_file_path)
        log.debug(f"config_file_path : {config_file_path}")

        self._resultDirectory = self._DirectoryChecker(result_directory_path)
        log.debug(f"result_directory_path : {result_directory_path}")

        self._printDirectory = self._DirectoryChecker(print_directory_path)
        log.debug(f"print_directory_path : {print_directory_path}")

        self.command_directory_path = command_directory_path
        log.debug(f"command_directory_path : {command_directory_path}")

        self._runnable = False
        self._reason_for_not_runnable = ""

    def read_py(self):
        if self.interpreter_py_path.endswith(".py"):
            file = self.interpreter_py_path[:-3]
            exec(f"import {file}")
            log.info(f"{file}.py 읽기 성공")
        else:
            log.error(f"custom interpreter python file 읽기 실패")
            raise Exception("interpreter file has to end with \".py\"")
        if self.report_py_path.endswith(".py"):
            r = reportWriter.ReportWriter(1, ".", self.get_config(), ["1"])
            file = self.report_py_path[:-3]
            exec(f"import {file}")
            log.info(f"{file}.py 읽기 성공")
        else:
            log.error(f"report writer python file 읽기 실패")
            raise Exception("report writer py file has to end with \".py\"")

    def start(self):
        log.info("초기화 작업 시작")
        self._runnable = True
        self.log_level = log.Level.DEBUG
        try:
            if not self._configFile.exist():
                self._configFile.make()
                log.info("config file 생성")
            else:
                log.info("config file 불러오기 성공")
                try:
                    self._configFile.get_config().available()
                    log.info("config file 유효성 검증 성공")
                except InitException as e:
                    self._reason_for_not_runnable = str(e)
                    self._runnable = False
                    self.log_level = log.Level.ERROR
                    log.error(f"config file 유효성 검증 실패:{self._reason_for_not_runnable}")
                    return
        except:
            self._reason_for_not_runnable = str(sys.exc_info())
            self._runnable = False
            self.log_level = log.Level.ERROR
            log.error(f"config file 에러:{self._reason_for_not_runnable}")
            return

        if self._configFile.get_config().debug_mode:
            log.set_file_level(log.Level.DEBUG)
            log.set_stdout_level(log.Level.DEBUG)

        log.debug(f"현재 실행 경로:{os.path.abspath(__file__)}")
        log.debug(f"os.cwd:{os.getcwd()}")


        if not self._resultDirectory.exist():
            self._resultDirectory.make()
            log.debug("result directory 생성")
        else:
            log.debug("result directory 확인 완료")

        if not self._printDirectory.exist():
            self._printDirectory.make()
            log.debug("print directory 생성")
        else:
            log.debug("print directory 확인 완료")

        #sys.path.append(os.path.join(os.getcwd(), self.report_py_path))
        #sys.path.append(os.path.join(os.getcwd(), self.interpreter_py_path))
        sys.path.append(os.getcwd())
        try:
            self.read_py()
        except:
            self._reason_for_not_runnable = f"reading python file failed.  : {str(sys.exc_info())}"
            self._runnable = False
            self.log_level = log.Level.ERROR
            return

        info_list_extension = self._configFile.get_config().info_list_extension
        log.debug(f"info_list_extension = {info_list_extension}")

        _serverInfo = self._ServerInfoListChecker(
            os.path.join('./', server_info_list_file_name + info_list_extension)
        )

        _sampleCommandList = self._SampleCommandListChecker(
            self.command_directory_path,
            "sample_command_list" + info_list_extension
        )

        if not _sampleCommandList.exist():
            _sampleCommandList.make()
            log.debug("sample command list 생성")
            self._reason_for_not_runnable = "커맨드 리스트를 작성해주세요."
            self.log_level = log.Level.INFO
            self._runnable = False
        if not _serverInfo.exist():
            _serverInfo.make()
            log.debug("server info list 생성")
            self._reason_for_not_runnable = "서버 정보 리스트를 작성해주세요."
            self.log_level = log.Level.INFO
            self._runnable = False

    def runnable(self):
        return self._runnable

    def why_not_runnable(self):
        return self._reason_for_not_runnable

    def get_config(self):
        return self._configFile.get_config()


class Printer:
    def __init__(self):
        pass

    def start(self, info: ServerInfo):
        log.info("[{}] {}({}) 의 작업을 출력합니다.".format(info.index, info.server_name, info.hostname))

    def print(self, index, output: str):
        log.lprint(output)

    def done(self, index):
        pass


class ToTxtPrinter(Printer):

    def __init__(self, print_directory, config):
        super().__init__()
        self.print_directory = print_directory
        self.config = config
        self.file_pointer_dictionary = dict()

    def start(self, info: ServerInfo):
        super().start(info)
        self.file_pointer_dictionary[info.index] = open(
            os.path.join(self.print_directory, f"{info.server_name}.txt"), "w", encoding=self.config.default_encoding
        )

    def print(self, index, output: str):
        super().print(index, output)
        tmp = output.encode(self.config.default_encoding).replace(b'\r\n', b'\n')
        tmp = tmp.decode(self.config.default_encoding)
        self.file_pointer_dictionary[index].write(tmp)

    def done(self, index):
        super().done(index)
        self.file_pointer_dictionary[index].close()


class BlankTodoSaver:
    def __init__(self, result_directory, config):
        self.result_directory = result_directory
        self.config = config
        self.file_pointer_dictionary = dict()

    def open(self, info: ServerInfo):
        self.file_pointer_dictionary[info.index] = [info.server_name, None]

    def write(self, index, output: str):
        if self.file_pointer_dictionary[index][1] is None:
            self.file_pointer_dictionary[index][1] = open(
                os.path.join(self.result_directory, f"{self.file_pointer_dictionary[index][0]}.txt"), "w")
        tmp = output.encode(self.config.default_encoding).replace(b'\r\n', b'\n')
        tmp = tmp.decode(self.config.default_encoding)
        self.file_pointer_dictionary[index][1].write(tmp)
        log.debug(f'write {os.path.join(self.result_directory, f"{self.file_pointer_dictionary[index][0]}.txt")}')

    def close(self, index):
        if self.file_pointer_dictionary[index][1] is not None:
            self.file_pointer_dictionary[index][1].close()
            log.debug(f'close {os.path.join(self.result_directory, f"{self.file_pointer_dictionary[index][0]}.txt")}')


class InterpreterSet:
    def __init__(self, interpreter_py_path: str):
        self.to_import = interpreter_py_path[:-3]

    def get_interpreter(self, to_do_keyword):
        exec(f"import {self.to_import}")
        try:
            result = eval(f"{self.to_import}.{to_do_keyword}()")
        except:
            raise AutomaticException(f"{to_do_keyword} 클래스가 없습니다.")
        return result


class Worker:
    def __init__(self, server_count: int, config: Config, printer: Printer,
                 interpreter_set: Optional[InterpreterSet] = None):
        self.output = ''
        self.index_data_dict = dict()
        self.printer = printer
        self.interpreter_set: Optional[InterpreterSet] = interpreter_set
        if self.interpreter_set is not None:
            exec(f"import {reportwriter_py_path[:-3]}")
            self.report_writer = eval(
                f"{reportwriter_py_path[:-3]}.ReportWriter(server_count, report_file_path, config.default_encoding)")
            self.blank_todo_saver = BlankTodoSaver(result_directory_path, config)
        self._retry = False

    def insert_header(self, info: ServerInfo):
        self.printer.start(info)
        if self.interpreter_set is not None:
            self.report_writer.insert(info.index, (info.server_name, info.hostname))
            self.blank_todo_saver.open(info)

    def process(self, index: int, output: str, keyword: str):
        self.index_data_dict[index] = [output, keyword]
        self.printer.print(index, output)
        if self.interpreter_set is not None:
            if self.index_data_dict[index][1]:
                self._interpret(index)
            else:
                self.blank_todo_saver.write(index, output)

    def reprocess(self, index: int, retry_output: str):
        data = self.index_data_dict[index]
        data[0] += retry_output
        self.index_data_dict[index] = data

        self.printer.print(index, retry_output)
        if self.interpreter_set is not None:
            if self.index_data_dict[index][1]:
                self._interpret(index)
            else:
                self.blank_todo_saver.write(index, retry_output)

    def _interpret(self, index: int):
        custom_interpreter = self.interpreter_set.get_interpreter(self.index_data_dict[index][1])
        stdout_lines = self.index_data_dict[index][0].split('\n')

        for line in stdout_lines:
            custom_interpreter.interpret_single_line(line)
            status = custom_interpreter.get_status()
            if status == interpreter.Status.DONE:
                break

        status = custom_interpreter.get_status()
        if status == interpreter.Status.UNFINISHED:
            self._retry = True
        else:
            cell_to_insert = custom_interpreter.values()
            self.report_writer.insert(index, cell_to_insert)
            self.report_writer.save()
            log.debug(f"[{index}] result value -> {cell_to_insert}")
            self._retry = False

    def retry(self) -> bool:
        return self._retry

    def done(self, index):
        self.printer.done(index)
        if self.interpreter_set is not None:
            self.blank_todo_saver.close(index)
            self.report_writer.save()


class AutomaticException(Exception):
    def __init__(self, *args: object) -> None:
        self.exception_args = args
        super().__init__(*args)

    def __str__(self) -> str:
        res = ''
        for a in self.exception_args:
            res += str(a) + ' '
        return res


def work_at_one_connection(serverInfo: ServerInfo, worker: Worker, config: Config):
    if config.file_instead_hostname:
        ssh = sshConnector.DebugConnector(config.default_encoding)
    else:
        ssh = sshConnector.SshConnector(config.default_encoding)
    try:
        log.info(f"[{serverInfo.index}] {serverInfo.server_name}({serverInfo.hostname}) 연결 시도중...")
        ssh.connect(hostname=serverInfo.hostname, user_id=serverInfo.user_id, password=serverInfo.password,
                    port=serverInfo.port, timeout=config.ssh_timeout, login_term=serverInfo.login_term)
    except:
        raise AutomaticException(f"[{serverInfo.index}] {serverInfo.server_name}({serverInfo.hostname}): SSH 연결 실패",
                                 sys.exc_info())
    else:  # 연결 성공
        log.info(f"[{serverInfo.index}] {serverInfo.server_name}({serverInfo.hostname}) 연결 성공!")
        try:
            commandList = CommandList(config)
            commandList.read_excel(
                os.path.join(command_directory_path, serverInfo.command_list_name + config.info_list_extension)
            )
            log.debug(f"[{serverInfo.index}] cmd:" + str([c.command for c in commandList.iter_commands()]))
        except:
            ssh.close()
            raise AutomaticException(
                f"[{serverInfo.index}] {serverInfo.server_name}({serverInfo.hostname}): {serverInfo.command_list_name + config.info_list_extension} 읽기 실패",
                sys.exc_info())
        else:  # 커맨드 파일 읽기 성공
            try:
                with thread_lock:
                    log.debug(f"insert {serverInfo}")
                    worker.insert_header(serverInfo)
            except:
                ssh.close()
                raise AutomaticException(
                    f"[{serverInfo.index}] {serverInfo.server_name}({serverInfo.hostname}): 헤더 처리 중 예외 발생",
                    sys.exc_info())
            for commandInfo in commandList.iter_commands():  # 명령어들 수행
                retry_count = 0
                try:
                    if commandInfo.command:
                        if commandInfo.command in config.forbidden_word_list:
                            with thread_lock:
                                ssh.close()
                                worker.done(serverInfo.index)
                            raise AutomaticException(
                                f"[{serverInfo.index}] {serverInfo.server_name}({serverInfo.hostname}): {commandInfo.command}는 금지된 명령어입니다. 작업 종료."
                            )
                        else:
                            ssh.send(commandInfo.command)
                    result_stdout = ssh.recv(commandInfo.stdout_term, commandInfo.encoding)
                except:
                    with thread_lock:
                        ssh.close()
                        worker.done(serverInfo.index)
                    raise AutomaticException(
                        f"[{serverInfo.index}] {serverInfo.server_name}({serverInfo.hostname}): {commandInfo.command} 송수신 중 SSH 통신 에러",
                        sys.exc_info())
                try:  # 첫번째 시도
                    with thread_lock:
                        worker.process(serverInfo.index, result_stdout, commandInfo.to_do_keyword)
                        retry = worker.retry()
                except:
                    with thread_lock:
                        ssh.close()
                        worker.done(serverInfo.index)
                    raise AutomaticException(
                        f"[{serverInfo.index}] {serverInfo.server_name}({serverInfo.hostname}):{commandInfo.command} 처리중 예외 발생",
                        sys.exc_info()
                    )
                while retry and retry_count < config.maximum_number_of_recollections:
                    retry_count += 1
                    log.info(
                        f"[{serverInfo.index}] {serverInfo.server_name}({serverInfo.hostname}):{commandInfo.command} 재수집 중...({retry_count})")
                    try:
                        retry_stdout = ssh.recv(config.recollection_delay_time, commandInfo.encoding)
                    except:
                        with thread_lock:
                            ssh.close()
                            worker.done(serverInfo.index)
                        raise AutomaticException(
                            f"[{serverInfo.index}] {serverInfo.server_name}({serverInfo.hostname}):{commandInfo.command} 의 {retry_count}번째 재수집 중 SSH 통신 에러",
                            sys.exc_info())
                    try:
                        with thread_lock:
                            worker.reprocess(serverInfo.index, retry_stdout)
                            retry = worker.retry()
                    except:
                        with thread_lock:
                            ssh.close()
                            worker.done(serverInfo.index)
                        raise AutomaticException(
                            f"[{serverInfo.index}] {serverInfo.server_name}({serverInfo.hostname}):{commandInfo.command} 재처리중 예외 발생",
                            sys.exc_info())
                if retry_count >= config.maximum_number_of_recollections:
                    with thread_lock:
                        ssh.close()
                        worker.done(serverInfo.index)
                    raise AutomaticException(
                        f"[{serverInfo.index}] {serverInfo.server_name}({serverInfo.hostname}):{commandInfo.command} 재수집 회수 초과")

            ssh.close()
            worker.done(serverInfo.index)
            log.info(f"[{serverInfo.index}] {serverInfo.server_name}({serverInfo.hostname}) 작업 성공!")


class Main:
    def __init__(self):
        self.total_count = 0
        self.success_count = 0
        self.failed_server_list = []

    def init(self):
        log.info("프로그램 시작")
        setter = InitialSetter(command_directory_path, interpreter_py_path, reportwriter_py_path)
        setter.start()
        if not setter.runnable():
            log.pass_to_log(setter.log_level, setter.why_not_runnable())
            self.exit(0)

        # 콘픽 불러오기
        self.config = setter.get_config()
        log.debug(f"config: {self.config}")

    def exit(self, code):
        input("종료하시려면 엔터를 누르세요.")
        log.info("프로그램 종료")
        exit(code)

    def run(self, with_save_txt: bool, with_interpreter: bool, single_thread_mode:bool):
        try:
            # 서버 정보 불러오기
            serverInfoList = ServerInfoList(self.config)
            if self.config.info_list_extension == ".xlsx":
                try:
                    serverInfoList.read_excel(server_info_list_file_name + self.config.info_list_extension)
                except:
                    log.error(f"서버 정보 액셀 불러오기 실패. {sys.exc_info()}")
                else:
                    self.total_count = len(serverInfoList)
                    self.success_count = 0
                    self.failed_server_list = []
                    log.info(f"서버 정보 액셀 불러오기 성공. 총 {self.total_count}개의 서버")
            elif self.config.info_list_extension == ".csv":
                log.warning("csv 미구현")
                self.exit(0)

            # 실행
            if len(serverInfoList) > 0:
                if with_save_txt:
                    printer = ToTxtPrinter(print_directory_path, self.config)
                else:
                    printer = Printer()

                if with_interpreter:
                    interpreter_set = InterpreterSet(interpreter_py_path)
                else:
                    interpreter_set = None

                worker = Worker(len(serverInfoList), self.config, printer, interpreter_set)

                if self.config.file_instead_hostname:
                    log.info("TEST 모드로 시작.")

                log.info(f"txt 출력:{with_save_txt}, interpreter mode:{with_interpreter} 으로 {self.total_count}개의 작업 시작")

                if single_thread_mode:
                    max_connection = 1
                else:
                    max_connection = self.config.thread_count

                thread_manager = ThreadConnection(max_connection, self)
                log.debug(f"thread count = {max_connection}")
                for serverInfo in serverInfoList.iter_servers():
                    try:
                        thread_manager.connect(serverInfo, worker, self.config)
                    except AutomaticException as e:
                        log.error(str(e))

                thread_manager.wait()
                log.info(f"작업 종료. {self.total_count}개 작업 중 {self.success_count}개 성공.")
                if self.failed_server_list:
                    log.info("실패한 서버목록은 아래와 같습니다.")

                    def server_info_idx_cmp(a: ServerInfo, b: ServerInfo):
                        if a.index > b.index:
                            return 1
                        elif a.index < b.index:
                            return -1
                        else:
                            return 0

                    sorted_list = [f"[{server.index}] {server.server_name}" for server in sorted(self.failed_server_list, key=cmp_to_key(server_info_idx_cmp))]
                    for failed_server in sorted_list:
                        log.info(failed_server)
            else:
                log.warning("작업할 서버가 없습니다.")
                return
            return
        except:
            log.critical(f"예기치 못한 오류:{sys.exc_info()}")


class ConnectionThread(threading.Thread):

    def set_args(self, server_info: ServerInfo, worker: Worker, config: Config):
        self.server_info = server_info
        self.worker = worker
        self.config = config

    def run(self):
        try:
            work_at_one_connection(self.server_info, self.worker, self.config)
            self.success = True
        except AutomaticException as e:
            self.success = False
            log.error(str(e))


class ThreadConnection:
    def __init__(self, max_thread:int, main):
        self.main = main
        self.max_thread = max_thread
        self.cur_thread_count = 0
        self.last_joined_idx = 0
        self.thread_list: List[Optional[ConnectionThread]] = [None for i in range(self.max_thread)]

    def connect(self, *args):
        thread = ConnectionThread()
        thread.set_args(*args)

        if self.cur_thread_count < self.max_thread:
            thread.start()
            self.thread_list[self.cur_thread_count] = thread
            self.cur_thread_count += 1
        else:
            self.thread_list[self.last_joined_idx].join()
            if self.thread_list[self.last_joined_idx].success:
                self.main.success_count += 1
            else:
                self.main.failed_server_list.append(
                    self.thread_list[self.last_joined_idx].server_info
                )
            thread.start()
            self.thread_list[self.last_joined_idx] = thread
            self.last_joined_idx = (self.last_joined_idx + 1) % self.max_thread

    def wait(self):
        for i in range(self.cur_thread_count):
            self.thread_list[self.last_joined_idx].join()
            if self.thread_list[self.last_joined_idx].success:
                self.main.success_count += 1
            else:
                self.main.failed_server_list.append(
                    self.thread_list[self.last_joined_idx].server_info
                )
            self.last_joined_idx = (self.last_joined_idx + 1) % self.max_thread


if __name__ == '__main__':
    main = Main()
    main.init()
    main.run(True, True, False)
