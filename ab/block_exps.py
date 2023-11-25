
from auxs import *
from block import *
import os
import networkx as nx


# block
block = mk_gol_pattern('block')

# skip running single exps
run_exps = False

# 1) proto block domains no constraints
if run_exps==True:
    xpn = True
    e0 = False
    ct = False
    print('\n1) e0 = {}'.format(e0))
    if 'pb_domains.gol' in os.listdir():
        pb_domains = load_data(filename='pb_domains.gol')
        print_ac_cases(pb_domains,title='proto-block domains:')
    else:
        pb_domains = get_sxs_from_sy(block,'block',e0=e0,ct=ct,xpn=xpn,print_data=True)
        save_as(pb_domains,name='pb_domains',ext='gol')
# 1331/65536

# 2) proto block domains e0=True:
if run_exps==True:
    xpn = True
    e0 = True
    ct = False
    print('\n2) e0 = {}'.format(e0))
    if 'pb_domains_e0.gol' in os.listdir():
        pb_domains_e0 = load_data(filename='pb_domains_e0.gol')
        print_ac_cases(pb_domains_e0,title='proto-block (e0) domains:')
    else:
        pb_domains_e0 = get_sxs_from_sy(block,'block',e0=e0,ct=ct,xpn=xpn,print_data=True)
        save_as(pb_domains_e0,name='pb_domains_e0',ext='gol')
# 523
# same as e0=False until ac=5, small change for 6, big decay later

# 3) proto block domains expanded=False
# e0 = False
# xpn = False
# ct = False
# print('\n3) expanded = {}'.format(xpn))
# pb_domains_3 = get_sxs_from_sy(block,'block',e0=e0,ct=ct,xpn=xpn,print_data=True)
# 1459
# grows up???
# because 3 is too weird and theoretically worse
# i'll keep expanded=True
xpn = True

# 4.1) apply ct to 1)
if run_exps==True:
    e0 = False
    ct = True
    print('\n4.1) e0 = {}, ct = {}'.format(e0,ct))
    if 'pb_domains_ct.gol' in os.listdir():
        pb_domains_ct = load_data(filename='pb_domains_ct.gol')
        print_ac_cases(pb_domains_ct,title='proto-block (ct) domains:')
    else:
        pb_domains_ct = get_sxs_from_sy(block,'block',e0=e0,ct=ct,xpn=xpn,print_data=True)
        save_as(pb_domains_ct,name='pb_domains_ct',ext='gol')
# 1331 -> 1195
# affects only cases < 7

# 4.2) apply ct to 2)
if run_exps==True:
    e0 = True
    ct = True
    print('\n4.2) e0 = {}, ct = {}'.format(e0,ct))
    if 'pb_domains_e0_ct.gol' in os.listdir():
        pb_domains_e0_ct = load_data(filename='pb_domains_e0_ct.gol')
        print_ac_cases(pb_domains_e0_ct,title='proto-block (e0_ct) domains:')
    else:
        pb_domains_e0_ct = get_sxs_from_sy(block,'block',e0=e0,ct=ct,xpn=xpn,print_data=True)
        save_as(pb_domains_e0_ct,name='pb_domains_e0_ct',ext='gol')
# 523 -> 387
# same as 4.1) for ac=3,4,5. Then, fast decay

# 5.1) apply symmetries to 4.1)
if run_exps==True:
    e0 = False
    ct = True
    sym = True
    print('\n5.1) e0 = {}, ct = {}, sym = {}'.format(e0,ct,sym))
    # pb_domains = get_sxs_from_sy(block,'block',e0=e0,ct=ct,xpn=xpn,print_data=True)
    if 'pb_domains_ct_sms.gol' in os.listdir():
        pb_sms = load_data(filename='pb_domains_ct_sms.gol')
        print_ac_cases(pb_sms,title='pb_domains_ct_sms:')
    else:
        pb_sms = mk_symsets(pb_domains_ct,block,incremental=True,print_data=True)
        save_as(pb_sms,name='pb_domains_ct_sms',ext='gol')
# 1331 -> 1195 -> 110

# 5.2) apply symmetries to 4.2)
if run_exps==True:
    e0 = True
    ct = True
    print('\n5.2) e0 = {}, ct = {}, symsets'.format(e0,ct))
    # pb_domains = get_sxs_from_sy(block,'block',e0=e0,ct=ct,xpn=xpn,print_data=True)
    if 'pb_domains_e0_ct_sms.gol' in os.listdir():
        pb_sms_e0 = load_data(filename='pb_domains_e0_ct_sms.gol')
        print_ac_cases(pb_sms_e0,title='pb_domains_e0_ct_sms:')
    else:
        pb_sms_e0 = mk_symsets(pb_domains_e0_ct,block,incremental=True,print_data=True)
        save_as(pb_sms_e0,name='pb_domains_e0_ct_sms',ext='gol')
# 523 -> 387 -> 13

# 6.1) apply is_in_domain to 5.1)
if run_exps==True:
    print('\n6.1) minsets: e0 = {}, ct = {}, sym = {}'.format(e0,ct,sym))
    pb_minset = mk_minset(pb_sms,print_data=True)
# 1331 -> 1195 -> 110 -> 13

# 6.2) apply is_in_domain to 5.2)
if run_exps==True:
    print('\n6.2) minsets: e0 = {}, ct = {}, sym = {}'.format(e0,ct,sym))
    pb_minset_e0 = mk_minset(pb_sms_e0,print_data=True) 
# 523 -> 387 -> 13 -> 12 

# pb_minset and pb_minset_e0 are almost the same, except that:
# i) pb_minset excludes block as a proto block (pb0 is more basic)
# ii) it adds an extra, similar to another, but yielding e1
# so if we avoid e0 and consider blocks in different doms
# i) the block itself wouldn't be a primary proto-block
# ii) there would be 13 proto-blocks

# 7) do the same, one step back for pb0
if run_exps==True:
    # params
    xpn = True
    e0 = False
    ct = True
    # proto block 0
    print('\n7) proto block 0:')
    pb0 = mk_gol_pattern('pb0')
    # domains
    if 'pb0_domains.gol' in os.listdir():
        pb0_domains = load_data(filename='pb0_domains.gol')
        print_ac_cases(pb0_domains,title='proto-block-0 domains:')
    else: 
        pb0_domains = get_sxs_from_sy(pb0,'pb0',e0=e0,ct=ct,xpn=xpn,print_data=True)
        save_as(pb0_domains,name='pb0_domains',ext='gol')
    # 2864/65536 -> ct: 2712
    # symmetries
    if 'pb0_sms.gol' in os.listdir():
        pb0_sms = load_data(filename='pb0_sms.gol')
        print_ac_cases(pb0_sms,title='proto-block-0 symmetries:')
    else: 
        pb0_sms = mk_symsets(pb0_domains,pb0,incremental=True,print_data=True)
        save_as(pb0_sms,name='pb0_sms',ext='gol')
    # 2864/65536 -> ct: 2712 -> sms: 316
    # minset
    if 'pb0_minset.gol' in os.listdir():
        pb0_ms = load_data(filename='pb0_minset.gol')
        print_ac_cases(pb0_ms,title='proto-block-0 minset:')
    else: 
        pb0_ms = mk_minset(pb0_sms,print_data=True)
        save_as(pb0_ms,name='pb0_minset',ext='gol')
# 2864/65536 -> ct: 2712 -> sms: 316 -> minset: 19

# 8) Same but for the rest of the basic proto blocks 

# General function
def mk_proto_px(px_name,xpn=True,e0=False,ct=True,print_data=True):
    px = mk_gol_pattern(px_name)
    # domains
    file_dxs = 'proto-{}_domains.gol'.format(px_name)
    if file_dxs in os.listdir():
        px_dxs = load_data(filename=file_dxs)
        print_ac_cases(px_dxs,title='proto-{} domains:'.format(px_name))
    else: 
        px_dxs = get_sxs_from_sy(px,px_name,xpn=xpn,e0=e0,ct=ct,print_data=print_data)
        save_as(px_dxs,name='proto-{}_domains'.format(px_name),ext='gol')
    # symsets
    file_sms = 'proto-{}_symsets.gol'.format(px_name)
    if file_sms in os.listdir():
        px_sms = load_data(filename=file_sms)
        print_ac_cases(px_sms,title='proto-{} symsets:'.format(px_name))
    else:
        px_sms = mk_symsets(px_dxs,px,incremental=True,print_data=print_data)
        save_as(px_sms,name='proto-{}_symsets'.format(px_name),ext='gol')
    # minsets
    file_min = 'proto-{}_minset.gol'.format(px_name)
    if file_min in os.listdir():
        px_min = load_data(filename=file_min)
        print_ac_cases(px_min,title='proto-{} minset:'.format(px_name))
    else:
        px_min = mk_minset(px_sms,print_data=print_data)
        save_as(px_min,name='proto-{}_minset'.format(px_name),ext='gol')
    # graph and data
    pxg = nx.DiGraph()
    return px,px_min

# 9) As objects:

# Summary (expanded=True, e0=False):
# protoblocks
# print('\n\nblock\n')
block = mk_gol_pattern('block')
# block = GolPx('block')
# 1331/65536 -> ct: 1195 -> gensms: 145 -> sms: 110 -> min: 13
# proto-pb0 (pacman)
# print('\n\npb0\n')
# pb0 = mk_gol_pattern('pb0')
# pb0 = GolPx('pb0')
# 2864/65536 -> ct: 2712 -> gensms: 358 -> sms: 316 -> min: 19
# proto-pb1 (snake)
# proto-pb2 (helix)

# 10) check sx -> sy, sx = active cells + membrane
if False==True:
    pb0 = expand_domain(pb0)
    pb0_dxs = mk_sx_domains('pb0',membrane=True)
    pb0_dxs,sxys = get_sxys_from_sx(pb0_dxs,pb0)
    # mk basic symsets
    ids35 = sum_in_range(sxys,3,5)
    sms35,sms35_cases,sms35_ids = mk_symsets(sxys[ids35],pb0,incremental=True,return_data=True)
    # save symsets only (23)
    sxys[ids35] = 0
    sxys[ids35[sms35_ids]] = sms35.reshape(sms35.shape[0],sms35.shape[1]*sms35.shape[2])
    # do 6 (212)
    ids6 = sum_is(sxys,6)
    sms6,sms6_cases,sms6_ids = mk_symsets(sxys[ids6],pb0,incremental=False,return_data=True)
    sxys[ids6] = 0
    sxys[ids6[sms6_ids]] = sms6.reshape(sms6.shape[0],sms6.shape[1]*sms6.shape[2])
    # apply minsets

# minimal proto blocks
# e0 = False, ct = True, symsets, minsets + adjacencies
if run_exps:
    minset_pbs = load_data(filename='proto-block_minset.gol')
    pbs = check_adjacency(minset_pbs,arrays=True)
    save_as(pbs,'proto-block_pbs',ext='gol')

# forward proto blocks
if run_exps:
    pbs = load_data(filename='proto-block_pbs.gol')
    pb0 = pbs[0]
    pb0_dxs = mk_sx_domains(pbs[0])
    pb0_dxs,pb0_sxys = get_sxys_from_sx(pb0_dxs,pb0,decay_txs=1)
    # nonzero: 4088/4096, after CT: 3519, after decay=1: 2974 
    pb0_sxys = rm_non_env(pb0_sxys,pb0)
    # this filter doesn't change the total amount, but changes the ca distribution
    # pb0_sms,pb0_sms_cases,pb0_sms_ids = mk_symsets(pb0_sxys,pb0,incremental=True,return_data=True)
    pb0_sms = mk_symsets(pb0_sxys,pb0,incremental=True)
    # general symsets: 499, incremental symsets: 413
    pb0_adj = check_adjacency(pb0_sms)
    # after adjacency (discard discontinuous compositions): 264
    pb0_ftb = check_basic_patterns(pb0_adj)
    # after filtering out basic patterns, present in higher order domains: 
    # pb0_mms = mk_minset(pb0_sms)
    # basic/minimal symsets (not contained by others): 33
    # save_as(pb0_mms,'fwd_pb0.gol')

pb0_adj = load_data(filename='pb0_fwd_adj.gol')
pb0_ftb = check_basic_patterns(pb0_adj)
# pb0_sms = load_data(filename='pb0_fwd_sms.gol')
# pb0_adj = check_adjacency(pb0_sms)
# pb0_mms = mk_minset(pb0_adj)
# pb0_mms = mk_minset(pb0_sms)
# pb0_fwd = check_adjacency(pb0_mms)


