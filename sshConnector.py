from typing import Optional

import paramiko
import time


class SshConnector:
    def connect(self, hostname: str, user_id: str, password: str,
                port: Optional[int] = None, timeout: Optional[float] = None, login_term: Optional[float] = None):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.hostname, self.user_id, self.password = hostname, user_id, password
        if port is not None:
            self.port = int(port)
        else:
            self.port = 22
        if timeout is not None:
            self.timeout = float(timeout)
        else:
            self.timeout = 10.0
        self.ssh_client.connect(hostname=self.hostname, username=self.user_id, password=self.password, port=self.port,
                                timeout=self.timeout)
        self.channel = self.ssh_client.invoke_shell()
        if login_term:
            time.sleep(float(login_term))

    def __init__(self, default_encoding: str):
        self.default_encoding = default_encoding
        pass

    def send(self, cmd):
        self.channel.send(cmd + '\n')

    def recv(self, recv_term: float = 0.0, encoding: Optional[str] = None):
        time.sleep(recv_term)
        if encoding is not None:
            self.encoding = encoding
        else:
            self.encoding = self.default_encoding
        stdout_string = self.__wait_streams()[0]
        return stdout_string

    def close(self):
        if self.ssh_client is not None:
            self.ssh_client.close()
            self.ssh_client = None

    def __wait_streams(self):
        stdout_string = stderr_string = ""
        while self.channel.recv_ready():
            stdout_string += self.channel.recv(65535).decode(self.encoding)
        while self.channel.recv_stderr_ready():
            stderr_string += self.channel.recv_stderr(65535).decode(self.encoding)
        return stdout_string, stderr_string


class DebugConnector(SshConnector):

    def connect(self, file_name: str, user_id: str, password: str, port: Optional[int] = None,
                timeout: Optional[float] = None, login_term: Optional[float] = None):
        self.file_name, self.user_id, self.password = file_name, user_id, password
        self.port, self.timeout, self.login_term = port, timeout, login_term
        self.f = open(self.file_name, 'r', encoding=self.default_encoding)

    def __init__(self, default_encoding: str):
        super().__init__(default_encoding)
        self.default_encoding = default_encoding
        self.past_commands = []

    def send(self, cmd):
        self.past_commands.append(cmd)

    def recv(self, recv_term: float = 0.0, encoding: Optional[str] = None):
        return self.f.read()

    def close(self):
        self.f.close()


def __sshConnectorDebug():
    ssh = SshConnector(default_encoding='utf-8')
    ssh.connect(hostname='gammaru.net', user_id='gammaru', password='katomegumi#001@', port=9022, timeout=10,
                login_term=0.0)
    print("연결 성공")
    while True:
        print(ssh.recv(1.0))
        user_input = input()
        if user_input == 'exit':
            ssh.close()
            break
        ssh.send(user_input)
    print("종료.")


if __name__ == '__main__':
    pass
