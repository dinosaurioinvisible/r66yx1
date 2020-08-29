
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
plt.rcParams['animation.ffmpeg_path'] = '/Users/sol/x01/bin'
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon

#TODO: animation continues from 999 to 0, but does not reset

def sim_animation(world, agents, t=None, video=False, ft=None):
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
    ags=[]; trajs=[]; olfs=[]; coms=[]; irs=[]; feeds=[]
    for agent in agents:
        ag, = plt.plot([],[], color="black")
        ags.append(ag)
        traj, = plt.plot([],[], color="grey")
        trajs.append(traj)
        agent_irs = []
        for ir_n in range(agents[0].sensors.vs_n):
            ir, = plt.plot([],[], color="orange")
            agent_irs.append(ir)
        irs.append(agent_irs)
        olf, = plt.plot([],[], color="yellow")
        olfs.append(olf)
        com, = plt.plot([],[], color="blue")
        coms.append(com)
        feed, = plt.plot([],[], color="blue")
        feeds.append(feed)
    # for deleted objects from agents (when energy = 0)
    del_agents = []

    # to pause the animation and get data
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
        # print time and fitness (plot and terminal)
        if ft:
            time.set_text("time: {}, fitness: {}".format(i,ft))
        else:
            time.set_text("time: "+str(i))
        print("\nt={}".format(i))
        # check if at least some agent is alive, if not stop
        if len(ags) == len(del_agents):
            import pdb; pdb.set_trace()

        # for each agent
        for enum, ag in enumerate(ags):
            # for checking/debugging
            # location (xt, yt) meanwhile, old problem with the np.arrays copies
            x = agents[enum].data.area[i].centroid.x
            y = agents[enum].data.area[i].centroid.y
            # x = agents[enum].data.x[i]
            # y = agents[enum].data.y[i]
            o = agents[enum].data.o[i]
            e = agents[enum].data.e[i]
            print("agent {} - x:{}, y:{}, o:{}".format(enum+1, np.around(x,2), np.around(y,2), np.around(o,2)))

            # print information (if alive)
            if e > 0:
                # feeding
                ag_ax_tx = agents[enum].data.agent_ax_tx[i]
                de = agents[enum].data.de[i]
                print("ag_ax_tx: {}, de={}, e={}".format(ag_ax_tx, np.around(de,2), np.around(e,2)))
                # sm inputs/outputs
                # for old versions:
                try:
                    vs_in = agents[enum].data.vs_info[i]
                    olf_in = agents[enum].data.olf_info[i]
                    vs_attn = agents[enum].data.vs_attn[i]
                    olf_attn = agents[enum].data.olf_attn[i]
                except:
                    sm_info = agents[enum].data.sm_info[i]
                    # vision & olfact
                    vs_n = agents[enum].genotype.vs_n
                    olf_n = agents[enum].genotype.olf_n
                    # input (vis, olf, e, com)
                    vs_in = np.around(sm_info[0:vs_n],2)
                    olf_in = np.around(sm_info[vs_n:vs_n+olf_n],2)
                    # inverted order output (olf, vis, e, com)
                    olf_attn = np.around(agents[enum].data.e_states[i][4:4+olf_n].T,2)
                    vs_attn = np.around(agents[enum].data.e_states[i][4+olf_n:4+olf_n+vs_n].T,2)
                print("sm inputs:")
                print("vision={}, attn outputs={}".format(vs_in, vs_attn))
                print("olfact={}, attn outputs={}".format(olf_in, olf_attn))
                # energy
                if agents[enum].e_in > 0:
                    e_n = olf_n + agents[enum].e_in
                    e_info = np.around(sm_info[olf_n:e_n],2)
                    print("energy={}".format(e_info))
                # communication (if active)
                if agents[enum].com_len > 0:
                    com_in = np.around(sm_info[-agents[enum].com_len:],2)
                    com_out = agents[enum].data.com_out[i]
                    print("com_in={}, com_out={}".format(com_in, com_out))
            else:
                print("death...")

            # agent body area location
            ag.set_data(*agents[enum].data.area[i].exterior.xy)

            # for adjusting sensors indexes
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

            # check if alive and that their objects weren't already deleted
            if e <= 0 and ag not in del_agents:
                # deactivate visibility
                for ir in irs[enumx]:
                    ir.set_visible(False)
                olfs[enumx].set_visible(False)
                feeds[enumx].set_visible(False)
                # delete objects
                del(irs[enumx])
                del(olfs[enumx])
                del(feeds[enumx])
                # the same but for optional com
                if agents[enumx].com_len:
                    coms[enumx].set_visible(False)
                    del(coms[enumx])
                # list as removed (agent)
                del_agents.append(ag)

            # normal case
            all_irs = []
            if e > 0:
                try:
                    # trajectory
                    # xt = agents[enumx].data.x[:i]
                    # yt = agents[enumx].data.y[:i]
                    xt = [a.centroid.x for a in agents[enum].data.area[:i]]
                    yt = [a.centroid.y for a in agents[enum].data.area[:i]]
                    trajs[enumx].set_data(xt,yt)
                    # ir sensors
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
                except:
                    # just in case, for debugging
                    import pdb; pdb.set_trace()
                # stop in the last timestep (temporal i hope)
                if i == t:
                    print("last timestep")
                    import pdb; pdb.set_trace()

        return time, tuple(ags)+tuple(trajs)+tuple(all_irs)+tuple(olfs)+tuple(coms)+tuple(feeds)

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
