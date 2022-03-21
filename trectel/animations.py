
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from agents import RingB
from simulations import ring_gol_trial
from helper_fxs import *

def ringb_animation(ring,ft,trial_data,sim_speed=1000,save_animation=False):

    # 3 subplots (trial, transitions, information)
    fig = plt.figure(figsize=[15,10],constrained_layout=True)
    ax1 = fig.add_subplot(1,3,1)
    ax1.set_title("trial")
    ax2 = fig.add_subplot(1,3,2)
    ax2.set_title("transitions")
    ax3 = fig.add_subplot(1,3,3)
    ax3.set_title("information")
    fig.suptitle("fitness = {}".format(round(ft,2)),ha='center',va='center')
    time = fig.text(0.5,0.94,'',ha='center',va='center')

    # to pause the animation and check data
    anim_running = True
    def onClick(event):
        nonlocal anim_running
        if anim_running:
            anim.event_source.stop()
            anim_running = False
        else:
            anim.event_source.start()
            anim_running = True
        rx,tdx = ring,trial_data
        print("\n\nvars: rx=ring, tdx=trial_data\n")
        import pdb; pdb.set_trace()

    # 0:white, 1:black, 2:cyan, 3:blue, 4:red, 5:green
    palette = np.array([[255,255,255],[0,0,0],[0,255,255],[0,0,255],[255,0,0],[0,255,0]])
    timesteps = len(trial_data)

    # to start
    def init():
        return True

    def animate(i):
        time.set_text("time={}/{}".format(i,timesteps))

        # trial
        world = trial_data[i][0].astype(int)
        for rx,[ri,rj] in enumerate(ring.locs):
            world[ri,rj] += 2
        ax_trial = ax1.imshow(palette[world])

        # transitions

        # information

        return ax_trial

    fig.canvas.mpl_connect('button_press_event',onClick)
    anim=animation.FuncAnimation(fig,animate,
        init_func=init,frames=timesteps,interval=500,blit=False,repeat=True)

    if save_animation:
        if fname == '':
            fname = 'ring_animation_{}'.format(np.random.uniform(0,9999))
        writer = animation.FFMpegWriter(fps=30)
        try:
            anim.save("{}.mp4".format(fname),writer=writer)
        except:
            print("\ncould\'t save animation...\n")
            import pdb; pdb.set_trace()
    plt.show()
    plt.close('all')







def ring_trial_animation(gt=[],fname='',show=True,save=False,trial_mode='gol',sim_speed=500,trial_steps=100,world_size=11,world_th0=0.25):

    # run simulation (for debugging)
    if len(gt)==0:
        gt = np.random.randint(0,2,size=(4,512))
        ij = int(world_size/2)
        ringx = Ring(gt,i=ij,j=ij)
        ft,trial_data = trial(ringx,mode=trial_mode,n_steps=trial_steps,world_size=world_size,world_th0=world_th0,save_data=True)

    # 4 subplots (rows,columns,index)
    fig = plt.figure(figsize=[10,10],constrained_layout=False)
    # animated world grid
    ax1 = fig.add_subplot(2,2,1)
    ax1.set_title("trial")
    # descending states
    ax2 = fig.add_subplot(1,2,2)
    ax2.set_title("system states")
    # transitions
    ax3 = fig.add_subplot(2,2,3)
    ax3.set_title("transitions")

    # title
    fig.suptitle("system fitness = {}".format(round(ft,2)), ha='center', va='center')
    time = fig.text(0.5,0.94,'',ha='center',va='center')

    # to pause the animation and check data
    anim_running = True
    def onClick(event):
        nonlocal anim_running
        if anim_running:
            anim.event_source.stop()
            anim_running = False
        else:
            anim.event_source.start()
            anim_running = True
        gx,data = gt,trial_data
        print("\n\ngx,data = gt,trial_data\n")
        import pdb; pdb.set_trace()

    # colors for imshow
    # white=255,255,255 - black:0,0,0
    # green=0,255,0 dark green=0,128,0 - yellow=255,255,0
    # red=255,0,0 - magenta=255,0,255 - blue=0,0,255 - cyan=0,255,255
    # 0:white, 1:black, 2:cyan, 3:blue, 4:red, 5:green
    palette = np.array([[255,255,255],[0,0,0],[0,255,255],[0,0,255],[255,0,0],[0,255,0]])
    # grid for descending states
    global flat_sts
    flat_sts = np.zeros((100,21))

    # to start
    def init():
        return True

    def animate(i):
        time.set_text("time={}/{}".format(i,trial_steps))

        # ax1: trial animation
        grid = np.zeros((7,7))
        # world: 0=off (and unknown), 1=on > white, black
        world,world_st,ring_st,core_st = trial_data[i]
        # ring: 2=off, 3=on > cyan, blue
        ring = int2arr(ring_st,arr_len=4)+2
        # locations
        xy = int(world.shape[0]/2)
        world[xy-1,xy] = ring[0]
        world[xy,xy-1] = ring[1]
        world[xy,xy+1] = ring[2]
        world[xy+1,xy] = ring[3]
        # core: 4=off, 5=on > red, green
        world[xy,xy] = core_st+4
        # broadcast colors
        # grid[1:6,1:6] = world
        world_rgb = palette[world.astype(int)]
        world_im = ax1.imshow(world_rgb)

        # ax2 : descending sts
        flat_sti = world[xy-2:xy+3,xy-2:xy+3].flatten()
        # delete corners outside env
        for sx in [24,20,4,0]:
            flat_sti = np.delete(flat_sti,sx)
        # update
        flat_sts[i] = flat_sti
        # broadcast colors
        flat_sts_rgb = palette[flat_sts.astype(int)]
        flat_sts_im = ax2.imshow(flat_sts_rgb)

        # ax3: transitions

        return world_im,flat_sts_im

    fig.canvas.mpl_connect('button_press_event', onClick)
    anim=animation.FuncAnimation(fig,animate,
        init_func=init,frames=trial_steps,interval=500,blit=False,repeat=True)

    if save:
        if fname == '':
            fname = 'ring_animation_{}'.format(np.random.uniform(0,9999))
        writer = animation.FFMpegWriter(fps=30)
        try:
            anim.save("{}.mp4".format(fname),writer=writer)
        except:
            print("\ncould\'t save animation...\n")
            import pdb; pdb.set_trace()
    if show:
        plt.show()
    plt.close('all')









#
