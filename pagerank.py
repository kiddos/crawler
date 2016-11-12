#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
import os
import pickle
from optparse import OptionParser
import crawler


def compute_prob(nodes):
    url_count = len(nodes)
    url_list = [url for url in nodes]
    R = np.ones([url_count, 1], dtype=np.float32)
    M = np.zeros([url_count, url_count], dtype=np.float32)

    R = R / url_count

    for i in range(url_count):
        for j in range(url_count):
            if i == j:
                M[i][j] = 1
            if url_list[j] in nodes[url_list[i]]:
                M[i][j] = 1
    for j in range(url_count):
        count = 0
        for i in range(url_count):
            if M[i][j] == 1:
                count += 1
        for i in range(url_count):
            M[i][j] /= count
    return url_list, R, M


def load_nodes(filepath):
    with open(filepath, 'rb') as f:
        nodes = pickle.load(f)
        f.close()
        return nodes


def page_rank_iterative(R, M, d):
    max_iter = 100
    eps = 1e-3
    N = R.shape[0]
    for it in range(max_iter):
        new_R = d * np.matmul(M, R) + (1 - d) / N
        if np.sum(np.abs(new_R - R)) < eps:
            break
        R = new_R
    return R


def plot_rank(filepath, damping_factor, display):
    nodes = load_nodes(filepath)
    url_list, R, M = compute_prob(nodes)
    rank = page_rank_iterative(R, M, damping_factor)
    sort_index = np.argsort(rank, axis=0, kind='quicksort')[::-1]
    relation = M > 0

    print('%4s %8s %4s %4s %s' % ('rank', 'score', 'in', 'out', 'url'))
    for i, index in enumerate(sort_index[:display]):
        print('%3d. %1.6f %4d %4d %s' % (i + 1, rank[index],
            np.sum(relation[index, :]), np.sum(relation[:, index]),
            url_list[index]))

    relation_figure = plt.figure()
    relation_plot = relation_figure.add_subplot(111)
    relation_plot.matshow(relation)

    node_count = len(nodes)
    rank_figure = plt.figure()
    rank_plot = rank_figure.add_subplot(111)
    rank_plot.bar(range(node_count), [r for r in rank], width=0.8)
    plt.show()


def main():
    parser = OptionParser()
    parser.add_option('-f', '--file', dest='file',
        default=crawler.CRAWLER_RESULT, help='pickle file containing the urls')
    parser.add_option('-n', '--display', dest='display',
        default=30, help='number of entries to display', type='int')
    parser.add_option('-d', '--damping-factor', dest='damping_factor',
        default=0.85, help='damping factor', type='float')
    parser.add_option('-c', '--computation', dest='computation',
        default='iterative', help='computation method')
    (options, args) = parser.parse_args()

    option_dict = options.__dict__
    url_filepath = option_dict['file']
    damping_factor = float(option_dict['damping_factor'])
    display = int(option_dict['display'])
    plot_rank(url_filepath, damping_factor, display)


if __name__ == '__main__':
    main()
