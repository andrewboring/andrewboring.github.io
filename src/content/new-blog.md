Title: New Site
Date: 2019-09-23
Category: weblog

I'm kinda done with Wordpress. But that's a blog for another day.

No, this is about the new site that's *not* running Wordpress.

I needed to assemble a portfolio (both technical and musical) for work that I was doing, and it seemed like a good time to explore new options for site management and deployment. I'd seen [Pelican](https://getpelican.com) pop up more and more, and preferred the speed and simplicity of maintaining a static site over a PHP-driven blog/CMS. But I hated hand-coding HTML, and markup editors tended to be better for LaTeX-oriented processing and were simply over-engineered for my needs.

Happily, I enjoy using Markdown format and can crank out docs pretty quickly using it. Since Pelican supports Markdown as an input format, it seemed like a good place to start.

The net result is that andrewboring.com is now a Pelican site, and is hosted and served from Github pages.

The benefits are that I can knock out an article using Markdown. I can check it in at the command line if I'm at my desk, or write it directly on Github using the web interface if I'm not. It could hook into a CI/CD system that would build and deploy the site whenever master changes. I can focus on writing content, not fiddle-farting around with it in some new editor called "Gutenberg".

![This doesn't look like a Wordpress editor]({static}/media/steve-guttenberg.jpg)*This doesn't look like a Wordpress editor.*
