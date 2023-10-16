How-Are-Servers
===
배포 버전: 1.7

매 주기마다 SSH 연결을 통해 서버를 점검합니다.

여러 서버의 CPU 상태, 메모리 상태, 데이터베이스 상태 등등... 이러한 항목을 자동으로 체크하여 xlsx 문서로 만듭니다.

간단 요약
---
1. 서버에 ssh 접속한다.
2. 정해진 명령어를 전송한다.
3. 서버로부터 출력 결과를 받아온다.
4. 출력 결과에서 필요한 값을 추출하여 액셀화한다.
5. 다음 서버로 넘어간 뒤 `1.`부터 작업을 반복한다.


빌드 하기전에!
---

* **Windows**에서 `build.bat`로 빌드 가능합니다.
* **Python**이 깔려있어야 하며, python venv가 정상 작동해야 합니다.

빌드하여 `exe` 만들기
---

<img src="https://github.com/simjeehoon/src_repository/blob/master/How-Are-Servers/master/b_buildbat.PNG?raw=true" title="b_buildbat.PNG" alt="b_buildbat.PNG"></img><br/>

<img src="https://github.com/simjeehoon/src_repository/blob/master/How-Are-Servers/master/b_buildshell.png?raw=true" title="b_buildshell.png" alt="b_buildshell.png"></img><br/>

 1. `build.bat`을 실행한다.

<img src="https://github.com/simjeehoon/src_repository/blob/master/How-Are-Servers/master/b_output.png?raw=true" title="b_output.png" alt="b_output.png"></img><br/>

 2. 빌드를 성공하면 `output`폴더가 생성된다. 안으로 들어간다.

<img src="https://github.com/simjeehoon/src_repository/blob/master/How-Are-Servers/master/b_checker.png?raw=true" title="b_checker.png" alt="b_checker.png"></img><br/>

 3. `checker.exe`가 생성되었다. 두개의 `py` 파일은 레포트 출력을 할 때 수정한다.

# 사용법

<img src="https://github.com/simjeehoon/src_repository/blob/master/How-Are-Servers/master/c_initrun.png?raw=true" title="c_initrun.png" alt="c_initrun.png"></img><br/>

`checker.exe`를 처음 실행하면 필요 파일이 생성된다.

<img src="https://github.com/simjeehoon/src_repository/blob/master/How-Are-Servers/master/c_initfiles.png?raw=true" title="c_initfiles.png" alt="c_initfiles.png"></img><br/>

작동 방식
---
<img src="https://github.com/simjeehoon/src_repository/blob/master/How-Are-Servers/master/c_y1.png?raw=true" title="c_y1.png" alt="c_y1.png"></img><br/>

### serverInfoList

`serverInfoList.xlsx`에 checker가 접속할 서버들의 정보를 입력할 수 있다.

 * ***name*** : 서버의 별명이다. 임의로 지을 수 있으며, 이 이름대로 텍스트 파일명이나 레포트 서버명이 지정된다.
 * ***hostname*** : 서버가 존재하는 네트워크 호스트 네임 혹은 아이피 주소이다.
 * ***id*** : 서버 계정 아이디
 * ***password*** : 서버 계정 비밀번호
 * ***port*** : 접속 포트 번호
 * ***command_file*** : 커맨드 파일 이름이다. `cmdset` 내 `sample_command_list.xlsx`를 복사하여 이름을 설정한 후 확장자 .xlsx를 제외한 파일이름을 적으면 된다.
   * 이 파일에 적힌 커맨드에 따라 명령어 전송 및 출력이 수행된다.
   * 사진에서는 `Webserver.xlsx`을 `cmdset` 폴더 내에 만들었다.
 * ***login_term*** : 로그인 후 기다릴 시간이다. 단위: **second**
  
### command file

`sample_command_list.xlsx`을 복사하여 `serverInfoList`의 ***command_file***에 입력했던 파일명으로 이름을 변경한 뒤 커맨드들을 입력한다.

 * ***command*** : 서버에 보낼 커맨드이다.
 * ***stdout_term*** : 커맨드 전송 후 출력을 기다릴 시간이다. 단위: **second**
 * ***to_do_keyword*** : 다음 세가지 케이스가 있다.
   1. 빈칸으로 두기
      * 이 경우 출력 결과를 result 폴더 내 `서버_별명.txt`에 기록한다.
   2. `customInterpreter.py` 내 `CustomInterpreter`를 상속한 클래스명을 적기
      * 이 경우 `result/resultReport.xlsx`의 해당 셀에 `values()`를 호출하여 얻은 값을 기록한다.
      * `CustomInterpreter` 클래스는 아래와 같다.
      ```py
      class CustomInterpreter:
        def __init__(self, status: Status=Status.VALID_AND_CONTINUABLE):
            self.status: Status = status

        def interpret_single_line(self, one_line: str):
            pass

        def get_status(self) -> Status:
            return self.status

        def values(self):
            return None
      ```
      * 위의 `CustomInterpreter`를 상속한 클래스를 `customInterpreter.py`에 작성하게 되면 런타임에 해당 클래스를 `import`하여 실행하게 된다.
      * Status는 다음과 같다.
      ```py
      class Status(Enum):
        UNFINISHED = 0     
        VALID_AND_CONTINUABLE = 1
        DONE = 2
        PASS = 3
      ```
      #### 작동 과정

      * 커맨드 입력 후 서버로부터 표준 출력을 받게된다.
      * 표준 출력을 개행 단위로 나눈 뒤 차례대로 `interpret_single_line`에 인자로 넣는다.
      * 사용자는 이 `interpret_single_line` 메서드 안에서 `self.status`를 변경할 수 있다. 각각은 다음을 의미한다.
        + `UNFINISHED` : 원하는 값이 안나왔으므로 시간이 초과되었을 때 결과값이 나올 때까지 다시 기다린다.
        + `VALID_AND_CONTINUABLE` : 시간이 초과되었을 때 `values()` 메서드의 값을 수용한다.
        + `DONE` : 원하는 값이 등장하였으므로 `values()` 메서드의 값을 받아 들인 후 다음 작업으로 넘어간다.
        + `PASS` : Report에 값을 기록하지 않는다. 
      * 프로그램은 `interpret_single_line` 메서드를 수행한 이후 `get_status`로 현재 `status`를 파악하며, 기록할 조건이 성립되면 `values` 메서드로부터 값을 받아들인다. 
   3. Pass 입력
      * `customInterpreter.py`에 `Pass` 클래스가 있다. 이것을 사용하면 명령어 입력에 대한 표준 출력에 대해 아무 작업을 하지 않는다. 
        * 무조건 `Status.PASS`를 반환하기 때문이다.
        * 예시로 슈퍼유저 진입시 사용할 수 있다.
 
 * ***encoding*** : 출력 결과를 어떤 Character Set으로 인코딩할지 지정한다.

예시
---

<img src="https://github.com/simjeehoon/src_repository/blob/master/How-Are-Servers/master/_easy.png?raw=true" title="_easy.png" alt="_easy.png"></img><br/>

`_EasyExtract`는 `CustomInterpreter`를 상속함

<img src="https://github.com/simjeehoon/src_repository/blob/master/How-Are-Servers/master/c_y2.png?raw=true" title="c_y2.png" alt="c_y2.png"></img><br/>

`DfChecker`는 `_EasyExtract`를 상속함.

df -h 명령어 입력 후 점유율이 10퍼센트가 넘는 경로들을 모두 반환

### `customReportWriter.py`
<img src="https://github.com/simjeehoon/src_repository/blob/master/How-Are-Servers/master/c_y3.png?raw=true" title="c_y3.png" alt="c_y3.png"></img><br/>

`resultReport.xlsx`의 첫 행 제목을 위와 같이 변경

작업 수행
---

<img src="https://github.com/simjeehoon/src_repository/blob/master/How-Are-Servers/master/d_y1.png?raw=true" title="d_y1.png" alt="d_y1.png"></img><br/>

<img src="https://github.com/simjeehoon/src_repository/blob/master/How-Are-Servers/master/d_y2.png?raw=true" title="d_y2.png" alt="d_y2.png"></img><br/>



<img src="https://github.com/simjeehoon/src_repository/blob/master/How-Are-Servers/master/e1.png?raw=true" title="e1.png" alt="e1.png"></img><br/>

<img src="https://github.com/simjeehoon/src_repository/blob/master/How-Are-Servers/master/e2.png?raw=true" title="e2.png" alt="e2.png"></img><br/>

정상적으로 기록됨을 확인할 수 있습니다.

<img src="https://github.com/simjeehoon/src_repository/blob/master/How-Are-Servers/master/f1.png?raw=true" title="f1.png" alt="f1.png"></img><br/>


메뉴 설명
---

<img src="https://github.com/simjeehoon/src_repository/blob/master/How-Are-Servers/master/d_y1.png?raw=true" title="d_y1.png" alt="d_y1.png"></img><br/>

 * 출력 : `result/print` 폴더에 서버별 결과가 텍스트 파일로 저장됩니다.
 * 레포트 작성 : `result/resultReport.xlsx` 에 *to_do_keyword*에 따라 적절하게 출력값을 해석하고 반환합니다.
 * 3번의 경우 출력과 레포트 작성을 둘 다 합니다.
 * 4번의 멀티 스레드 모드를 선택할 경우 동시에 여러 서버에 접속하여 병렬적으로 작업을 수행합니다. 작업 시간이 대폭 단축됩니다.


`config.json` 설명
---
### `default_port`

 serverInfoList.xlsx에서 port를 지정하지 않을 경우 입력되는 기본 포트입니다.
### `default_login_term`

 serverInfoList.xlsx에서 login_term을 지정하지 않을 경우 입력되는 기본 로그인 대기 시간입니다. 초 단위입니다.
### `default_stdout_term`

 command file에서 stdout_term을 지정하지 않을 경우 입력되는 기본 대기 시간입니다. 초 단위입니다.
### `default_encoding`

 command file에서 encoding을 지정하지 않을 경우 적용되는 기본 캐릭터셋입니다.
### `ssh_timeout`

 ssh로 접속했을 때 ssh_timeout초만큼 대기해도 응답이 없으면 해당 작업을 실패로 처리합니다.
### `maximum_number_of_recollections`

 interpret 과정중 UNFINISHED 상태일때 재해석을 몇회까지 할것인지 지정합니다.
### `recollection_delay_time`

 재해석을 위해 recollection_delay_time초 만큼 기다리게 됩니다.
### `info_list_extension`

 serverInfoList의 파일 형식입니다. 현재는 xlsx만 됩니다.
### `debug_mode`

 디버그모드를 true로 하면 interpret 과정을 전부 표시합니다.
### `file_instead_hostname`

 네트워크 연결 대신 파일 입력을 바탕으로 처리합니다. serverInfoList의 hostname 열을 텍스트 파일 경로로 간주합니다.
### `thread_count`

 최대 쓰레드 카운트입니다. 동시에 몇개의 연결을 수행할 것인지 결정합니다.
### `forbidden_word_list`

 금지 명령어를 설정할 수 있습니다. 이 리스트에 포함된 단어가 명령어에 포함되면 해당 명령어는 수행되지 않습니다.


`log.txt` 설명
---
작업의 모든 로그는 `log.txt`에 기록됩니다.
어떤 작업에 문제가 있었는지 쉽게 확인 가능합니다.

term에 대해...
---
네트워크 상태, 서버 상태, 서버에서 작업하는 속도 등의 영향으로 모든 표준 출력을 즉각 가져올 수 없을 수 있습니다.

따라서 대기 시간이 필요합니다.

서버 관리자가 명령어별로 필요한 대기 시간을 입력하여 작업에 차질이 없도록 만듭니다.


추후 과제
---
 + Windows 이외의 운영체제에서도 연결할 수 있도록 제작
 + argument를 지정해서 수행할 수 있도록 제작
 + csv 형식으로 serverInfoList 및 command file을 받아들일 수 있도록 제작
 + serverInfoList의 hostname을 hostname/IP로 변경
  


