
from copy import deepcopy

class Data:
    def __init__(self):
        # starting conditions
        self.x = []
        self.y = []
        self.o = []
        self.area = []
        self.f_area = []
        self.e = []
        # sensors
        self.vs_sensors = []
        self.olf_sensors = []
        self.vs_info = []
        self.olf_info = []
        self.e_info = []
        self.com_info = []
        # net
        self.net_state = []
        self.net_out = []
        # feeding
        self.agent_ax_tx = []
        self.de = []
        # com channel
        self.com_area = []
        self.com_out = []


    def save_ax(self, x, y, o, area, f_area, e):
        self.x.append(x)
        self.y.append(y)
        self.o.append(o)
        self.area.append(area)
        self.f_area.append(f_area)
        self.e.append(e)

    def save_sensors(self, vs_sensors, olf_sensors, vs_info, olf_info, e_info):
        self.vs_sensors.append(vs_sensors)
        self.olf_sensors.append(olf_sensors)
        self.vs_info.append(vs_info)
        self.olf_info.append(olf_info)
        self.e_info.append(e_info)

    def save_nnet(self, net_state, net_out):
        self.net_state.append(deepcopy(net_state))
        self.net_out.append(deepcopy(net_out))

    def save_com(self, com_area, com_info, com_out):
        self.com_area.append(com_area)
        self.com_info.append(com_info)
        self.com_out.append(com_out)

    def fill_off(self):
        # basics for animation
        self.x.append(self.x[-1])
        self.y.append(self.y[-1])
        self.o.append(0)
        self.area.append(self.area[-1])
        self.e.append(0)







#
