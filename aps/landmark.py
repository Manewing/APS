# Landmark Node
import sys
import random
import numpy as np
import pygame

from node import Node
from data import *
from gbls import *

class Landmark(Node):
    def __init__(self, x, y, ss, env):
        Node.__init__(self, x, y, ss)

        # build initial table entry for this landmark
        data = NodeTEntry(self, x, y, 0, self)

        # schedule broadcast
        self.schedule_broadcast(env, data)

    def calculate_position(self, method):
        pass # position is known

    def process(self, env, data):
        # we received data
        if isinstance(data, NodeTEntry) and self.is_valid_nte(data):

            # we received information of another landmark, forward it
            Node.process(self, env, data)

            # compute correction of hopsize
            h_sum = 1
            diff_sum = 0.0
            for entry in self.table.values():
                h_sum += entry.value
                diff = self.pos - np.array([entry.x, entry.y])
                diff_sum += np.sqrt(np.dot(diff, diff))
            self.hopsize = diff_sum / h_sum

            # schedule broadcast correction of hopsize
            data = Correction(self.hopsize, self, len(self.table))
            self.schedule_broadcast(env, data)
        else:
            # drop data
            #print "L:", self.id, "dropped data packet"
            return

        return

    def draw(self, screen):
        pygame.draw.circle(screen, BLUE, np.int64(self.pos), 8)
        Node.draw(self, screen)
