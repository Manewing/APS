# Simple Node
import sys
import random
import numpy as np
import pygame

from data import *
from gbls import *

sys.path.append("../common/")
from NodeBase import NodeBase

class Node(NodeBase):

    def __init__(self, x, y, ss):
        # pass parameters to parent
        NodeBase.__init__(self, x, y, ss)

        # hopsize (estimated)
        self.hopsize = 0

        # reference of the last correction
        self.last_corr = None

        # table for landmark information
        self.table = dict()

        # estimated position of node
        self.u = None

    def process(self, env, data):
        # we received data
        if isinstance(data, NodeTEntry):
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

        elif isinstance(data, Correction):
            #print "N:", self.id, "received new data packet (Correction)"
            #data.dump()

            # update hopsize
            self.hopsize = data.hopsize

            # schedule broadcast of copy of data
            new_data = data.copy()
            self.schedule_broadcast(env, new_data)

        else:
            # drop data
            #print "N:", self.id, "dropped data packet"
            return

        return

    def is_valid(self, data):
        # check if packet is node table entry
        if isinstance(data, NodeTEntry):
            if data.landmark in self.table:
                return False
            if data.landmark == self: # only landmarks True
                return False
            return True

        # check if packet is correction
        if isinstance(data, Correction):
            # initial correction
            if self.last_corr == None:
                self.last_corr = data
                return True
            if self.last_corr.landmark == data.landmark \
                    and self.last_corr.number < data.number:
                self.last_corr = data
                return True

        # invalid packet
        return False


    def set_random_pos(self, size):
        # assume random position
        self.u = np.array([rnd(size), rnd(size)])

    def calculate_position(self, method, size):
        # update distances of landmarks
        for landmark in self.table:
            entry = self.table[landmark]
            self.add_landmark(landmark, entry.value * self.hopsize)

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

