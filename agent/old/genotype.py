
class Genotype:
    def __init__(self, energy=10000\
        , r=2.5\
        , max_speed = 5\
        , feed_range=10, feed_rate=10\
        , s_points=100\
        , olf_angle=270, olf_range=25\
        , ir_angle=30, ray_length=50, beam_spread=90\
        , aud_angle=90, aud_range=50\
        , n_in=6, n_hidden=3, n_out=5\
        , ut=0.5, lt=0.1, vt=0.9\
        , W=[], V=[]\
        , plasticity=0):
        self.energy = energy
        self.r = r
        self.max_speed = max_speed
        self.feed_range = feed_range
        self.feed_rate = feed_rate
        self.s_points = s_points
        self.olf_angle = olf_angle
        self.olf_range = olf_range
        self.ir_angle = ir_angle
        self.ray_length = ray_length
        self.beam_spread = beam_spread
        self.aud_angle = aud_angle
        self.aud_range = aud_range
        self.n_in = n_in
        self.n_hidden = n_hidden
        self.n_out = n_out
        self.ut = ut
        self.lt = lt
        self.vt = vt
        self.W = W
        self.V = V
        self.plasticity = plasticity
