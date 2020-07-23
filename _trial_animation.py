
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
plt.rcParams['animation.ffmpeg_path'] = '/Users/sol/x01/bin'
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon

#TODO:


def sim_animation(world, agents, t=None, video=False):
    # time steps
    if t==None:
        t = len(agents[0])
    # def
    fig = plt.figure()
    ax = plt.axes(xlim=(0,world.xmax), ylim=(0,world.ymax), aspect="equal")
    ax.grid = True
    time = ax.text(world.xmax/2, world.ymax+10,str("time: 0"),ha="left",va="top")
    anim_running = True
    # plot basics for agents
    ags = []; olfs = []; coms = []; irs = []; feeds = []
    for agent in agents:
        ag, = plt.plot([],[], color="black")
        ags.append(ag)
        agent_irs = []
        for ir_n in range(agents[0].sensors.vs_n):
            ir, = plt.plot([],[], color="orange")
            agent_irs.append(ir)
        irs.append(agent_irs)
        olf, = plt.plot([],[], color="yellow")
        olfs.append(olf)
        com, = plt.plot([],[], color="blue")
        coms.append(com)
        feed, = plt.plot([],[], color="grey")
        feeds.append(feed)
    # for deleted objects from agents (when energy = 0)
    del_agents = []

    # to pause the animation
    def onClick(event):
        nonlocal anim_running
        if anim_running:
            anim.event_source.stop()
            anim_running = False
        else:
            anim.event_source.start()
            anim_running = True
        xworld = world
        xags = agents
        import pdb; pdb.set_trace()

    def init():
        # optional walls, trees and initial locations
        for wall in world.walls[4:]:
            ax.plot(*wall.area.xy)
            # ax.plot([wall.xmin, wall.xmax], [wall.ymin, wall.ymax], color="black")
        for tree in world.trees:
            # ax.plot(*tree.area.exterior.xy, color="green")
            tx = plt.Circle((tree.x, tree.y), radius=tree.r, color="green", fill=True)
            ax.add_patch(tx)
        return True

    def animate(i):
        time.set_text("time: "+str(i))
        # for each agent
        print("\nt={}".format(i))
        for enum, ag in enumerate(ags):
            # for debugging
            x = agents[enum].data.x[i]
            y = agents[enum].data.y[i]
            o = agents[enum].data.o[i]
            ag_ax_tx = agents[enum].data.agent_ax_tx[i]
            de = agents[enum].data.de[i]
            e = agents[enum].data.e[i]
            sm_info = agents[enum].data.sm_info[i]
            com_out = agents[enum].data.com_out[i]
            print("agent {} - x:{}, y:{} o:{}".format(enum+1, np.around(x,2), np.around(y,2), np.around(o,2)))
            print("ag_ax_tx: {}, de={}, e={}".format(ag_ax_tx, np.around(de,2), np.around(e,2)))
            print("sm_info: {} > com_out: {}".format([np.around(i,2) for i in sm_info],com_out))

            # agent body area location
            ag.set_data(*agents[enum].data.area[i].exterior.xy)

            # for adjusting sensors index
            if enum == 0:
                enumx = enum
            else:
                # check if previous agents are alive
                ags_e = np.array([a.data.e[i] for a in agents[:enum]])
                ags_alive = np.where(ags_e>0,1,0)
                # if all agents (up to here) are alive
                if enum == sum(ags_alive):
                    enumx = enum
                else:
                    # previous dead agents
                    ags_dead = sum(np.where(ags_e<=0,1,0))
                    enumx = enum - ags_dead

            # enumx = enum-len(del_agents) if enum > 0 else enum
            # # if agent 0 alive and agent 2 dead: agent 1 -> enumx=1
            # # if agent 0 dead and agent 2 alive: agent 1 -> enumx=0
            # # if agent 0 dead and agent 2 dead: agent 1 ->
            # if enum == 1 and enumx == 0 and len(irs) == 1:
            #     enumx = 1

            # check if alive and that they objects weren't already deleted
            if e <= 0 and ag not in del_agents:
                # deactivate visibility
                for ir in irs[enumx]:
                    ir.set_visible(False)
                olfs[enumx].set_visible(False)
                feeds[enumx].set_visible(False)
                if agents[enumx].com_len:
                    coms[enumx].set_visible(False)
                # delete objects
                del(irs[enumx])
                del(olfs[enumx])
                del(feeds[enumx])
                del(coms[enumx])
                del_agents.append(ag)
            # normal case
            if e > 0:
                # ir sensors
                try:
                    for n in range(len(irs[enumx])):
                        irs[enumx][n].set_data(*agents[enum].data.vs_sensors[i][n].exterior.xy)
                        # vx = True if agents[enum].data.env_info[i][n] != 0 else False
                        # irs[enumx][n].set_visible(vx)
                        irs[enumx][n].set_visible(True)
                    all_irs = [ir for irx in irs for ir in irx]
                    # olf sensor
                    olfs[enumx].set_data(*agents[enum].data.olf_sensor[i].exterior.xy)
                    # vx = True if agents[enum].data.env_info[i][-1] != 0 else False
                    # olfs[enumx].set_visible(vx)
                    olfs[enumx].set_visible(True)
                    # feeding info
                    feeds[enumx].set_data(*agents[enum].data.feeding_area[i].exterior.xy)
                    # communication info
                    if agents[enum].data.com_area[i]:
                        coms[enumx].set_data(*agents[enum].data.com_area[i].exterior.xy)
                        com_array = np.array(agents[enum].data.com_info[i])
                        vx_com = sum(np.where(com_array!=0,1,0))
                        vx = True if vx_com != 0 else False
                        coms[enumx].set_visible(vx)
                    else:
                        coms = []
                except:
                    import pdb; pdb.set_trace()
            # in case all agents are dead
            if len(ags) == len(del_agents):
                all_irs = []

        return time, tuple(ags)+tuple(all_irs)+tuple(olfs)+tuple(coms)+tuple(feeds)

    fig.canvas.mpl_connect('button_press_event', onClick)
    anim = animation.FuncAnimation(fig, animate,
                                        init_func=init,
                                        frames=t,
                                        interval=50,
                                        blit=False)
    if video:
        # writer for saving the animation
        # xwriter = animation.PillowWriter(fps=30)
        # xwriter = animation.ImageMagickFileWriter(fps=30)
        # xwriter = animation.ImageMagickWriter(fps=30)
        xwriter = animation.FFMpegWriter(fps=30)
        anim.save("Users/sol/desktop/trials/animfile.mp4", writer=xwriter)#, fps=30)#, extra_args=["-vcodec", "libx264"])

    plt.show()
    plt.close()



























#
