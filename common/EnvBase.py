import numpy as np

import NodeBase
import ActionBase

class EmptyScheduler(Exception):
    pass

class EnvBase:
    def __init__(self):
        # init nodes
        self.nodes          = list()

        # init the action manager
        self.action_manager = ActionBase.ActionManager()

    def add_node(self, node):
        self.nodes.append(node)

    def broadcast(self, at, ss, data):
        # find nodes in range
        for n in self.nodes:
            # distance between broadcasting position and node
            d = NodeBase.distance(at, n.pos)

            # in range?
            if d <= ss:
                # yes
                # set carrier sense to high
                n.carrier_sense = 1
                try:
                    n.receive(self, data)
                except NodeBase.InvalidPacket:
                    pass # ignore

    """
        Advance scheduler (action manager) by one tick
    """
    def tick(self):
        self.action_manager.tick()

        for n in self.nodes:
            n.carrier_sense = 0

        if self.action_manager.empty():
            raise EmptyScheduler # signal no more actions left

    """
        Get the (node) degree at the given position 'at'
        with signal strength 'ss'
    """
    def get_degree(self, at, ss):
        degree = 0
        # find nodes in range
        for n in self.nodes:
            # distance between broadcasting position and node
            d = NodeBase.distance(at, n.pos)

            # in range?
            if d <= ss:
                degree += 1
        return degree

