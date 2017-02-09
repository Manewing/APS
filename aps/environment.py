# Environment
import sys
import random
import numpy as np
import pygame

from node import Node
from landmark import Landmark

from gbls import *

sys.path.append("../common/")
import action_base
import node_base

class Environment:
    def __init__(self, nc, lc, size, max_hop, method, npos, lpos):
        self.size           = float(size)
        self.max_hop        = float(max_hop)
        self.normal_nodes   = len(npos)
        self.landmark_nodes = len(lpos)
        self.action_manager = action_base.ActionManager()

        self.method         = method
        self.est_err        = 1.0
        self.avg_deg        = 0

        self.running        = False
        self.do_update      = True
        self.screen         = pygame.display.set_mode((size+ENV_OFF*2, size+ENV_OFF*2))
        self.fps_clock      = pygame.time.Clock()
        pygame.display.set_caption("APS Simulation")

        # init nodes
        self.nodes          = list()

        # add normal nodes
        for pos in npos:
            self.nodes.append(Node(pos[0], pos[1], self.max_hop))

        for pos in lpos:
            self.nodes.append(Landmark(pos[0], pos[1], self.max_hop, self))


    def get_degree(self, atpos, ss):
        degree = 0
        # find nodes in range
        for n in self.nodes:
            # distance between broadcasting position and node
            d = node_base.distance(atpos, n.pos)

            # in range?
            if d <= ss:
                degree += 1
        return degree

    def broadcast(self, atpos, ss, data):
        # find nodes in range
        for n in self.nodes:
            # distance between broadcasting position and node
            d = node_base.distance(atpos, n.pos)

            # in range?
            if d <= ss:
                # yes
                n.receive(self, data)

    def handle_input(self):
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                print "QUIT"
                break

    def update(self):
        self.action_manager.tick()
        if self.action_manager.empty():
            self.do_update = False

            # average degree of nodes
            self.avg_deg = 0.0

            # estimate node positions
            est_err = np.array([0.0, 0.0])
            for n in self.nodes:
                n.determine_degree(self)
                self.avg_deg += n.degree
                if isinstance(n, Landmark):
                    continue
                n.calculate_position(self.method, self.size)
                est_err += abs(n.pos - n.u) / float(n.ss)

            est_err /= self.normal_nodes
            self.est_err = np.sqrt(np.dot(est_err, est_err))

            self.avg_deg /= len(self.nodes)

            print "Estimation error:", self.est_err, "Node degree: ", self.avg_deg
            print "--- DONE --- "

    def render_grid(self):
        global SMALL_FONT, BIG_FONT
        e = ENV_OFF
        s = int(self.size)
        p = 0
        for l in range(0, 11):
            # vertical
            pygame.draw.line(self.screen, BLACK, (e+p, e), (e+p, e+s), 1)
            write_screen(self.screen, str(p), (e+p-5, e-20), BLACK, SMALL_FONT)
            # horizontal
            pygame.draw.line(self.screen, BLACK, (e, e+p), (e+s, e+p), 1)
            write_screen(self.screen, str(p), (e-20, e+p-5), BLACK, SMALL_FONT)
            p += s/10

    def render(self):
        self.screen.fill(WHITE)
        self.render_grid()
        self.fps_clock.tick(30)

        for n in self.nodes:
            n.draw(self.screen)

        pygame.display.update()

    def run_visual(self):
        self.running = True
        while self.running:
            self.handle_input()
            if self.do_update:
                self.update()
            self.render()

    def run(self, show_results):
        while True:
            self.update()
            if not self.do_update:
                # no more updates quit
                break

        # show results
        if show_results:
            self.run_visual()
