
import world
import geometry
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import matplotlib.animation as animation

# agent ps = [ir_range, ir_angles, olf_range, olf_angles, aud_range, aud_angles]
# agent states = [ir1, ir2, olf, aud1, aud2, e]
# agent positions = [x, y, o]

def sim_animation(limits, walls, trees, agents, past=True, start=True):
    # defs
    fig = plt.figure()
    ax = plt.axes(xlim=(0,limits[0]), ylim=(0,limits[1]), aspect="equal")
    # plot basics for agents
    agent_objs = []
    olf_domain = []
    aud_domain = []
    vis_domain = []
    # agent objects
    for agent in agents:
        # create objects
        agent_obj = plt.Circle((agent.positions[0][0],agent.positions[0][1]), radius=agent.r, color="blue", fill=True)
        agent_objs.append(agent_obj)
        olf = Wedge((0,0), r=agent.ps[2], theta1=0, theta2=0, color="purple", fill=False, visible=False)
        olf_domain.append(olf)
        aud_left = plt.Circle((0,0), radius=agent.ps[4], color="red", fill=False, visible=False)
        aud_right = plt.Circle((0,0), radius=agent.ps[4], color="red", fill=False, visible=False)
        aud_domain.append([aud_left, aud_right])
        ir_left = Wedge((0,0), r=agent.ps[0], theta1=0, theta2=0, color="orange", fill=False, visible=False)
        ir_right = Wedge((0,0), r=agent.ps[0], theta1=0, theta2=0, color="orange", fill=False, visible=False)
        vis_domain.append([ir_left, ir_right])

    def init():
        # optional walls
        for wall in walls:
            ax.plot([wall.xmin, wall.ymin], [wall.xmax, wall.ymax], color="black")
        # trees
        for tree in trees:
            t = plt.Circle((tree.x, tree.y), radius=tree.r, color="green", fill="True")
            ax.add_patch(t)
        # agents and sensors
        for agent in agent_objs:
            ax.add_patch(agent)
        for olf in olf_domain:
            ax.add_patch(olf)
        for aud in aud_domain:
            for audx in aud:
                ax.add_patch(audx)
        for ir in vis_domain:
            for irx in ir:
                ax.add_patch(irx)
        return agent, olf, audx, irx,

    def animate(i):
        # for each agent in the list of animated objects
        for enum, agent_obj in enumerate(agent_objs):
            # location data
            o = np.degrees(agents[enum].positions[i][2])
            x = agents[enum].positions[i][0]
            y = agents[enum].positions[i][1]
            # agent (circle)
            agent_obj.center = (x, y)
            # olf domain (wedge)
            olf_x = x + agents[enum].r*np.cos(np.radians(o))
            olf_y = y + agents[enum].r*np.sin(np.radians(o))
            olf_o1 = geometry.force_angle_degrees(np.degrees(agents[enum].ps[3][0])+o)
            olf_o2 = geometry.force_angle_degrees(np.degrees(agents[enum].ps[3][1])+o)
            olf_domain[enum].center = (olf_x,olf_y)
            olf_domain[enum].theta1 = olf_o1
            olf_domain[enum].theta2 = olf_o2
            olf_domain[enum]._recompute_path()
            # signals
            #olf_domain[enum].set_visible = False
            olf_val = agents[enum].states[i][2]
            if olf_val > 0:
                print(olf_val)
                olf_domain[enum].visible = True
            # aud domain (circles)
            for n in range(len(aud_domain[enum])):
                aud_o = o + agents[enum].ps[5][n]
                aud_x = x + agents[enum].r*np.cos(aud_o)
                aud_y = y + agents[enum].r*np.sin(aud_o)
                aud_domain[enum][n].center = (aud_x, aud_y)
                # signal
                #aud_domain[enum][n].set_visible = False
                aud_val = agents[enum].states[i][3+n]
                if aud_val > 0:
                    print(aud_val)
                    aud_domain[enum][n].set_visible = True
            # vis domain (wedges)
            for n in range(len(vis_domain[enum])):
                vis_o = geometry.force_angle(agents[enum].positions[i][2]+agents[enum].ps[1][n])
                vis_x = x + agents[enum].r*np.cos(vis_o)
                vis_y = y + agents[enum].r*np.sin(vis_o)
                # esto manual por ahora (beam spread = 120)
                vis_o1 = geometry.force_angle_degrees(np.degrees(vis_o)-60)
                vis_o2 = geometry.force_angle_degrees(np.degrees(vis_o)+60)
                vis_domain[enum][n].center = (vis_x, vis_y)
                vis_domain[enum][n].theta1 = vis_o1
                vis_domain[enum][n].theta2 = vis_o2
                vis_domain[enum][n]._recompute_path()
                # signals
                #vis_domain[enum][n].set_visible = False
                vis_val = agents[enum].states[i][n]
                if vis_val > 0:
                    print(vis_val)
                    vis_domain[enum][n].set_visible = True
            # check energy values
            energy = agents[enum].states[i][5]
            if energy <= 25 and energy > 0:
                agent_obj.set_color("red")
            if energy <= 0:
                agent_obj.set_color("black")
                agent_obj.fill = False
                olf_domain[enum].set_visible =False
                aud_domain[enum][0].set_visible = False
                aud_domain[enum][1].set_visible = False
                vis_domain[enum][0].set_visible = False
                vis_domain[enum][1].set_visible = False
            all_aud = [aud for audx in aud_domain for aud in audx]
            all_vis = [vis for visx in vis_domain for vis in visx]

        return tuple(agent_objs)+tuple(olf_domain)+tuple(all_aud)+tuple(all_vis)

    anim = animation.FuncAnimation(fig, animate,
                                        init_func=init,
                                        frames=100,
                                        blit=True)
    plt.show()





























#
