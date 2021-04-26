
import numpy as np

def force_angle(angle, unit="rad"):
    # force angle between valid values
    if unit == "rad":
        max = 2*np.pi
    elif unit == "deg":
        max = 360
    if angle > max:
        angle -= max
    elif angle < 0:
        angle += max
    # double check
    if angle > max or angle < 0:
        print("\nsomething's wrong with the angle!\n")
        import pdb; pdb.set_trace()
    return angle
