사용 방법:
최초로 tui.py를 실행하면 아래와 같은 파일이 생긴다.

serverInfoList.xlsx : 접속할 서버의 정보를 적는다. 행 하나당 하나의 연결이다.

cmdset/sample_command_list.xlsx : serverInfoList에서 지정한 키워드 + .xlsx으로 이름을 변경한 후
서버에서 전송할 명령어들을 입력한다. 여기서 todo keyword는 customInterpreter.py의 클래스명과 일치해야 한다.

위 두 문서를 작성한 후 다시 실행하면 모드 선택이 나온다.

출력 모드 : ssh 연결을 통해 받은 stdout을 모두 result/print/server_name.txt 에 저장

레포트 모드 : todo keyword를 활용하여 출력으로부터 레포트값을 받은 뒤 이를 종합하여 result/result_report.txt에 저장

출력 및 레포트 모드 : 위의 두가지를 동시에 수행한다.

멀티 쓰레드 모드 : 따로 설정하지 않으면 한번에 하나의 연결만 연결한다. 멀티 쓰레드 모드를 설정하면 동시에
여러 연결을 수행한다.


config.json에서 forbidden_command_list를 설정할 수 있다. 배열로 입력한다. 해당 배열에 들어있는 문자열이
커맨드에 포함되면 그 연결을 중단한다.
또한 thread count를 지정하여 멀티 쓰레드 모드에서 동시에 접속할 연결의 최대 갯수를 설정할 수 있다.

이외에 login_term, stdout_term, recollecting_term은 동작 수행 전 약간의 딜레이 타임을 의미한다.
충분한 시간을 입력하여야 모든 출력을 받아온다.

recollecting은 레포트 모드에서 정상적인 레포트값이 나오지 않았을 때 다시 서버로부터 stdout을 받는 것을 의미하며
최대 실행 횟수와 기다리는 시간을 설정할 수 있다.


프로그램이 실행되는 동안에 발생하는 모든 로그는 log.txt에 저장된다. config.json에서 debug를 활성화하면 디버그 메세지도 포함된다.

file instead hostname은 serverInfoList의 hostname 열을 파일 경로로 간주한다. 텍스트파일로부터 작업을 수행할 때 사용한다.
