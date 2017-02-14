import random
from abc import ABCMeta, abstractmethod

# Action Base Class
class ActionBase:
    __metaclass__ = ABCMeta

    def __init__(self, am):
        self.am = am

    def execute_internal(self):
        self.execute()

    @abstractmethod
    def execute(self):
        pass

class PeriodicAction(ActionBase):
    __metaclass__ = ABCMeta

    def __init__(self, am, p):
        ActionBase.__init__(self, am)
        self.__p = p

    def execute_internal(self):
        self.execute()
        self.am.queue(self, self.__p)

    @abstractmethod
    def execute(self):
        pass

class ActionManager:
    def __init__(self):
        self.__ticks        = 0
        self.__action_count = 0
        self.__action_map   = dict()

    def queue(self, action, ticks):
        # calculate (future) timing point
        tp = int(self.__ticks + abs(ticks))

        # get actions / action queue
        actions = None
        try:
            actions = self.__action_map[tp]
        except KeyError:
            self.__action_map[tp] = list()
            actions = self.__action_map[tp]

        # add action
        actions.append(action)
        self.__action_count += 1

    def queue_random(self, action, rnd_min, rnd_max):
        # queue action at random timing point
        self.queue(action, random.randint(int(rnd_min), int(rnd_max)))

    def tick(self):
        # try to get action queue
        try:
            actions = self.__action_map[self.__ticks]

            # execute actions in queue
            for action in actions:
                action.execute_internal()
                self.__action_count -= 1

            # delete queue
            del self.__action_map[self.__ticks]

        except KeyError:
            # no action queue
            pass

        self.__ticks += 1

    def size(self):
        return self.__action_count

    def empty(self):
        return self.__action_count == 0
