
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
plt.rcParams['animation.ffmpeg_path'] = '/Users/sol/x01/bin'
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon

def sim_animation(world, agents, t, video=False):
    # define plot mode
    # mode = "ga"
    # if len(agents) <= 3:
    #     mode = "group"
    #     # fig, (ax1, ax2) = plt.subplots(2,1)
    #     ax1 = plt.subplots(213)
    #     ax2 = plt.subplots(231)
    #     ax3 = plt.subplots(232)
    #     ax4 = plt.subplots(233)
    #     axs = [ax2, ax3, ax4]
    # else:
    # fig, ax1 = plt.subplots()
    # ax1 = plt.axes(xlim=(0,world.xmax), ylim=(0,world.ymax), aspect="equal")
    # ax1.grid = True
    # time = ax1.text(world.xmax/2, world.ymax+25,str("time: 0"),ha="left",va="top")
    fig = plt.figure()
    ax1 = plt.axes(xlim=(0,world.xmax), ylim=(0,world.ymax), aspect="equal")
    ax1.grid = True
    time = ax1.text(world.xmax/2, world.ymax+25,str("time: 0"),ha="left",va="top")

    # ax1 plt objects
    ags=[]; trajs=[]; olfs=[]; coms=[]; irs=[]; feeds=[]
    for agent in agents:
        ag, = ax1.plot([],[], color="black")
        ags.append(ag)
        feed, = ax1.plot([],[], color="green")
        feeds.append(feed)
        traj, = ax1.plot([],[], color="grey")
        trajs.append(traj)
        ag_irs = []
        for ir_n in range(agent.sensors.vs_n):
            ir, = ax1.plot([],[], color="yellow")
            ag_irs.append(ir)
        irs.append(ag_irs)
        ag_olfs = []
        for olf_n in range(agent.sensors.olf_n):
            olf, = ax1.plot([],[], color="orange")
            ag_olfs.append(olf)
        olfs.append(ag_olfs)
        com, = ax1.plot([],[], color="blue")
        coms.append(com)

    # # remaining ax plt objects
    # if mode=="group":
    #     hmaps=[]; cbars=[]
    #     for enum, agent in enumerate(agents):
    #         n_net = agent.genotype.n_net
    #         hmap, = axs[enum].imshow(np.zeros((n_net,4)))
    #         hmaps.append(hmap)
    #         cbar, = axs[enum].figure.colorbar(hmap)
    #         # cbar.ax2.set_ylabel("heatmap", rotation=90, va="bottom")
    #         cbars.append(cbar)

    anim_running = True
    # to pause the animation and check data
    def onClick(event):
        nonlocal anim_running
        if anim_running:
            anim.event_source.stop()
            anim_running = False
        else:
            anim.event_source.start()
            anim_running = True
        xworld = world
        xagents = agents
        import pdb; pdb.set_trace()

    def init():
        # bound walls are implied, so just trees
        for tree in world.trees:
            # trees
            tx = plt.Circle((tree.x, tree.y), radius=tree.r, color="green", fill=True)
            ax1.add_patch(tx)
        # extra walls
        for wall in world.walls[4:]:
            ax1.plot(*wall.area.xy, color="black")
        return True

    def animate(i):
        time.set_text("time: "+str(i))
        print("\n{}".format(i))
        # for enum, agents
        for enum, agent in enumerate(agents):
            # NOTE: ax1
            # basics
            x = agent.data.x[i]
            y = agent.data.y[i]
            o = agent.data.o[i] if agent.data.o[i] else 0
            e = agent.data.e[i]
            print("\nagent{}: x={}, y={}, o={}, e={}".format(enum,round(x),round(y),round(np.degrees(o)),round(e)))
            # agent body area
            ags[enum].set_data(*agent.data.area[i].exterior.xy)
            # trajectories
            xt = agent.data.x[:i]
            yt = agent.data.y[:i]
            trajs[enum].set_data(xt,yt)

            # sensors and output info (mainly for debugging)
            if e>0:
                vs_info = agent.data.vs_info[i]
                olf_info = agent.data.olf_info[i]
                e_info = agent.data.e_info[i]
                com_info = agent.data.com_info[i]
                net_state = agent.data.net_state[i]
                net_out = agent.data.net_out[i]
                print("vs_info: {}".format(np.around(vs_info,2)))
                print("olf_info: {}".format(np.around(olf_info,2)))
                print("e_info: {}".format(np.around(e_info,2)))
                print("net states:")
                print("hidden: {}".format(np.around(net_state[5:7],2)))
                print("motors: {}".format(np.around(net_state[7:],2)))
                print("net output:")
                print("{}".format(np.around(net_out,2)))
            # sensors
                try:
                    # feeding
                    feeds[enum].set_data(*agent.data.f_area[i].exterior.xy)
                    # vision
                    for nv in range(len(agent.data.vs_sensors[i])):
                        irs[enum][nv].set_data(*agent.data.vs_sensors[i][nv].exterior.xy)
                        # vx = True if vs_info[nv] > 0 else False
                        # irs[enum][nv].set_visible(vx)
                    # olf
                    for no in range(len(agent.data.olf_sensors[i])):
                        olfs[enum][no].set_data(*agent.data.olf_sensors[i][no].exterior.xy)
                        # vx = True if olf_info[no] > 0 else False
                        # olfs[enum][nv].set_visible(vx)
                    # com
                    if agent.genotype.com_n > 0:
                        com_out = agent.data.com_out[i]
                        print("com_info:{}, com_out:{}".format(com_info,com_out))
                        coms[enum].set_data(*agent.data.com_area[i].exterior.xy)
                        vx = True if com_info > 0 else False
                except:
                    import pdb; pdb.set_trace()

                # try:
                #     # NOTE: remaining axs
                #     if mode == "group":
                #         mx = np.zeros((agent.net.n_net, 4))
                #         # input
                #         env_info = np.concatenate((vs_info,olf_info,e_info,com_info,np.zeros((agent.net.n_hidden+agent.net.n_output))))
                #         mx[:,0] += env_info
                #         # internal activity
                #         if i > 0:
                #             mx[:,1] += agent.data.net_state[i-1]
                #         # new internal activity
                #         mx[:,2] += agent.data.net_state[i]
                #         # output
                #         net_output = np.concatenate((np.zeros((agent.net.n_input+agent.net.n_hidden)),agent.data.net_output[i]))
                #         mx[:,3] += net_output
                #         # set new data for heatmap and cbar
                #         hmaps[enum].set_data(mx)
                #         cbar[enum](hmpas)
                #         axs[enum].set_tittle("agent {}".format(enum))
                #         # axs[enum].tight_layout
                # except:
                #     import pdb; pdb.set_trace()
            else:
                feeds[enum].set_data([],[])
                for nv in range(agent.sensors.vs_n):
                    irs[enum][nv].set_data([],[])
                for no in range(agent.sensors.olf_n):
                    olfs[enum][no].set_data([],[])
        # convert from list of lists to one list
        all_irs = [ir for irx in irs for ir in irx]
        all_olfs = [olf for olfx in olfs for olf in olfx]

        return time, tuple(ags)+tuple(trajs)+tuple(feeds)+tuple(all_irs)+tuple(all_olfs)+tuple(coms)

    fig.canvas.mpl_connect('button_press_event', onClick)
    anim = animation.FuncAnimation(fig, animate,
                                        init_func=init,
                                        frames=t,
                                        interval=50,
                                        blit=False,
                                        repeat=False)
    if video:
        # writer for saving the animation
        # xwriter = animation.PillowWriter(fps=30)
        # xwriter = animation.ImageMagickFileWriter(fps=30)
        # xwriter = animation.ImageMagickWriter(fps=30)
        xwriter = animation.FFMpegWriter(fps=30)
        anim.save("Users/sol/desktop/trials/animfile.mp4", writer=xwriter)

    plt.show()
    plt.close()







































#
