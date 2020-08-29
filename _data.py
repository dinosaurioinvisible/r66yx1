

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
        # self.env_info = []
        self.vs_info = []
        self.olf_info = []
        self.e_info = []
        self.com_info = []
        # com channel
        self.com_area = []
        self.com_out = []
        # net
        # self.sm_info = []
        self.e_states = []
        self.h_states = []
        self.vs_attn = []
        self.olf_attn = []
        self.com_vals = []
        # feeding
        self.agent_ax_tx = []
        self.de = []

    def save_ax(self, x, y, o, area, feeding_area, e):
        self.x.append(x)
        self.y.append(y)
        self.o.append(o)
        self.area.append(area)
        self.feeding_area.append(feeding_area)
        self.e.append(e)

    def save_sensors(self, vs_sensors, olf_sensor, vs_info, olf_info, e_info, com_info):
        self.vs_sensors.append(vs_sensors)
        self.olf_sensor.append(olf_sensor)
        self.vs_info.append(vs_info)
        self.olf_info.append(olf_info)
        self.e_info.append(e_info)
        self.com_info.append(com_info)

    def save_com(self, com_area, com_out):
        self.com_area.append(com_area)
        self.com_out.append(com_out)

    def save_nnet(self, e_state, h_state, vs_attn, olf_attn, com_vals):
        # self.sm_info.append(sm_info) # old version
        self.e_states.append(e_state)
        self.h_states.append(h_state)
        self.vs_attn.append(vs_attn)
        self.olf_attn.append(olf_attn)
        self.com_vals.append(com_vals)

    def save_feeding(self, agent_ax_tx, de):
        self.agent_ax_tx.append(agent_ax_tx)
        self.de.append(de)

    def fill_off(self):
        # location (repeat)
        self.x.append(self.x[-1])
        self.y.append(self.y[-1])
        self.o.append(0)
        self.area.append(self.area[-1])
        # feeding and energy
        self.feeding_area.append(None)
        self.e.append(0)
        self.agent_ax_tx.append([0]*len(self.agent_ax_tx[0]))
        self.de.append(0)
        # sensors
        self.vs_sensors.append(None)
        self.olf_sensor.append(None)
        # self.env_info.append([0]*len(self.env_info[0]))
        self.vs_info.append(None)
        self.olf_info.append(None)
        self.e_info.append(None)
        self.com_info.append(None)
        # communication
        # self.com_info.append([0]*len(self.com_info[0]))
        self.com_area.append(None)
        self.com_out.append(None)
        # neural net
        # self.sm_info.append([0]*len(self.sm_info[0]))
        self.e_states.append(None)
        self.h_states.append(None)
        self.vs_attn.append(None)
        self.olf_attn.append(None)
        self.com_vals.append(None)




#
