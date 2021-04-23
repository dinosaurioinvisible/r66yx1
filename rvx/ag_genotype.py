
class Genotype:
    def __init__(self,wx_in,wx_out,thresholds,ga,gb):
        self.r = 5
        self.frange = 2.5
        self.max_speed = 10
        self.wheels_sep = 6
        self.srange = 25
        self.sdos = [-75,-30,30,75]
        self.sangle = 45
        # evolving parameters
        self.wx_in = wx_in
        self.wx_out = wx_out
        self.thresholds = thresholds
        self.ga = ga
        self.gb = gb
