# -*- coding: utf-8 -*-

import os
import sys
import getpass
import re
import codecs

import urllib
import urllib2
import cookielib

import feedparser

class LJSaver(object):
    """
    A class for saving entries of a blog hosted at LJ.

    On init, it accepts the username of the blogger, the
    path to the directory where the HTML files for the
    entries should be saved and an stdout object that
    should be used for the output (can be set to None
    to disable the output of the class methods).

    The “login” method accepts username and
    password pair that should be used for
    authentication. Call this method before
    using “crawl” if there are non-public
    entries available to you that you want
    to save.

    The “crawl” method locates the newest entry,
    saves it, and then loads all the previous
    entries one by one.

    The “save” method accepts a string containing
    the HTML of an entry and a filename that should
    be used for saving the entry. It creates a new
    file inside the directory specified when
    initializing the class and saves the entry’s
    HTML in this file.
    """
    entry_filename_re = re.compile(r".*/(\d+\.html)$")
    entry_title_re = re.compile(
        r"<meta property=\"og:title\" content=\"([^\"]+)\" />"
    )

    def __init__(self, blog, directory, stdout=None):
        self.blog = blog
        self.directory = directory
        self.stdout = stdout

        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self.cj)
        )
        self.opener.addheaders = [
            ('User-Agent', ('Mozilla/5.0 (X11; Ubuntu; Linux '
                            'x86_64; rv:20.0) Gecko/20100101 '
                            'Firefox/20.0')),
        ]

    def msg(self, message):
        """
        This method accepts a message and writes it to
        the stdout object if it is present. If the stdout
        object is not set (which means the verbose output
        can be neglected), the function does nothing.
        """
        if self.stdout:
            self.stdout.write(u"%s\n" % message)
            self.stdout.flush()

    def login(self, username, password):
        self.msg(u'Logging in…')

        params = urllib.urlencode({
            "user": username, "password": password
        })

        self.opener.open(
            "https://www.livejournal.com/login.bml?ret=1",
            params,
        )

    def crawl(self):
        self.msg(u"Fetching the URL of the newest entry…")

        feed_url = "http://%s.livejournal.com/data/rss" % self.blog

        req = self.opener.open(feed_url)

        feed = feedparser.parse(req)

        if not feed.entries:
            self.msg(
                u"Couldn’t fetch entries from the RSS feed at %s" % feed_url
            )
            return

        link = feed.entries[0].get('link')

        self.msg(u"Starting crawling from %s" % link)

        while link:
            req = self.opener.open(link)
            # The final URL differs from the URL
            # contained in the link variable
            # if a redirect has occured
            match = self.entry_filename_re.match(req.geturl())
            if match:
                filename = match.group(1)
                self.save(req.read(), filename)
                # If there’s entry filename in the URL,
                # continue crawling
                link = "http://www.livejournal.com/go.bml?%s" % (
                           urllib.urlencode({
                               "journal": self.blog,
                               "itemid": filename.split(".")[0],
                               "dir": "prev",
                           })
                       )
            else:
                # If there’s no entry filename in the URL
                # (after redirect), stop crawling
                link = None

    def save(self, html, filename):
        f = open(os.path.join(self.directory, filename), "w")
        f.write(html)
        f.close()
        match = self.entry_title_re.search(html)
        if match:
            self.msg(
                u"Saved %s (%s)" % (
                    filename,
                    match.group(1).decode("utf-8")
                )
            )
        else:
            self.msg(u"Saved %s" % filename)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit("Usage: python ljsaver.py [username] [directory]")

    blog = sys.argv[1]
    directory = sys.argv[2]

    lj_saver = LJSaver(blog, directory, sys.stdout)

    if not os.path.exists(directory):
        sys.exit("Please make sure that the directory exists.")

    if not os.path.isdir(directory):
        sys.exit("%s should be a directory." % directory)

    username = raw_input("Username (leave empty if you want "
                         "to only crawl public posts): ")

    if username:
        password = getpass.getpass("Password (will not be echoed): ")
        lj_saver.login(username, password)

    lj_saver.crawl()
