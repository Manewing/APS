#!/usr/bin/python

import sys
import time
import random
import argparse

from environment import Environment

sys.path.append("../common/")
from NodeBase import NodeBase

from gbls import *

# create list of uniformly distributed positions
# count - number of positions
# size  - size of square
def create_uniform(count, size):
    pos = list()
    for l in range(0, count):
        pos.append((rnd(size), rnd(size)))
    return pos

# create list of isotropic distributed positions
# count - number of position
# size  - size of boundaries
def create_isotropic(count, size):
    pos = list()

    sq_num  = int(np.sqrt(count))
    sq_size = size / sq_num
    sq_pos  = dict()

    sq_x    = 0
    sq_y    = 0

    for l in range(0, count):
        x = rnd(sq_size/2) + (0.25+sq_x)*sq_size
        y = rnd(sq_size/2) + (0.25+sq_y)*sq_size
        pos.append((x, y))
        sq_x += 1
        if sq_x >= sq_num:
            sq_x = 0
            sq_y +=1
        if sq_y >= sq_num:
            sq_y = 0

    # shuffle positions
    random.shuffle(pos)
    return pos

def read_pos_file(file_name, count, size):
    pos = list()
    with open(file_name, "r") as f:
        for line in f:

            # ignore comments and empty lines
            if not line.strip():
                continue
            elif line.strip()[0] == '#':
                continue

            line = line.split()
            pos.append((float(line[0]), float(line[1])))

    if len(pos) != count:
        print len(pos), "!=", count
        raise ValueError("not enough positions provided by file: " + file_name)

    return pos

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='APS Simulation')

    parser.add_argument('-v', dest='visual', default=False, \
            help='if set runs visual simulation (default: False)',\
            action="store_true")

    parser.add_argument('-n', dest='nodes', default=50, \
            help='number of normal nodes (default: 50)', type=int)

    parser.add_argument('-l', dest='landmarks', default=0, \
            help='number of landmarks (default: 30 percent of Nodes)', type=int)

    parser.add_argument('-s', dest='size', default=500, \
            help='size of the area the nodes are deployed in (default: 500)', type=int)

    parser.add_argument('-r', dest='radio', \
            default=100, help='radio range of the individual nodes', type=float)

    parser.add_argument('--iso', dest='isotropic', default=False, \
            action='store_true', help='if to use isotropic distribution for nodes')

    parser.add_argument('--rnd', dest='random', default=True, \
            action='store_true', help='if to use uniform distribution (anisotropic) for nodes')

    parser.add_argument('--dist', dest='dist_file', default='', \
            help='if to read node distribution from file', type=str)

    parser.add_argument('-c', dest='cases', default=1, \
            help='number of cases to evaluate (default: 1)', type=int)

    parser.add_argument('-m', dest='method', default='GDM', \
            help='the algorithm to use for MLAT: GDM/GNA (default: GDM)', type=str)

    parser.add_argument('-t', dest='delay', default=45, \
            help='defines simulation speed, delay in frames (default: 45 = 1.5s)', type=int)


    args = parser.parse_args()


    # check parameters
    if args.landmarks == 0:
        args.landmarks = int(float(args.nodes) * 0.3)

    if args.method.upper() != "GDM" and args.method.upper() != "GNA":
        raise ValueError("Invalid Method: " + args.method.upper())

    node_count = args.landmarks + args.nodes
    if args.isotropic:
        pos = create_isotropic(node_count, args.size)
    elif args.dist_file:
        pos = read_pos_file(args.dist_file, node_count, args.size)
    elif args.random:
        pos = create_uniform(node_count, args.size)

    # get node positions
    npos = pos[:args.nodes]

    # get landmark positions
    lpos = pos[args.nodes:]

    # add delay
    NodeBase.PRC_DELAY_MIN += args.delay
    NodeBase.PRC_DELAY_MAX += args.delay
    NodeBase.BRC_DELAY_MIN += args.delay
    NodeBase.BRC_DELAY_MAX += args.delay


    if args.cases == 1:
        env = Environment(args.nodes, args.landmarks, \
                args.size, args.radio, args.method, npos, lpos)
        if args.visual:
            env.run_visual()
        else:
            env.run(True)

    else:
        total_est_err   = 0.0
        total_avg_deg   = 0.0
        total_avg_time  = 0.0
        for l in range(0, args.cases):
            env = Environment(args.nodes, args.landmarks, \
                    args.size, args.radio, args.method, npos, lpos)
            start = time.time()
            env.run(False)
            end = time.time()
            total_avg_time += end - start
            total_est_err  += env.est_err
            total_avg_deg  += env.avg_deg

        print "--------------------------------------------------------------------------------"
        total_est_err   /= args.cases
        total_avg_deg   /= args.cases
        total_avg_time  /= args.cases
        print "Average time elapsed:", total_avg_time
        print "Average Estimation Error:", total_est_err, "Average node degree:", total_avg_deg
        print "--------------------------------------------------------------------------------"

