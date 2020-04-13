
import world
import geometry
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import matplotlib.animation as animation

# agent states = [ir1, ir2, olf, aud1, aud2, e]
# agent positions = [x, y, o]
# agent feeding_states = [Bool]

def sim_animation(lifetime, limits, walls, trees, agents):
    # defs
    fig = plt.figure()
    ax = plt.axes(xlim=(0,limits[0]), ylim=(0,limits[1]), aspect="equal")
    ax.grid = True
    # for time
    time = ax.text(limits[0]/2, limits[1]+10,str("time: 0"),ha="left",va="top")
    # plot basics for agents
    agent_objs = []
    o_lines = []
    olf_domain = []
    aud_domain = []
    vis_domain = []
    feed_domain = []
    # agent objects
    for agent in agents:
        # create objects
        # agent
        ag = plt.Circle((agent.positions[0][0],agent.positions[0][1]), radius=agent.r, color="blue", fill=True)
        agent_objs.append(ag)
        # orientation line
        o_line, = plt.plot([],[], color="orange")
        o_lines.append(o_line)
        # olfactory domain
        olf, = plt.plot([],[], color="grey")
        olf_domain.append(olf)
        # auditory domain
        aud_left = plt.Circle((0,0), radius=agent.genotype.aud_range, color="red", fill=False, visible=False)
        aud_right = plt.Circle((0,0), radius=agent.genotype.aud_range, color="red", fill=False, visible=False)
        aud_domain.append([aud_left, aud_right])
        # visual domain
        #ir_left = Wedge((0,0), r=agent.genotype.ray_length, theta1=0, theta2=0, color="grey", fill=False, visible=True)
        #ir_right = Wedge((0,0), r=agent.genotype.ray_length, theta1=0, theta2=0, color="grey", fill=False, visible=True)
        #vis_domain.append([ir_left, ir_right])
        ir_left, = plt.plot([],[], color="grey")
        ir_right, = plt.plot([],[], color="grey")
        vis_domain.append([ir_left, ir_right])
        # feeding domain
        feed = plt.Circle((0,0), radius=(agent.feed_range+agent.r), color="green", fill=False, visible=False)
        feed_domain.append(feed)

    def init():
        # optional walls
        for wall in walls:
            ax.plot([wall.xmin, wall.xmax], [wall.ymin, wall.ymax], color="black")
        # trees
        for tree in trees:
            t = plt.Circle((tree.x, tree.y), radius=tree.r, color="green", fill="True")
            ax.add_patch(t)
        # agents and sensors (not necessary for orientation)
        for agent in agent_objs:
            ax.add_patch(agent)
        for aud in aud_domain:
            for audx in aud:
                ax.add_patch(audx)
        for feed in feed_domain:
            ax.add_patch(feed)
        return agent, audx, feed,

    def animate(i):
        # time
        time.set_text("time: "+str(i))
        # for each agent in the list of animated objects
        for enum, agent_obj in enumerate(agent_objs):
            # location data
            o = np.degrees(agents[enum].positions[i][2])
            x = agents[enum].positions[i][0]
            y = agents[enum].positions[i][1]
            # agent body (circle)
            agent_obj.center = (x, y)
            agent_obj.set_color("blue")

            # agent orientation (line from center)
            ox = x + agents[enum].r * np.cos(np.radians(o))
            oy = y + agents[enum].r * np.sin(np.radians(o))
            o_lines[enum].set_data([x,ox],[y,oy])

            # olf domain (shapely polygon)
            olf_domain[enum].set_data(*agents[enum].sensors.sensory_domain["olf"][i].exterior.xy)
            # olf signals
            olf_val = agents[enum].states[i][2]
            print("time: {}, location: {},{}, agent: {}, olf_val: {}".format(i,round(x,2),round(y,2),enum,olf_val))
            if olf_val > 0:
                # olf_domain[enum].set_visible(True)
                olf_domain[enum].set_color("purple")
            else:
                # olf_domain[enum].set_visible(False)
                olf_domain[enum].set_color("grey")

            # aud domain (circles)
            for n in range(len(aud_domain[enum])):
                #aud_o = o + agents[enum].ps[5][n]
                aud_o = o + agents[enum].sensors.aud_angles[n]
                aud_x = x + agents[enum].r*np.cos(aud_o)
                aud_y = y + agents[enum].r*np.sin(aud_o)
                aud_domain[enum][n].center = (aud_x, aud_y)
                # auditory signal
                aud_val = agents[enum].states[i][3+n]
                # if aud_val > 0:
                #     aud_domain[enum][n].set_visible(True)
                # else:
                #     aud_domain[enum][n].set_visible(False)

            # vis domain (wedges)
            for n in range(len(vis_domain[enum])):
                # get polygon
                vis_domain[enum][n].set_data(*agents[enum].sensors.sensory_domain["vis"][i][n].exterior.xy)
                # visual signals
                vis_val = agents[enum].states[i][n]
                # print("time: {}, location: {},{}, agent: {}, sensor: {}, vis_val: {}".format(i,round(x,2),round(y,2),enum,n,vis_val))
                if vis_val > 0:
                    # vis_domain[enum][n].set_visible(True)
                    vis_domain[enum][n].set_color("yellow")
                else:
                    # vis_domain[enum][n].set_visible(False)
                    vis_domain[enum][n].set_color("grey")

            # feeding (circle)
            if agents[enum].feeding_states[i] == True:
                feed.center = (x,y)
                feed.set_visible(True)
            else:
                feed.set_visible(False)

            # check energy values (circle)
            energy = agents[enum].states[i][5]
            if 0 < energy <= 200:
                agent_obj.set_color("grey")
                agent_obj.fill = False
            if energy <= 0:
                agent_obj.set_color("black")
                agent_obj.fill = False
                olf_domain[enum].set_visible(False)
                aud_domain[enum][0].set_visible = False
                aud_domain[enum][1].set_visible = False
                vis_domain[enum][0].set_visible(False)
                vis_domain[enum][1].set_visible(False)
            all_aud = [aud for audx in aud_domain for aud in audx]
            all_vis = [vis for visx in vis_domain for vis in visx]

        return time, tuple(agent_objs)+tuple(o_lines)+tuple(olf_domain)+tuple(all_aud)+tuple(all_vis)+tuple(feed_domain)

    anim = animation.FuncAnimation(fig, animate,
                                        init_func=init,
                                        frames=lifetime,
                                        interval=200,
                                        blit=False)
    plt.show()



























#
