from data import Test, Course, CourseButton
import random
from datetime import datetime, timedelta, timezone
from copy import deepcopy


class TestManager:
    def __init__(self, tests: list[Test],
                 mix_tests: bool = False,
                 time: int = None):
        self.tests = tests
        if mix_tests:
            random.shuffle(self.tests)
        for index, test in enumerate(self.tests):
            test.number = index + 1
            test.tests_leng = len(self.tests)
        self.tests_leng_static = len(self.tests)
        self.current_test: Test = None
        self.finished_tests : list[Test] = []
        self.time = time
        self.deadline = (
            datetime.now() + timedelta(minutes=time)
            if time else None
        )
        self.start_time = datetime.now()
        self.correct, self.incorrect = 0, 0

    def pop_test(self) -> Test:
        if self.tests:
            self.current_test = self.tests.pop(0)
            return self.current_test
        
    def skip_test(self) -> Test:
        if self.current_test and self.tests_leng >= 2:
            self.tests.append(self.current_test)
            self.current_test = self.tests.pop(0)
            return self.current_test
    
    def check_test(self, answer_index: int):
        if self.current_test:
            self.finished_tests.append(deepcopy(self.current_test))
            if answer_index == self.current_test.correct_index:
                self.correct += 1
                return True
            else:
                self.incorrect += 1
                return False

    @property
    def time_is_up(self) -> bool:
        # print('dedline:', self.deadline)
        # print('now:', datetime.now())
        return self.deadline is not None and datetime.now() >= self.deadline
    
    @property
    def tests_leng(self) -> int:
        return len(self.tests)
    
    @property
    def finished_tests_leng(self) -> int:
        return len(self.finished_tests)

    @property
    def finish_date(self) -> datetime:
        if self.time:
            return self.start_time + timedelta(minutes=self.time)

    @property
    def time_left(self) -> str:
        if not self.time:
            return

        td = self.finish_date - datetime.now()
        total = int(td.total_seconds())

        if total <= 0:
            return '00 sec'
        minutes = total // 60
        seconds = total % 60
        if minutes:
            return f"{minutes:02d} min {seconds:02d} sec"
        return f"{seconds:02d} sec"
    
    @property
    def correct_prestage(self) -> int:
        return round(self.correct / self.tests_leng_static * 100) if self.correct or self.tests_leng else 0