# Actions

import sys

sys.path.append("../common/")
import action_base

class ActionProcess(action_base.ActionBase):
    def __init__(self, node, env, data):
        self.node = node
        self.env  = env
        self.data = data

    def execute(self):
        self.node.process(self.env, self.data)

class ActionBroadcast(action_base.ActionBase):
    def __init__(self, node, env, data):
        self.node = node
        self.env  = env
        self.data = data

    def execute(self):
        self.node.broadcast(self.env, self.data)
