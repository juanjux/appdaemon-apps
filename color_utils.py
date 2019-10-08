temperatures = [153, 326, 500]


def cycle_temp_front(current_temp):
    try:
        c = temperatures.index(current_temp)
    except ValueError:
        # manually setted to another value, restart cycle
        return temperatures[0]

    if c == len(temperatures) - 1:
        return temperatures[0]
    return temperatures[c + 1]


def cycle_temp_back(current_temp):
    try:
        c = temperatures.index(current_temp)
    except ValueError:
        # manually setted to another value, restart cycle
        return temperatures[0]

    if c == 0:
        return temperatures[-1]
    return temperatures[c - 1]


colors = [
    [255, 0, 0],  # red
    [255, 65, 0],  # red-orange
    [255, 127, 0],  # orange
    [255, 190, 0],  # orange-yellow,
    [255, 254, 0],  # yellow
    [190, 255, 0],  # green-yellow,
    [126, 255, 0],  # green1
    [63, 255, 0],  # green2
    [0, 255, 0],  # green3
    [0, 255, 63],  # green4
    [0, 255, 127],  # green5
    [0, 255, 190],  # green-blue
    [0, 254, 255],  # blue1
    [0, 192, 255],  # blue2
    [0, 127, 255],  # blue3
    [0, 66, 255],  # blue4
    [0, 0, 255],  # blue5
    [66, 0, 255],  # blue6
    [129, 0, 255],  # purple1
    [191, 0, 255],  # pink1,
    [255, 0, 254],  # pink2,
    [255, 0, 191],  # pink3
    [255, 0, 127],  # pink4
    [255, 0, 65],  # pink5
]


# TODO: move to an utility module
def color_distance(color1, color2):
    distance = 0
    for i in (0, 1, 2):
        distance += abs(color1[i] - color2[i])
    return distance


def find_next_closest(current_color):
    if current_color is None:
        return colors[0]

    closest = None
    next_ = None
    store_next = False
    break_next = False
    closest_distance = None

    for color in colors:
        if store_next:
            next_ = color
            store_next = False

        if break_next:
            break

        distance = color_distance(current_color, color)
        if closest is None or distance < closest_distance:
            next_ = None
            closest_distance = distance
            closest = color
            store_next = True

        if distance == 0:
            break_next = True

    if next_ is None:
        # closest was the last one
        return colors[0]

    return next_


def cycle_color_front(current_color):
    return find_next_closest(current_color)
