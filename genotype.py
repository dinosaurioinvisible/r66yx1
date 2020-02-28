
class Genotype:
    def __init__(self, energy=1000\
        , r=2.5\
        , feed_range=10, feed_rate=5\
        , olf_angle=120, olf_range=20\
        , ir_angle=60, ray_length=40, n_rays=4, beam_spread=120\
        , aud_angle=90, aud_range=50\
        , n_in=6, n_hidden=3, n_out=5\
        , ut=0.5, lt=0.1, vt=0.9\
        , W=[], V=[]):
        self.energy = energy
        self.r = r
        self.feed_range = feed_range
        self.feed_rate = feed_rate
        self.olf_angle = olf_angle
        self.olf_range = olf_range
        self.ir_angle = ir_angle
        self.ray_length = ray_length
        self.n_rays = n_rays
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
