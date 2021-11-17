import sys

from automatic_test import Main
import logManager as log

if __name__ == '__main__':
    try:
        main = Main()
        main.init()

        single_thread_mode = True
        show = True
        def thread_string(mode):
            if mode:
                return "싱글"
            else:
                return "멀티"
        while True:
            if show:
                string = f"""Auto Checker 1.7
                [1] 출력하기
                [2] 레포트 작성하기
                [3] 출력 & 레포트 작성
                [4] {thread_string(not single_thread_mode)} 스레드 모드
                [5] 종료
                """
                print(string)
                show=False
            userInput = input("입력: ").strip()
            if userInput == "1":
                main.run(True, False, single_thread_mode)
            elif userInput == "2":
                main.run(False, True, single_thread_mode)
            elif userInput == "3":
                main.run(True, True, single_thread_mode)
            elif userInput == "4":
                if single_thread_mode:
                    single_thread_mode = False
                else:
                    single_thread_mode = True
                print(f"{thread_string(single_thread_mode)} 스레드 모드로 설정되었습니다.")
                show=True
                continue
            elif userInput == "5":
                exit(0)
            else:
                print("잘못된 입력.")
                continue
            break
    except:
        log.critical(f"알 수 없는 오류 발생 {sys.exc_info()}")
        input()
        exit(-1)
    else:
        main.exit(0)