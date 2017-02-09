# Simple Node
import sys
import random
import numpy as np
import pygame

from action import *
from data import *
from gbls import *

sys.path.append("../common/")
import node_base

class Node(node_base.node):

    __ID = 0

    def __init__(self, x, y, ss):
        # pass position in meters to parent
        node_base.node.__init__(self, x, y)

        # set id of node
        self.id = Node.__ID
        Node.__ID += 1

        # signal strength in meters
        self.ss = ss

        # hopsize (estimated)
        self.hopsize = 0

        # reference of the last correction
        self.last_corr = None

        # keep track of number queued broadcasts
        self.broadcasts = 0

        # table for landmark information
        self.table = dict()

        # estimated position of node
        self.u = None

        # degree of node
        self.degree = 0

    def determine_degree(self, env):
        # get degree from Environment
        self.degree = env.get_degree(self.pos, self.ss)

    def schedule_broadcast(self, env, data):
        # create new broadcast action
        action = ActionBroadcast(self, env, data)

        # schedule broadcast
        env.action_manager.queue_random(action, DELAY, DELAY+5)

        # increase number of queue broadcasts
        self.broadcasts += 1

    def broadcast(self, env, data):
        # broadcast at node position with signal strength some data
        env.broadcast(self.pos, self.ss, data)

        # decrease number of queued broadcasts
        self.broadcasts -= 1

    def schedule_process(self, env, data):
        # create new process action_manager
        action = ActionProcess(self, env, data)

        # schedule process
        env.action_manager.queue_random(action, DELAY, DELAY+5)

    def process(self, env, data):
        self.schedule_broadcast(env, data)

    def valid_entry(self, data):
        if not isinstance(data, NodeTEntry):
            return False
        if data.landmark in self.table:
            return False
        if data.landmark == self: # only landmarks True
            return False
        return True

    def valid_correction(self, data):
        if not isinstance(data, Correction):
            return False

        # initial correction
        if self.last_corr == None:
            self.last_corr = data
            return True

        if self.last_corr.landmark == data.landmark \
                and self.last_corr.number < data.number:
            self.last_corr = data
            return True

        return False


    def receive(self, env, data):
        # we received data
        if self.valid_entry(data):
            #print "N:", self.id, "received new data packet (NodeTEntry)"
            #data.dump()

            # save copy of data in table
            self.table[data.landmark] = data.copy()

            # create new data packet
            new_data = data.copy()
            new_data.value += 1 # TODO allow distance
            new_data.sender = self

            # schedule broadcast of new data
            self.schedule_broadcast(env, new_data)

        elif self.valid_correction(data):
            #print "N:", self.id, "received new data packet (Correction)"
            #data.dump()

            # update hopsize
            self.hopsize = data.hopsize

            # schedule broadcast of copy of data
            new_data = data.copy()
            self.schedule_process(env, new_data)

        else:
            # drop data
            #print "N:", self.id, "dropped data packet"
            return

        return

    def set_random_pos(self, size):
        # assume random position
        self.u = np.array([rnd(size), rnd(size)])

    def calculate_position(self, method, size):
        # clean distances and landmarks
        self.landmarks = list()
        self.landmark_dists = dict()

        # update distances of landmarks
        for landmark in self.table:
            entry = self.table[landmark]
            self.landmarks.append(landmark)
            self.landmark_dists[landmark] = entry.value * self.hopsize

        try:
            self.u = self.triangulate(method)
        except:
            # error during estimation
            self.set_random_pos(size)

        #print "N:", self.id, " u = ", self.u, ", p = ", self.pos, "deg =", self.degree


    def draw(self, screen):
        color = RED
        p = np.int64(self.pos)
        if self.broadcasts > 0:
            pygame.draw.circle(screen, BLACK, p, int(self.ss), 1)
            color = GREEN
        pygame.draw.circle(screen, color, p, 6)

        # draw id of node
        wp = p + np.array([-15, -9])
        write_screen(screen, str(self.id), wp, BLUE, SMALL_FONT)

        # draw number of table entries
        wp = p + np.array([9, -9])
        write_screen(screen, str(len(self.table)), wp, BLACK, SMALL_FONT)

        # draw estimated hop size
        wp = np.int64(self.pos) + np.array([5, 5])
        write_screen(screen, str(round(self.hopsize,1)), wp, BLACK, SMALL_FONT)

        # do we have an estimated position?
        if not self.u == None:
            #yes
            pygame.draw.line(screen, BLACK, np.int64(self.u), p, 1)
            pygame.draw.circle(screen, BLUE, np.int64(self.u), 4)

