import datetime
import logging
import os
import re
import time


class Adb:

    def __init__(self, package_name):
        self.package = package_name

    def get_PID(self, package):
        if int(str((os.popen("adb shell getprop ro.build.version.release").readlines())).replace(
                "'", "").replace("\\n", "").replace("]", " ").replace("[", " ").split('.')[0]) >= 8:
            cmd = "adb shell ps -A"
        else:
            cmd = "adb shell ps"
        try:
            pid = []
            redcmd = str((os.popen(cmd).readlines())).replace("'", "").replace("\\n", " ").replace("]", " ").replace(
                "[",
                " ").split(
                ",")
            for n in redcmd:
                if package in n:
                    list_n = [i for i in n.split(" ") if i != '']  # 删除空元素
                    if package == list_n[-1]:
                        pid.append(list_n[1])
            return pid[0]
        except Exception as e:
            print(str(e), "get_mem(package)，请检查adb是否连通……")
            return 'xxxxx'

    def get_mem(self, package):
        try:
            cmd = r'adb shell dumpsys meminfo ' + package + ' | findstr "TOTAL"'  # % apk_file
            # cmd1 = 'adb shell cat /proc/meminfo | findstr "MemTotal"'
            red_cmd = str((os.popen(cmd).readlines()))
            # res = int(re.findall(r"\d+\.?\d*", red_cmd)[0])
            # # print(res)
            # total = int(str((os.popen(cmd1).readlines())).replace(" ", "").replace("MemTotal:", "").replace("kB", "")
            #             .replace("\\n", "").replace("]", "").replace("[", "").replace("'", ""))
            # # print(total)
            # per = round(res / total, 3)
            # return per
            return re.findall(r"\d+\.?\d*", red_cmd)[0]
        except Exception as e:
            print(str(e), "get_mem(package)，请检查包名是否正确……")
            return -1

    def get_cpu(self, pid):
        try:
            cmd = 'adb shell "cat /proc/stat | grep ^cpu"'  # % apk_file
            cmd1 = 'adb shell cat /proc/%s/stat' % pid
            redcmd = str((os.popen(cmd).readlines())).replace("'", "").replace("\\n", " ").replace("]", " ").replace(
                "[",
                " ")
            redcmd = [i for i in redcmd.split(",")[0].split(" ") if i != '']
            redcmd.remove(redcmd[0])
            del redcmd[-3:]
            total_cpu = sum(list(map(int, redcmd)))
            idle = redcmd[3]
            redcmd1 = str((os.popen(cmd1).readlines())).replace("'", "").replace("\\n", " ").replace("]", " ").replace(
                "[",
                " ").split(
                " ")[14:18]
            pjiff = sum(list(map(int, redcmd1)))
            return [total_cpu, idle, pjiff]
        except Exception as e:
            print(e, "get_s_cpu(),检查adb是否连通……")
            return [-1, -1, -1, -1, -1, -1, -1]

    def sum_dic(self):
        pid = self.get_PID(self.package)
        total_cpu1, idle1, avg_cpu1 = self.get_cpu(pid)

        # bt = "'time', 'package', 'mem', 'cpu', 'systemCpu', 'rxBytes', 'txBytes', 'rxTcpBytes', 'txTcpBytes'".replace(
        #     "'", "").replace(" ", "")
        # self.csv.info(bt)
        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        mem = round(int(self.get_mem(self.package)) / 1024, 3)
        # mem = self.get_mem(self.package)
        total_cpu2, idle2, avg_cpu2 = self.get_cpu(pid)
        p_cpu = 100.0 * (int(avg_cpu2) - int(avg_cpu1)) / (int(total_cpu2) - int(total_cpu1))  # process cpu
        system_cpu = 100.0 * ((int(total_cpu2) - int(idle2)) - (int(total_cpu1) - int(idle1))) / (
                int(total_cpu2) - int(total_cpu1))  # system cpu
        total_cpu1, idle1, avg_cpu1 = total_cpu2, idle2, avg_cpu2
        sum_dic_dit = {
            "time": time_str,
            'package': self.package,
            "mem": mem.__str__(),
            "cpu": round(p_cpu, 2).__str__(),
            "systemCpu": round(system_cpu, 2).__str__(),
        }
        list_v = list(sum_dic_dit.values())  # .replace("[", "").replace("]", "").replace("'", "")
        print(f"时间: {sum_dic_dit['time']}, 包名: {sum_dic_dit['package']}, "
              f"内存: {sum_dic_dit['mem']} MB, CPU: {sum_dic_dit['cpu']} %")
        return list_v


if __name__ == '__main__':
    testName = "1"
    a = Adb(testName, "")
