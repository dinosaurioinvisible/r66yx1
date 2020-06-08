

class Data:
    def __init__(self):
        # starting conditions
        self.x = []
        self.y = []
        self.o = []
        self.area = []
        self.feeding_area = []
        self.e = []
        # sensors
        self.vs_sensors = []
        self.olf_sensor = []
        self.env_info = []
        # com channel
        self.com_area = []
        self.com_info = []
        self.com_out = []
        # net
        self.sm_info = []
        self.e_states = []
        self.h_states = []
        # feeding
        self.ax_tx = []

    def save_ax(self, x, y, o, area, feeding_area, e):
        self.x.append(x)
        self.y.append(y)
        self.o.append(o)
        self.area.append(area)
        self.feeding_area.append(feeding_area)
        self.e.append(e)

    def save_sensors(self, vs_sensors, olf_sensor, env_info):
        self.vs_sensors.append(vs_sensors)
        self.olf_sensor.append(olf_sensor)
        self.env_info.append(env_info)

    def save_com(self, com_area, com_info, com_out):
        self.com_area.append(com_area)
        self.com_info.append(com_info)
        self.com_out.append(com_out)

    def save_nnet(self, sm_info, e_states, h_states):
        self.sm_info.append(sm_info)
        self.e_states.append(e_states)
        self.h_states.append(h_states)

    def save_feeding(self, ax_tx):
        self.ax_tx.append(ax_tx)

#
