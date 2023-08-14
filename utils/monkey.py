import os
import re


class Monkey:
    def test(self):
        content = os.popen("adb devices").read()
        print(content)

    def monkey_test(self):
        content = os.popen("adb ").read()
        print(content)


