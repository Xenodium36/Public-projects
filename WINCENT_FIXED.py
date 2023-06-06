import numpy as np
import math

DIRECTIONS = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]


def read_file():
    lines = []
    with open("test.in", "r") as f:
        lines = f.read()

    lines = lines.split("\n")

    return lines


def rotate_vector_counterclockwise(vector):
    rotated_vector = (-vector[1], vector[0])
    return rotated_vector


def opposite_vector(vector):
    opposite = (-vector[0], -vector[1])
    return opposite


def distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def closest_point(given_point, points):
    min_distance = float('inf')
    closest = None
    for point in points:
        dist = distance(given_point, point)
        if dist < min_distance:
            min_distance = dist
            closest = point
    return closest


def convert_vector(vector):
    magnitude = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
    converted_vector = (vector[0] / magnitude, vector[1] / magnitude)
    return converted_vector


def calculate_vector(starting_point, ending_point):
    vector = (ending_point[0] - starting_point[0], ending_point[1] - starting_point[1])
    return vector


def normalizeVector(vector):
    a = 0
    b = 0
    if (vector[0] < 0):
        a = -1

    if (vector[0] == 0):
        a = 0

    if (vector[0] > 0):
        a = 1
    
    if (vector[1] < 0):
        b = -1

    if (vector[1] == 0):
        b = 0

    if (vector[1] > 0):
        b = 1

    return (a, b)


def get_points_on_vector(starting_point, vector, next_points):
    rotatedVector = rotate_vector_counterclockwise(vector)
    points_on_vector = []
    for point in next_points:
        difference = (point[0] - starting_point[0], point[1] - starting_point[1])
        dot_product = rotatedVector[0] * difference[0] + rotatedVector[1] * difference[1]
        if dot_product == 0:
            if(point != starting_point):
                calculatedVector = calculate_vector(starting_point, point)
                if((calculatedVector[0] < 0 and vector[0] < 0) or (calculatedVector[0] >= 0 and vector[0] >= 0)):
                    if((calculatedVector[1] < 0 and vector[1] < 0) or (calculatedVector[1] >= 0 and vector[1] >= 0)):
                        points_on_vector.append(point)

    return points_on_vector


def getStartingVector(direction):
    direction = direction.upper()
    if direction == 'N':
        return (0, 1)
    elif direction == 'NE':
        return (1, 1)
    elif direction == 'E':
        return (1, 0)
    elif direction == 'SE':
        return (1, -1)
    elif direction == 'S':
        return (0, -1)
    elif direction == 'SW':
        return (-1, -1)
    elif direction == 'W':
        return (-1, 0)
    elif direction == 'NW':
        return (-1, 1)
    else:
        return None


def retTestCase(lines, index):
    testCase = {}
    numOfPlayers = int(lines[index])
    testCase["numOfPlayers"] = numOfPlayers
    index += 1
    tmpPlayers = lines[index:numOfPlayers + index]
    testCase["players"] = [tuple(map(int, point.split())) for point in tmpPlayers]
    testCase["players2"] = [tuple(map(int, point.split())) for point in tmpPlayers]
    index += numOfPlayers
    testCase["direction"] = getStartingVector(lines[index])
    index += 1
    testCase["startPlayer"] = int(lines[index])
    index += 1

    return testCase, index


# def countCases(testCase):
def getNumOfTests(lines, index):
    numOfTests = 0
    try:
        numOfTests = int(lines[index])
        _ = int(lines[index + 1])
        index += 1
    except:
        numOfTests = 1
    return numOfTests, index


def calculateTestCase(testCase):
    cnt = 0
    players = testCase["players"]
    currentPlayer = players[testCase["startPlayer"]-1]
    direction = testCase["direction"]
    indexOfDirection = DIRECTIONS.index(direction)
    closestPlayer = None
    while(True):
        for i in range(1, 9):
            direction = DIRECTIONS[(i+indexOfDirection)%8]
            nextPlayers = get_points_on_vector(currentPlayer, direction, players)
            if (nextPlayers != []):
                players.pop(players.index(currentPlayer))
                break
        closestPlayer = closest_point(currentPlayer, nextPlayers)
        if (closestPlayer is None):
            return cnt, testCase["players2"].index(currentPlayer) + 1
        currentPlayer = closestPlayer
        cnt += 1
        direction = opposite_vector(direction)
        indexOfDirection = DIRECTIONS.index(direction)
        


def main():
    index = 0
    lines = read_file()
    numOfTests, index = getNumOfTests(lines, index)
    f = open("out2.txt", "w")
    for _ in range(numOfTests):
        testCase, index = retTestCase(lines, index)
        a, b = calculateTestCase(testCase)

        f.write(f"{a} {b}\n")


    f.close()



if __name__ == "__main__":
    main()
