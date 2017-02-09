import numpy as np

def distance(p1, p2):
    d = p1 - p2
    return np.sqrt(np.dot(d, d))

def distance_dx(p1, p2):
    d = p1[0] - p2[0]
    return d / distance(p1, p2)

def distance_dy(p1, p2):
    d = p1[1] - p2[1]
    return d / distance(p1, p2)


class node:
    def __init__(self, x, y):
        self.pos = np.array([x, y]) * 1.0
        self.radio_error = 0
        self.landmarks = list()
        self.landmark_dists = dict()

    def set_radio_error(self, r_err):
        self.radio_error = r_err

    def add_landmark(self, landmark):
        self.landmarks.append(landmark)
        self.landmark_dists[landmark] = self.measure_distance(landmark)

    def measure_distance(self, landmark):
        d = distance(self.pos, landmark.pos)
        merr = np.random.uniform(1-self.radio_error, 1+self.radio_error)
        return d * merr

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
