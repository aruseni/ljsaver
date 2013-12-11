LJ Saver
========

Saves all posts of the given blog hosted at livejournal.com.

Usage:

    python ljsaver.py [username] [directory]
    
Where:

* **username** is the username of the LJ user who writes the blog
* **directory** is the directory to save the HTML files for each entry

For example:

    python ljsaver.py tema tema_lj/

*Saves all posts for tema.livejournal.com to the tema_lj dir (you should create it before running the program).*

On startup, you will be prompted for your LJ username and password (LJ Saver will use it to gain access to the non-public posts that are available to you). You can skip entering your credentials if you want to only crawl public posts.

As the program runs, the names of the saved HTML files will be displayed (together with the title if it is available).
