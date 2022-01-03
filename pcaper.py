
class pcaper:
    def __init__(self, iface, freq, bw, center_freq):
        self.iface = iface
        self.freq = freq
        self.bw = bw
        self.center_freq = center_freq
        pass

    def start(self, path):
        print("start sniffer at channel %s with bandWidth %s using %s" %(self.freq, self.bw, self.iface))
        pass