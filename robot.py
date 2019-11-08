
import numpy as np
import geometry
import world

#TODO
# after collisions
# urgency fx, to define speed
# parameter/variable to differentiate lw and rw speed

class Robot:
    def __init__(self, x=50, y=50, orientation=0\
    , radius=2.5, wheel_sep=2, n_irs=2):
        self.x = x
        self.y = y
        self.position = np.array([self.x, self.y])
        self.orientation = orientation
        self.radius = radius
        #
        self.wheel_sep = wheel_sep
        self.lw_speed = 5
        self.rw_speed = 5
        #
        self.n_irs = n_irs
        self.irs_angles = []
        self.allocate_irs()
        #
        # urgency parameter between 0 and 1
        self.urgency = 0
        #
        print("\nrobot in {} looking at {}".format(self.position, self.orientation))

    def move(self):
        l_speed, r_speed = self.robot_speed()
        vel = (l_speed+r_speed)/2
        dx = vel*np.sin(self.orientation)
        dy = vel*np.cos(self.orientation)
        do = (l_speed - r_speed)/self.wheel_sep

        # oldx = self.x
        # oldy = self.y
        # oldtheta = self.orientation

        # new x,y and orientation
        # keep x and y within limits
        # force angle between 0 and 2pi
        self.x += dx
        if self.x > world.xmax:
            self.x = world.xmax
        self.y += dy
        if self.y > world.ymax:
            self.y = world.ymax
        self.orientation += do
        self.orientation = geometry.force_angle(self.orientation)

        if collision == True:
            # what to do after collisions?
            # reset after collision
            self.x -= dx
            self.y -= dy
            # self.orientation = oldtheta
            print("collided...")
            self.orientation += np.random.random()
            self.orientation = geometry.force_angle(self.orientation)

    def robot_speed(self):
        # there is no translation from voltage in this case
        # speed = speed % ? % urgency % noise
        # ? = something to get different speeds for lw and rw
        l_speed = self.lw_speed * 1 + self.lw*urgency
        r_speed = self.rw_speed * 1 + self.rw*urgency
        # add random noise from a normal distribution
        l_speed += np.random.randn()
        r_speed += np.random.randn()
        return l_speed, r_speed

    def collision(self):
        # collision with world walls
        for wall in world.walls:
            # wall: line segment [a,b]
            a = np.array(wall[0])
            b = np.array(wall[1])
            if geometry.shortest_dist(a, b, self.position) <= self.radius:
                print("\nposition: {}".format(self.position))
                print("wall, A: {} to B: {}".format(a,b))
                return True

    def allocate_irs(self):
        # sensor only on the top half of the body uniformily distributed
        angle = 0
        angle_sep = 180/(self.n_irs+1)
        for n in self.n_irs:
            # starting from the middle top
            if 90 >= angle >= 270:
                angle = 360 - angle
            else:
                angle += angle_sep
            self.irs_angles.append(np.radians(angle))

    def ir_reading(self):
        for angle in self.irs_angles:
            sensor_angle = self.orientation + angle
            sens_x = self.x + self.radius*np.cos(sensor_angle)
            sens_y = self.y + self.radius*np.sin(sensor_angle)
            # bounding rays relative to a central ir beam
            # sp_left =
            # sp_right =



































































        #
