#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Andrew Boring'
SITENAME = 'Andrew Boring'
SITEURL = 'https://andrewboring.com'

#PATH = 'content'

TIMEZONE = 'America/New_York'

DEFAULT_LANG = 'en'
# Feed generation is usually not desired when developing
FEED_ALL_ATOM = 'feeds/all/atom.xml'
FEED_ALL_RSS = None
CATEGORY_FEED_ATOM = 'feeds/{slug}/atom.xml'
CATEGORY_FEED_RSS = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None


# Blogroll
#LINKS = (('a10g Projects', 'https://a10g.com'),
#         ('Eriscape', 'https://eriscape.com'),
#         ('BENJA', 'https://benja.io'),
#         ('Here To', 'http://here.to'),)

# Social widget
SOCIAL = (('LinkedIn','https://linkedin.com/in/andrewboring'),
		  ('Twitter','https://twitter.com/andrewboring'),
		  ('SoundCloud','https://soundcloud.com/andrewboring'),
          ('Github', 'https://github.com/andrewboring'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True


# +++ Andrew's Settings
PATH = '~/dev/andrewboring.github.io/src'
DISPLAY_CATEGORIES_ON_MENU = False
CATEGORIES_SAVE_AS = ''
ARTICLE_PATHS = ['content']
INDEX_SAVE_AS = 'content/index.html'
STATIC_PATHS = ['media']
ARTICLE_URL = 'content/{slug}.html'
ARTICLE_SAVE_AS = 'content/{slug}.html'
DRAFT_PAGE_SAVE_AS = 'drafts/{slug}.html'
DRAFT_ARTICLE_SAVE_AS = 'drafts/{slug}.html'
TAG_URL = 'topic/{slug}.html'
TAG_SAVE_AS = 'topic/{slug}.html'
#THEME = 'monospace'
THEME = 'themes/monospace4me'
DESCRIPTION = 'There are many Andrews in this world, but only I am Boring.'
SITESUBTITLE = ''
RELATIVE_URLS = True
PLUGIN_PATHS = ['plugins']
#PLUGINS = ['liquid_tags.youtube', 'liquid_tags.soundcloud', 'md_inline_extension']
PLUGINS = ['liquid_tags.youtube', 'liquid_tags.soundcloud', 'sitemap']
HIDE_DATE = True
MD_EXTENSIONS = ['codehilite', 'extra']

# Comics
COMICS = (('Perry Bible Fellowship', 'https://pbfcomics.com'),
         ('XKCD', 'https://xkcd.com'),
         ('Red Meat', 'https://www.redmeat.com/max-cannon/FreshMeat'),
         ('', ''),)

AMUSEMENT = (('Museam of Unworkable Devices', 'https://www.lockhaven.edu/~dsimanek/museum/annex.htm'),
         ('ACME Klein Bottles', 'https://www.kleinbottle.com'),
         ('The Hosaphone(tm)', 'https://www.hosaphone.com'),
         ('', ''),)
