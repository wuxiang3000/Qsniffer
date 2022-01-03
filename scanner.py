# This Python file uses the following encoding: utf-8


class wifiscanner:
    def __init__(self):
        pass

    def do_scan(self, band):
        ap_list = ["Netgear97\twifi4\t11:22:33:44:55:66:77\t2.4G\t-23Dbm\t1\t20\t2412",
                   "Netgear-5G\twifi5\t22:22:33:44:55:66:77\t5G\t-36Dbm\t36\t80\t5210\t-32Dbm"]
        return_list = []
        for ap in ap_list:
            if band != "Full" and ap.split("\t")[2] != band:
                continue
            return_list.append(ap)
        return return_list
