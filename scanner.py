# This Python file uses the following encoding: utf-8


class wifiscanner:
    def __init__(self):
        pass

    def do_scan(self, band):
        ap_list = ["Netgear97\t11:22:33:44:55:66:77\t2.4G\t20\t1\t2412\t-35Dbm",
                   "Netgear-5G\t22:22:33:44:55:66:77\t5G\t40\t80\t-32Dbm\t5220"]
        return_list = []
        for ap in ap_list:
            if band != "Full" and ap.split("\t")[2] != band:
                continue
            return_list.append(ap)
        return return_list
