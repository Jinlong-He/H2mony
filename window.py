import cv


class Window(object):
    def __init__(self, bounds=None, img=None):
        if bounds is None:
            bounds = set()
        self.bounds = bounds
        self.img = img
        self.img_dhash = ''

    def bounds_similarity(self, other):
        l = self.bounds
        r = other.bounds
        bounds_sim = len(l.intersection(r))/len(l.union(r))
        return bounds_sim

    def img_similarity(self, other):
        if self.img_dhash == '':
            self.img_dhash = cv.calculate_dhash(self.img)
        if other.img_dhash == '':
            other.img_dhash = cv.calculate_dhash(other.img)
        distance = cv.dhash_hamming_distance(self.img_dhash, other.img_dhash)
        self_len = len(self.img_dhash)
        other_len = len(other.img_dhash)
        img_sim = 1-distance/self_len
        return img_sim
