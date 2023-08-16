import os
import time


class Monkey:

    def __init__(self, package=None, epoch=0, level=0, throttle=0, seed=11, event=None):
        self.cmd = None
        if event is None:
            event = {
                "touch": 0,
                "motion": 0,
                "trackball": 0,
                "nav": 0,
                "majornav": 0,
                "syskeys": 0,
                "appswitch": 0,
                "pinchzoom": 0,
                "rotation": 0,
                "flip": 0,
                "anyevent": 0,
            }
        self.package = package
        self.epoch = epoch
        self.level = level
        self.throttle = throttle
        self.seed = seed
        self.event = event

    def get_devices(self):
        content = os.popen("adb devices").read()
        print(content)

    def run_monkey_test(self):
        cmd = self.combine_cmd()
        os.popen(cmd)

    def combine_cmd(self):
        self.cmd = "adb shell monkey "
        self.__set_package()
        self.__set_event()
        self.__set_throttle()
        self.__set_seed()
        self.__set_level()
        self.__set_epoch()
        self.__set__ignore()
        # print(self.cmd)
        return self.cmd
    def __set_package(self):
        self.cmd += "-p " + self.package + " "

    def __set_epoch(self):
        self.cmd += self.epoch.__str__() + " "

    def __set_level(self):
        if self.level > 0:
            for i in range(0, self.level):
                self.cmd += "-v"
            self.cmd += " "

    def __set_seed(self):
        self.cmd += "-s " + self.seed.__str__() + " "

    def __set_throttle(self):
        self.cmd += "--throttle " + self.throttle.__str__() + " "

    def __set_event(self):
        for key in self.event:
            if self.event[key] > 0:
                self.cmd += "--pct-" + key + " " + self.event[key].__str__() + " "

    def __set__ignore(self):
        self.cmd += "--ignore-crashes --ignore-timeouts --ignore-security-exceptions --ignore-native-crashes"


if __name__ == "__main__":
    event = {
        "touch": 50,
        "motion": 50,
    }
    test = Monkey(package="com.example.CCAS", epoch=10, throttle=300, event=event, level=3)
    test.run_monkey_test()
    # test.get_devices()