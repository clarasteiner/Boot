# Author    -   Luis Gerloni    |   MIND-Codes
# Author    -   Clara Steiner   |   MIND-Codes
# Email:    -   gerloni-luis@outlook.com
# Github:   -   https://github.com/MIND-Codes

import numpy as np
from list import table, oxygen_list

weight = [0.08, 0.20, 0.10, 0.10, 0.15, 0.07, 0.10, 0.20]

list = ["Temperatur", "Sauerstoff", "pH", "Nitrat", "Ammonium", "Leitfähigkeit", "Phosphat", "BSB5"]


def oxygen(temperature, oxygen):
    concentration = transform(oxygen_list, temperature)
    return (oxygen * 100) / concentration


def transform(parameter, value):
    x = parameter[0]
    y = parameter[1]
    coefficients = []
    for i in range(len(x) - 1):
        coefficients.append(np.polyfit([x[i], x[i + 1]], [y[i], y[i + 1]], 1))

    if value <= x[0]:
        index = y[0]
    elif value >= x[-1]:
        index = y[-1]
    else:
        for i in range(len(x)):
            if value <= x[i]:
                n = coefficients[i - 1]
                break
        index = n[0] * value + n[1]

    return round(index, 2)


def index1(values):
    list = ["Temperatur", "Sauerstoff", "pH", "Nitrat", "Ammonium", "Leitfähigkeit", "Phosphat", "BSB5"]

    values[1] = oxygen(values[0], values[1])

    index = []
    for i in range(8):
        index.append(transform(table[i], values[i]))
    return index


def assessment(index):
    list = [83, 74, 56, 45, 27, 18, 0]
    quality_class = ["I: unbelastet", "I-II: gering belastet", "II: mäßig belastet", "II-III: kritisch belastet",
                     "III: stark verschmutzt", "III-IV: sehr stark verschmutz", "IV: verödet"]

    ci = 1
    for i in range(8):
        ci *= index[i] ** weight[i]

    for i in range(7):
        if ci >= list[i]:
            return round(ci, 2), quality_class[i]


def main(values):
    index = index1(values)
    ci, quality_class = assessment(index)
    oxygen(values[0], values[1])

    return index, ci, quality_class
