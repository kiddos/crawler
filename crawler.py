#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import urllib2
import re
import os
import pickle
from optparse import OptionParser
import pagerank

CRAWLER_RESULT = 'crawler-result.pickle'


def read_url(url):
    try:
        content = urllib2.urlopen(url, timeout=1).read()
        return content
    except:
        return ''


def concat_url(url, path):
    result = url
    if not url.endswith('/') and not path.startswith('/'):
        result += '/'
    return result + path


def trim_url(url):
    if url.endswith('/'):
        return url[:-1]
    return url


def get_root_url(url):
    starts = url.find('//') + 2
    ends = url.find('/', starts)
    if ends > 0:
        return url[:ends]
    return url


def is_web_page(href):
    other_type = ['css', 'js', 'png', 'jpg', 'gif', 'tiff', 'ico',
        'wma', 'ogg', 'mpg', 'mp3', 'mp4']
    if href.startswith('#'):
        return False
    if href == 'javascript:void(0)':
        return False
    for t in other_type:
        if href.endswith(t):
            return False
    return True


def get_links(url):
    content = read_url(url)
    if re.search('http-equiv=[\'"]refresh["\']', content):
        pattern = re.compile(r'content=\'0;url=([^\'"]+)[\'"]')
        new_url = pattern.findall(content)
        if new_url:
            url = concat_url(url, new_url[0])
            print('redirecting to ' + url)
            content = read_url(url)
    pattern = re.compile(r'href=[\'"]([^\'"]+)[\'"]')
    hrefs = pattern.findall(content)
    links = list()
    for href in hrefs:
        if not is_web_page(href):
            continue
        link = href
        if not href.startswith('http'):
            link = trim_url(concat_url(get_root_url(url), href))
            if link not in links and link != url:
                links.append(link)
        else:
            link = trim_url(link)
            if link not in links and link != url:
                links = [link] + links
    return links


def write_nodes(nodes, pickle_file):
    print('saving nodes to ' + pickle_file)
    with open(pickle_file, 'wb') as f:
        pickle.dump(nodes, f)
        f.close()


def save_nodes(nodes, pickle_file):
    if not os.path.isfile(pickle_file):
        write_nodes(nodes, pickle_file)
    else:
        old_pickle = open(pickle_file, 'rb')
        old_nodes = pickle.load(old_pickle)
        if old_nodes != nodes:
            old_pickle.close()
            write_nodes(nodes, pickle_file)


def crawl(url, nodes, level=1):
    print('crawling %s ...' % url)
    links = get_links(url)
    nodes[url] = links
    if level > 1:
        for link in links:
            crawl(link, nodes, level-1)


def main():
    parser = OptionParser()
    parser.add_option('-o', '--output', dest='output',
        default=CRAWLER_RESULT, help='pickle file to store urls')
    parser.add_option('-l', '--level', dest='level', default=1,
        help='crawling recursive level', type='int')
    parser.add_option('-u', '--url', dest='url',
        default='http://www.nuk.edu.tw', help='url to start crawling',
        action='store_false')
    (options, args) = parser.parse_args()
    option_dict = options.__dict__
    starting_url = option_dict['url']
    level = int(option_dict['level'])
    output_file = option_dict['output']
    nodes = {}
    crawl(starting_url, nodes, level=level)
    save_nodes(nodes, output_file)

    if level <= 2:
        pagerank.plot_rank(output_file, damping_factor=0.85, display=30)


if __name__ == '__main__':
    main()
