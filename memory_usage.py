#!/usr/bin/env python3

import subprocess
import sys
import os

if os.geteuid() > 0:
    print("Run this with ROOT privileges")
    exit(1)


def process_id(processName):
    try:
        pidof = subprocess.check_output(['pidof', processName])
        pids = pidof.decode('utf-8').split()
    except:
        print("Could not identify the process")
        exit(1)
    return pids


def pid_input(pid):
    proc = "/proc/" + str(pid)
    mem_file = proc + "/smaps"
    stat_file = proc + "/status"
    tot_phy = 0
    tot_swap = 0
    with open(mem_file, 'r') as smaps:
        for line in smaps:
            if line.startswith("Pss"):
                tot_phy += int(line.split()[1])
            elif line.startswith("SwapPSS"):
                tot_swap += int(line.split()[1])

    with open(stat_file, 'r') as stat:
        for line in stat:
            if line.startswith("Name"):
                process_name = "'".join(line.split()[1:])
    return (process_name, tot_phy, tot_swap)


def name_input(name):
    pids = process_id(name)
    tot_phy = 0
    tot_swap = 0
    for pid in pids:
        mem_file = "/proc/" + str(pid) + "/smaps"
        with open(mem_file, 'r') as smaps:
            phy_pid = 0
            swap_pid = 0
            for line in smaps:
                if line.startswith("Pss"):
                    phy_pid += int(line.split()[1])
                elif line.startswith("SwapPss"):
                    swap_pid += int(line.split()[1])

        tot_phy += phy_pid
        tot_swap += swap_pid
    return {"Phys": tot_phy, "Swap": tot_swap}


def main(process):
    tot_phys = 0
    tot_swap = 0
    for proc in process[1:]:
        if proc.isnumeric():
            process_name = pid_input(proc)[0]
            tot_phys = pid_input(proc)[1] / 1024
            print(f"Process {process_name}")
            print("Memory usage: {} MB Swap usage: {} MB".format(str(round(tot_phys, 2)), str(round(tot_swap, 2))))
        elif proc.isalpha():
            tot_phys += name_input(proc)["Phys"] / 1024
            tot_swap += name_input(proc)["Swap"] / 1024
            print("Process Name: ", proc)
            print("Memory usage: {} MB Swap usage: {} MB".format(str(round(tot_phys, 2)), str(round(tot_swap, 2))))
    return 0


main(sys.argv)
