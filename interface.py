# This Python file uses the following encoding: utf-8
import json

from paramiko import ssh_exception
from paramiko import SSHClient, AutoAddPolicy
import logging, re
import jc.parsers.iw_scan

class wifiInterface:
    def __init__(self, host_ip, root_password):
        self.ip = host_ip
        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        try:
            print("try to connect to ", host_ip, " with password:", root_password)
            self.ssh.connect(hostname=self.ip, port=22, username=b'root', password=root_password)
        except ssh_exception.NoValidConnectionsError as error:
            logging.error(error)
            return None
        except ssh_exception.AuthenticationException as error:
            logging.error(error)
            return None
        stdin, stdout, stderr = self.ssh.exec_command('uname -a')
        print(stdout.read().decode())
        print(self.ip)
        pass

    def getIfaceNames(self):
        logging.info("try to get wireless device names")
        stdin, stdout, stderr = self.ssh.exec_command('iw dev | grep Interface')
        command_result = stdout.read().decode()
        command_result = command_result.replace('Interface', '').strip().split()
        command_result.sort()
        print(command_result)
        return command_result

    def parse_scan_results(self, scan_results):
        access_points = []
        for line in scan_results:
            m = re.match(r"BSS (\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})\(on wlan\d\)", line)
            if m:
                # New BSS found
                access_point = {'MAC': '', 'FREQ': "",'SSID': '', 'BW':'', 'TYPE': ''}
                access_points.append(access_point)
                access_point['MAC'] = m.groups()[0]
            m = re.match(r"	freq: (\d{4})", line)
            if m:
                access_point["FREQ"] = m.groups()[0]
                continue

            m = re.match(r'^	SSID: (.+)$', line)
            if m:
                access_point["SSID"] = m.groups()[0]
                continue

            m = re.match(r'	HT operation:', line)
            if m:
                access_point["TYPE"] = 'WIFI4'
                continue

            m = re.match('		 \* secondary channel offset: (.+)', line)
            if m:
                sco = m.groups()[0]
                if sco == "no secondary":
                    access_point["BW"] = '20'
                elif sco == "above":
                    access_point["BW"] = '40+'
                elif sco == "below":
                    access_point["BW"] = '40-'
                continue

            m = re.match(r'	VHT operation:', line)
            if m:
                access_point["TYPE"] = 'WIFI5'
                continue

            m = re.match(r'	HE operation:', line)
            if m:
                access_point["TYPE"] = 'WIFI6'

        for ap in access_points:
            print(ap['MAC'], ap["FREQ"], ap["TYPE"], ap["SSID"], ap["BW"])


    def do_scan(self, band, iface_name):
        ap_list = []
        buffer = ''
        command = "jc iw dev " + iface_name + " scan"
        print(command)
        stdin, stdout, stderr = self.ssh.exec_command(command)
        scan_result = json.loads(stdout.read().decode())
        for access_point in scan_result:
            try:
                buffer += access_point['ssid'] + "\t"
                buffer += "wifi4" + "\t"
                buffer += access_point['bssid'] + '\t'
                buffer += "2.4G" + "\t"
                buffer += str(access_point['signal_dbm']) + '\t'
                buffer += str(access_point["primary_channel"]) + '\t'
                buffer += access_point["supported_channel_width"] + '\t'
                buffer += str(access_point["center_freq_segment_1"]) + '\t'
                ap_list.append(buffer)
                buffer = ''
            except KeyError as e:
                continue
        return_list = []
        for ap in ap_list:
            if band != "Full" and ap.split("\t")[2] != band:
                continue
            return_list.append(ap)
        return return_list

if __name__ == "__main__":
    with open("scan_result.txt", 'r') as file:
        lines = file.readlines()
    result = iw_scan.parse(lines)
