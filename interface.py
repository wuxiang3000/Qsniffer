# This Python file uses the following encoding: utf-8
import json
import socket

from paramiko import ssh_exception
from paramiko import SSHClient, AutoAddPolicy
import logging
import re
import jc.parsers.iw_scan


class WifiInterface:
    def __init__(self, host_ip, root_password):
        self.ip = host_ip
        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        try:
            print("try to connect to ", host_ip, " with password:", root_password)
            self.ssh.connect(hostname=self.ip, port=22, username=b'root', password=root_password, timeout=10)
        except (ssh_exception.NoValidConnectionsError,ssh_exception.AuthenticationException,socket.timeout):
            logging.error("ssh connect error")
            self.ssh_connected = False
            return None
        else:
            self.ssh_connected = True

        stdin, stdout, stderr = self.ssh.exec_command('uname -a')
        print(stdout.read().decode())
        print(self.ip)
        pass

    def getIfaceNames(self):
        logging.info("try to get wireless device names")
        if self.ssh_connected is not True:
            return ["NA"]
        stdin, stdout, stderr = self.ssh.exec_command('iw dev | grep Interface')
        command_result = stdout.read().decode()
        command_result = command_result.replace('Interface', '').strip().split()
        command_result.sort()
        print(command_result)
        return command_result

    def do_scan(self, band, iface_name):
        band_to_string = ['NA', '2.4G', '5G', '6G']
        ap_list = []
        print('selected band:', band)
        if iface_name != "NA":
            command = "iw " + iface_name + " scan"
            print(command)
            stdin, stdout, stderr = self.ssh.exec_command(command)
            scan_result = json.loads(stdout.read().decode())
        else:
            with open("scan_result.txt.bak", 'r') as file:
                lines = file.read()
            scan_result = jc.parsers.iw_scan.parse(lines)
        scan_result_sorted = sorted(scan_result, key=lambda d: d['signal_dbm'], reverse=True)
        # with open('scan_result.json', 'w') as file:
        #     json.dump(scan_result_sorted, file, indent=4)
        for ap in scan_result_sorted:
            try:
                # [0] is SSID
                buffer = ap['ssid'] + "\t"
                # [1] is standard: WiFi4/5/6
                if 'vht_rx_highest_supported_mbps' in ap.keys() and ap['vht_rx_highest_supported_mbps'] != 0:
                    buffer += "wifi5" + "\t"
                elif 'ht_rx_mcs_rate_indexes_supported' in ap.keys() or 'ht_tx/rx_mcs_rate_indexes_supported' in ap.keys():
                    buffer += "wifi4" + "\t"
                else:
                    buffer += "wifi3" + "\t"
                # [3] is BSSID
                buffer += ap['bssid'] + '\t'
                # [4] is Band
                if 'freq' in ap.keys():
                    if 2412 <= ap['freq'] <= 2484 and (band == '2G' or band == 'Full'):
                        buffer += '2G\t'
                    elif 5035 <= ap['freq'] <= 5980 and (band == '5G' or band == 'Full'):
                        buffer += '5G\t'
                    elif 5955 <= ap['freq'] <= 7117 and (band == '6G' or band == 'Full'):
                        buffer += '6G\t'
                    else:
                        logging.info("No matching AP by selected band:%s, freq:%s" %(band, ap['freq']))
                        continue
                else:
                    logging.error("No freq info of AP:", ap['ssid'])
                    continue

                buffer += str(ap['signal_dbm']) + 'Dbm\t'
                buffer += str(ap["primary_channel"]) + '\t'
                if 'channel_width' in ap.keys():
                    if ap['channel_width'] == '0 (20 or 40 MHz)':
                        if ap['secondary_channel_offset'] == 'above':
                            buffer += '40+\t'
                        elif ap['secondary_channel_offset'] == 'below':
                            buffer += '40-\t'
                        else:
                            buffer += '20\t'
                    elif ap['channel_width'] == '1 (80 MHz)':
                        buffer += '80\t'
                else:
                    buffer += '20\t'
                buffer += str(ap["center_freq_segment_1"]) + '\t'
                buffer += str(ap["center_freq_segment_2"]) + '\t'
                ap_list.append(buffer)
            except KeyError as e:
                continue
        return_list = []
        for ap in ap_list:
            return_list.append(ap)
        return return_list

if __name__ == "__main__":
    wifiInterface().do_scan("Full", "wlan0")
