# wcap

Capture web pages as images using Selenium and the Firefox webdriver.

# Usage

    wcap --dimensions 1500x1100 --wait 5 https://ukealong.com/key/c/ img/c.png

If Firefox is installed as a Snap on Ubuntu, you need to set the binary location.

    wcap --dimensions 1500x1100 --wait 5 --binary-location /snap/firefox/current/usr/lib/firefox/firefox https://ukealong.com/key/c/ img/c.png

# Installation

    pip install wcap

In order for `wcap` to work you need to install the [Firefox web browser](https://www.mozilla.org/firefox) and [geckodriver](https://github.com/mozilla/geckodriver). To install `geckodriver` download the release for your operating system from https://github.com/mozilla/geckodriver/releases and move the executable file to a directory that is included in your PATH environment variable.

## Authors

`wcap` was written by [Ramiro Gómez](https://ramiro.org/).