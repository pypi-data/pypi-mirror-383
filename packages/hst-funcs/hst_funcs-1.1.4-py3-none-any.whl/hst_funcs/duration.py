# pip install -U hst_funcs
# from hst_funcs import duration
# 코드 초입에 timer=duration.Timer()/ timer.tic()
# 코드 마지막에 timer.toc() 
import time

class Timer:
    def __init__(self):
        self.start_time = None
        self.end_time = None

    def tic(self):
        self.start_time = time.time()

    def toc(self):
        self.end_time = time.time()
        if self.start_time is None:
            print("tic() 메서드를 호출하여 시작 시간을 설정하세요.")
        else:
            elapsed_time = self.end_time - self.start_time
            print("코드 실행 시간:", elapsed_time, "초")