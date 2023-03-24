# varnish-cache-warmer

This is a python script to heat Varnish pointing to the website's sitemap.xml

# Requirements

Use selenium in python and the website must have a sitemap.xml to work using the full crawl type.

# Executing the script

You must pass the URL of the web as well as the type of crawl you want to perform ("full or only") full for the complete sitemap of the site or only for a specific url to the script like this:

$ py .\getXHR.py http://midominio.com/ full

or

$ py .\getXHR.py http://midominio.com/test-page only
