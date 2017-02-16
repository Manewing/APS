# EnvBase #

import numpy as np

import NodeBase
import ActionBase

"""
    Exception raised by EnvBase when scheduler is empty
"""
class EmptyScheduler(Exception):
    pass

class EnvStats(object):
    def __init__(self):
        # total number of broadcasts
        self.total_broadcasts   = 0

        # packet type specific number of broadcasts
        self.broadcasts         = dict()

        # node degrees
        self.node_degrees       = dict()

    def dump(self):
        print "Total number of broadcasts       : %10.4f" % self.total_broadcasts
        for dt, brcs in self.broadcasts.iteritems():
            dt = str(dt)
            dt = dt[dt.rfind('.')+1:dt.rfind("'")]
            print "Broadcasts of %-19s: %10.4f" % (dt, brcs)
        print "Average node degree              : %10.4f" % self.average_degree()

    def broadcast(self, data):
        self.total_broadcasts += 1
        try:
            self.broadcasts[type(data)] += 1
        except KeyError:
            self.broadcasts[type(data)] = 1

    def set_degree(self, at, dg):
        self.node_degrees[(at[0], at[1])] = dg

    def average_degree(self):
        avg_deg = 0.0
        for k,dg in self.node_degrees.iteritems():
            avg_deg += dg
        return avg_deg / len(self.node_degrees)

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
        Performs a broadcast by node 'node' with packet 'data'
    """
    def broadcast(self, node,  data):
        # register broadcast in statistics
        self.stats.broadcast(data)
        # get position
        at = node.pos
        # get signal strength
        ss = node.ss
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

    """
        Cache nodes which are in range of signal (strength: 'ss')
        at position 'at' while performing broadcast
    """
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

        # also set degree of node in stats
        self.stats.set_degree(at, len(nodes))


    """
        Advance scheduler (action manager) by one tick
    """
    def tick(self):
        self.action_manager.tick()

        if self.action_manager.empty():
            raise EmptyScheduler # signal no more actions left

