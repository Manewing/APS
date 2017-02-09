# Data Packets

class NodeTEntry:
    def __init__(self, landmark, x, y, value, sender):
        self.landmark   = landmark
        self.x          = x
        self.y          = y
        self.value      = value
        self.sender     = sender

    def copy(self):
        return NodeTEntry(self.landmark, self.x, self.y, self.value, self.sender)

    def dump(self):
        print "NodeTEntry Data Packet: (L: ", self.landmark.id, ")( N:", self.sender.id, ")"
        print "X:", self.x, "Y:", self.y, "Value:", self.value

class Correction:
    def __init__(self, hopsize, landmark, number):
        self.hopsize  = hopsize
        self.landmark = landmark
        self.number   = number

    def copy(self):
        return Correction(self.hopsize, self.landmark, self.number)

    def dump(self):
        print "Correction Data Packet: (L:", self.landmark.id, "): ", self.number
