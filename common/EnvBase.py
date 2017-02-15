import numpy as np

import NodeBase
import ActionBase

class EmptyScheduler(Exception):
    pass

class EnvStats(object):
    def __init__(self):
        # total number of broadcasts
        self.total_broadcasts   = 0

        # packet type specific number of broadcasts
        self.broadcasts         = dict()

    def dump(self):
        pass #TODO

    def broadcast(self, data):
        self.total_broadcasts += 1
        try:
            self.broadcasts[type(data)] += 1
        except KeyError:
            self.broadcasts[type(data)] = 1

"""
    Environment base

    Base class environment which allows broadcasting of data
"""
class EnvBase(object):
    def __init__(self):
        # init nodes
        self.nodes          = list()

        # init the action manager
        self.action_manager = ActionBase.ActionManager()

        # init statistics
        self.stats          = EnvStats()

        # init broadcast cache
        self.__brc_cache    = dict()


    """
        Adds a node to the environment.
    """
    def add_node(self, node):
        self.nodes.append(node)

    """
        Performs a broadcast at position 'at' of a data packet
        'data' with a signal strength of 'ss'
    """
    def broadcast(self, at, ss, data):
        # register broadcast in statistics
        self.stats.broadcast(data)
        # get key from arguments
        key = (at[0], at[1], ss)

        try:
            nodes = self.__brc_cache[key]

            # we did a broadcast with this configuration already
            for n in nodes:
                try:
                    n.receive(self, data)
                except NodeBase.InvalidPacket:
                    pass # ignore
        except KeyError:
            # we dit not do a broadcast with this configuration
            # build up cache
            self.__cache_broadcast(at, ss, data)

    def __cache_broadcast(self, at, ss, data):
        # get key from arguments
        key = (at[0], at[1], ss)

        # node list to be cached
        nodes = list()

        # find nodes in range
        for n in self.nodes:
            # distance between broadcasting position and node
            d = NodeBase.distance(at, n.pos)

            # in range?
            if d <= ss:
                # yes
                nodes.append(n)
                try:
                    n.receive(self, data)
                except NodeBase.InvalidPacket:
                    pass # ignore

        # set up cache
        self.__brc_cache[key] = nodes

    """
        Advance scheduler (action manager) by one tick
    """
    def tick(self):
        self.action_manager.tick()

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

