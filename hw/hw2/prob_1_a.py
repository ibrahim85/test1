import bisect
from itertools import izip

import numpy as np
import pandas as pd


# split

def split(data, m):
    test_size = 1 - m
    length = len(data)

    indices = list(data.index)
    np.random.shuffle(indices)

    test_length = int(round(test_size * length))
    test_indices = indices[:test_length]
    train_indices = indices[test_length:]

    test = data.loc[test_indices]
    train = data.loc[train_indices]

    return train, test


# knn

def distance(x1, x2):
    return abs(x1 - x2)


def find_best_neighbors_range(sorted_x_list, neighbors_range, test_x):
    current_left_index = neighbors_range[0]
    current_right_index = neighbors_range[1]
    best_range = current_left_index, current_right_index
    while current_right_index < len(sorted_x_list):
        left_distance = distance(test_x, sorted_x_list[current_left_index])
        right_distance = distance(test_x, sorted_x_list[current_right_index])
        if left_distance <= right_distance:
            break
        best_range = current_left_index, current_right_index
        current_left_index += 1
        current_right_index += 1
    if best_range[0] == neighbors_range[0]:
        # we didn't find better neighbors on the right, so we'll search left
        current_left_index = neighbors_range[0] - 1
        current_right_index = neighbors_range[1] - 1
        while current_left_index >= 0:
            left_distance = distance(test_x, sorted_x_list[current_left_index])
            right_distance = distance(test_x, sorted_x_list[current_right_index])
            if left_distance >= right_distance:
                break
            best_range = current_left_index, current_right_index
            current_left_index -= 1
            current_right_index -= 1
    return best_range


def get_initial_range(k, insertion_index, length):
    left_index = max(0, insertion_index - k / 2)
    right_index = left_index + k
    if right_index > length:
        right_index = length
        left_index = right_index - k
    return left_index, right_index


def find_nearest_neighbors(k, sorted_x_list, test_x):
    insertion_index = bisect.bisect_left(sorted_x_list, test_x)
    initial_range = get_initial_range(k, insertion_index, len(sorted_x_list))
    return find_best_neighbors_range(sorted_x_list, initial_range, test_x)


def knn_predict_one_point(k, sorted_train, sorted_x_list, test_x):
    neighbors_range = find_nearest_neighbors(k, sorted_x_list, test_x)
    total = 0.0
    for index in range(neighbors_range[0], neighbors_range[1]):
        total += sorted_train.iloc[index]['y']
    return total / k


def knn_predict(k, train, test):
    sorted_train = train.sort_values(by='x')
    sorted_x_list = sorted_train['x'].tolist()
    predicted_test = test.copy()

    predicted_test['y'] = [knn_predict_one_point(k, sorted_train, sorted_x_list, row['x'])
                           for index, row in test.iterrows()]
    return predicted_test


# linear regression

def linear_reg_fit(train):
    x_list = train['x'].tolist()
    y_list = train['y'].tolist()

    x_mean = np.mean(x_list)
    y_mean = np.mean(y_list)

    numerator_sum = 0.0
    denominator_sum = 0.0
    for x, y in izip(x_list, y_list):
        x_diff = x - x_mean
        numerator_sum += x_diff * (y - y_mean)
        denominator_sum += x_diff ** 2

    slope = numerator_sum / denominator_sum
    intercept = y_mean - slope * x_mean
    return slope, intercept


def linear_reg_predict(test, slope, intercept):
    predicted_test = test.copy()
    predicted_test['y'] = [intercept + slope * row['x'] for index, row in test.iterrows()]
    return predicted_test


# score

def score(predicted, actual):
    rss = 0.0
    tss = 0.0
    actual_y_list = actual['y'].tolist()
    actual_y_mean = np.mean(actual_y_list)
    for predicted_value, actual_value in izip(predicted['y'].tolist(), actual_y_list):
        rss += (actual_value - predicted_value) ** 2
        tss += (actual_value - actual_y_mean) ** 2
    return 1.0 - rss / tss


def compare_with_sklearn():
    np.random.seed(1090)

    df = pd.read_csv('dataset/dataset_1_full.txt')

    train, test = split(df, 0.7)

    test_x = test[['x']]
    predicted_test = knn_predict(1, train, test_x)
    # s = score(predicted_test, test)
    # print s

    slope, intercept = linear_reg_fit(train)
    predicted_test = linear_reg_predict(test_x, slope, intercept)
    s = score(predicted_test, test)
    print s


if __name__ == '__main__':
    compare_with_sklearn()
