
def encode_genome(ut=0.5,lw=0.1,lr=0.5,hu=5):
    genome = [hu,ut,lt,lr]
    return genome











# 3 chromosomes (controller, vision, food)

# chromosome:
# [ [IN1][IN2][IN3] [N1][N2][N3][N4]...[Nn] [OUT1][OUT2] ]
    # node:
    # [ [MK] [NS] [LS1][LS2][LS3][LS4]...[LNn] ]
    # MK: marker (X, Y, Z)
    # NS: node specifications
    # LS: link specifications
        # link:
        # [ [CX] [V] [J] ]
        # CX: connection type (fwds/bkwds, rel/abs)
        # V: normal/veto
        # J: size of jump

#ch_in = [["X"][90][5][0.5]]
#ch_hidden = [][][]
#ch_out = [][][]
#genome = 0
#initial_genome = [ [["X"][90][0.5][ [] ]]

# def encode_genome(n_in=3, n_hidden=5, n_out=2\
#     , threshold=5, links=10\
#     , cx="F", veto=False, jump=1):
#     nodes = ""
#     for n in range(n_in):
#         node = ""
#         marker = "X"
#         threshold = threshold
#         n_links = n_hidden
#         node += marker+str(threshold)
#         for l in range(n_links):
#             cx = cx
#             veto = "N" if veto==False else "V"
#             jump = str(jump)
#             node += cx+veto+jump
#         nodes += node
#     for n in range(n_hidden):
#         node = ""
#         marker = "Y"
#         threshold = threshold
#         n_links = n_hidden
#         node += marker+str(threshold)
#         for l in range(n_links):
#             cx = cx
#             veto = veto = "N" if veto==False else "V"
#             jump = str(jump)
#             node += cx+veto+jump
#         nodes += node
#     for n in range(n_output):
#         node = ""
#         marker = "Z"
#         threshold = threshold
#         n_links = n_output
#         node += marker+str(threshold)
#         for l in range(n_links):
#             cx = cx
#             veto = veto = "N" if veto==False else "V"
#             jump = str(jump)
#             node += cx+veto+jump
#
#
#     "XXXYYYYYZZ"
#     "[X5]"
#     "[FN][FN][FN][FN][FN]"
#
# def decode_genome(genome, ir_in=2, fs_in=2, n_out=2):
#     robot = robot_agent.Robot()
#     # chromosome 0: ir input
#     robot.ir_angle = genome[0][0]
#     robot.ir_spread = genome[0][1]
#     robot.ir_range = genome[0][2]
#     # chromosome 1: fs input
#     robot.fs_angle = genome[1][0]
#     robot.fs_range = genome[1][1]
#     # chromosome 2: controller
#     robot_net = robot_net.RNN()
#     self.ir_input_dims = ir_in
#     self.fs_input_dims = fs_in
#     self.output_dims = n_out
#     self.hidden_dims = len(genome[2])-n_in-n_out
#     for node in genome[2]:
#         marker = node[0]
#         threshold = node[1]
#         #learning_rate = node[2]
#         # links from each node
#         for link in node[3]:
#             link_cx = link[0]
#             link_veto = link[1]
#             link_jump = link[2]
