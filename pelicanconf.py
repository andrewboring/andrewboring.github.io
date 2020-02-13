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
FEED_ALL_RSS = 'feeds/all/rss.xml'
CATEGORY_FEED_ATOM = 'feeds/{slug}/atom.xml'
CATEGORY_FEED_RSS = 'feeds/{slug}/rss.xml'
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

TAGLINES = ['There are  many Andrews in this world, but only I am Boring.',
			'Various and Sundries',
			'What, me worry?']

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True


# +++ Andrew's Settings
PATH = '~/dev/andrewboring.github.io/src'
DISPLAY_CATEGORIES_ON_MENU = False
CATEGORY_SAVE_AS = 'content/{slug}.html'
ARTICLE_PATHS = ['content']
INDEX_SAVE_AS = 'content/index.html'
STATIC_PATHS = ['media', 'extra/CNAME']
ARTICLE_URL = 'content/{slug}.html'
ARTICLE_SAVE_AS = 'content/{slug}.html'
DRAFT_PAGE_SAVE_AS = 'drafts/{slug}.html'
DRAFT_ARTICLE_SAVE_AS = 'drafts/{slug}.html'
TAG_URL = 'topic/{slug}.html'
TAG_SAVE_AS = 'topic/{slug}.html'
TAGS_SAVE_AS = 'topics.html'
#THEME = 'monospace'
THEME = 'themes/monospace4me'
DESCRIPTION = 'There are many Andrews in this world, but only I am Boring.'
SITESUBTITLE = ''
RELATIVE_URLS = True
PLUGIN_PATHS = ['plugins']
#PLUGINS = ['liquid_tags.youtube', 'liquid_tags.soundcloud', 'md_inline_extension']
PLUGINS = ['liquid_tags.youtube', 'liquid_tags.soundcloud', 'sitemap']
HIDE_DATE = False
#MD_EXTENSIONS = ['codehilite', 'extra']
MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite': {'css_class': 'highlight'},
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
    },
    'output_format': 'html5',
}

SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.5,
        'indexes': 0.5,
        'pages': 0.5
    },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'daily',
        'pages': 'monthly'
    }

}

# Comics
COMICS = (('Perry Bible Fellowship', 'https://pbfcomics.com'),
         ('XKCD', 'https://xkcd.com'),
         ('Red Meat', 'https://www.redmeat.com/max-cannon/FreshMeat'),
         ('', ''),)

AMUSEMENT = (('Museam of Unworkable Devices', 'https://www.lockhaven.edu/~dsimanek/museum/annex.htm'),
         ('ACME Klein Bottles', 'https://www.kleinbottle.com'),
         ('The Hosaphone(tm)', 'https://www.hosaphone.com'),
         ('', ''),)

EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'},}
#RESPONSIVE_IMAGES = True
