# Node Base #

import numpy as np
from abc import ABCMeta, abstractmethod

import ActionBase

# action wrapper for NodeBase.broadcast
class ActionBroadcast(ActionBase.ActionBase):
    def __init__(self, node, env, data):
        self.node = node
        self.env  = env
        self.data = data

    def execute(self):
        self.node.broadcast(self.env, self.data)

# action wrapper for NodeBase.process
class ActionProcess(ActionBase.ActionBase):
    def __init__(self, node, env, data):
        self.node = node
        self.env  = env
        self.data = data

    def execute(self):
        self.node.process(self.env, self.data)


class InvalidPacket(Exception):
    pass

# Node Base
#
# Base class for sensor node that allows receiving, processing and
# broadcasting as well as methods for triangulation.
#
class NodeBase:
    __metaclass__ = ABCMeta

    # static node ID
    __ID = 0

    # static node broadcast delay (in ticks)
    BRC_DELAY_MIN = 0
    BRC_DELAY_MAX = 5

    # static node processing delay (in ticks)
    PRC_DELAY_MIN = 0
    PRC_DELAY_MAX = 5

    def __init__(self, x, y, ss):
        # set id of node
        self.id = NodeBase.__ID
        NodeBase.__ID += 1

        # set position
        self.pos = np.array([x, y]) * 1.0

        # signal strength
        self.ss = ss

        # list of all landmarks
        self.landmarks = list()

        # distances to the landmarks
        self.landmark_dists = dict()

        # keep track of the number of broadcasts
        self.broadcasts = 0

        # degree of node
        self.degree = 0

        # carrier sense
        self.carrier_sense = 0

    # Network #


    def determine_degree(self, env):
        # get degree from Environment
        self.degree = env.get_degree(self.pos, self.ss)

    def schedule_broadcast(self, env, data):
        # create new broadcast action
        action = ActionBroadcast(self, env, data)

        # schedule broadcast
        env.action_manager.queue_random(action, \
            NodeBase.BRC_DELAY_MIN, NodeBase.BRC_DELAY_MAX)

        # increase number of queue broadcasts
        self.broadcasts += 1

    def broadcast(self, env, data):
        # decrease number of queued broadcasts
        self.broadcasts -= 1

        # broadcast at node position with signal strength some data
        env.broadcast(self.pos, self.ss, data)

    def schedule_process(self, env, data):
        # create new process action_manager
        action = ActionProcess(self, env, data)

        # schedule process
        env.action_manager.queue_random(action, \
            NodeBase.PRC_DELAY_MIN, NodeBase.PRC_DELAY_MAX)


    @abstractmethod
    def process(self, env, data):
        """ processing of received data """
        pass

    @abstractmethod
    def is_valid(self, data):
        """ pre-check if to accept data packet """
        pass

    def receive(self, env, data):
        if not self.is_valid(data):
            raise InvalidPacket # catched by env

        # schedule processing of received data
        self.schedule_process(env, data)


    # "Triangulation" #


    def add_landmark(self, landmark, distance):
        self.landmarks.append(landmark)
        self.landmark_dists[landmark] = distance

    # fi(u)
    def f_u(self, u, landmark):
        return distance(u, landmark.pos) - self.landmark_dists[landmark]

    # f(u)
    def f_u_vec(self, u):
        f_vec = np.empty(len(self.landmarks))

        for idx in range(0, len(self.landmarks)):
            f_vec[idx] = self.f_u(u, self.landmarks[idx])

        return f_vec

    # J(u)
    def jacobi(self, u):
        J = np.empty([len(self.landmarks), 2])

        for idx in range(0, len(self.landmarks)):
            J[idx][0] = distance_dx(u, self.landmarks[idx].pos)
            J[idx][1] = distance_dy(u, self.landmarks[idx].pos)

        return J

    def triangulate(self, t):
        if len(self.landmarks) == 0:
            print "WARNING: cannot calculate position without landmarks"
            raise RuntimeError("no landmarks available!")

        if t == "GNA" or t == "gna":
            u = self.triangulate_gna()
        elif t == "GDM" or t == "gdm":
            u = self.triangulate_gdm()
        else:
            raise ValueError("unkown type: " + t)

        if np.isnan(u).any() == True:
            raise RuntimeError("position estimation resulted in invalid position")

        return u

    def increment_gna(self, u):
        f = self.f_u_vec(u)
        J = self.jacobi(u)
        Jt = np.transpose(J)

        JtJinv = -(np.linalg.inv(np.dot(Jt, J)))
        JtJinvJt = np.dot(JtJinv, Jt)
        return np.dot(JtJinvJt, f)

    def triangulate_gna(self):
        u = np.array([0, 0])

        for it in range(0, 1000):
            inc = self.increment_gna(u)

            if np.linalg.norm(inc) < 0.05:
                break

            u = u + inc

        return u

    def increment_gdm(self, u):
        f = self.f_u_vec(u)
        Jt = np.transpose(self.jacobi(u))

        # eta = 1.5 see paper
        alpha = 1.5 / len(self.landmarks)

        return -alpha * np.dot(Jt, f)

    def triangulate_gdm(self):
        u = np.array([0, 0])

        for it in range(0, 1000):
            inc = self.increment_gdm(u)

            if np.linalg.norm(inc) < 0.05:
                break;

            u = u + inc

        return u

def distance(p1, p2):
    d = p1 - p2
    return np.sqrt(np.dot(d, d))

def distance_dx(p1, p2):
    d = p1[0] - p2[0]
    return d / distance(p1, p2)

def distance_dy(p1, p2):
    d = p1[1] - p2[1]
    return d / distance(p1, p2)
