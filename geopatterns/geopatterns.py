from random import randint
from colour import Color
from svg import SVG


def promap(value, v_min, v_max, d_min, d_max):  # v for value, d for desired
    v_value = float(value)
    v_range = v_max - v_min
    d_range = d_max - d_min
    d_value = (v_value - v_min) * d_range / v_range + d_min
    return d_value


class GeoPattern(object):
    def __init__(self, width_count=8, height_count=8):
        self.width_count = width_count
        self.height_count = height_count
        self.svg = SVG()
        self.geo_squares()

    @property
    def svg_string(self):
        return self.svg.to_string()

    def geo_squares(self):
        square_size = 50

        self.svg.width = square_size * self.width_count
        self.svg.height = square_size * self.height_count

        for y in range(self.height_count):
            for x in range(self.width_count):

                type_ = randint(1, 3)
                if type_ == 1:
                    color = (randint(235, 255),
                             randint(31, 71),
                             randint(82, 122))
                elif type_ == 2:
                    color = (randint(133, 173),
                             randint(82, 122),
                             randint(235, 255))
                elif type_ == 3:
                    color = (randint(235, 255),
                             randint(133, 173),
                             randint(31, 71))

                self.svg.rect(x * square_size, y * square_size,
                              square_size, square_size,
                              **{'fill': 'rgb({}, {}, {})'.format(*color)})
