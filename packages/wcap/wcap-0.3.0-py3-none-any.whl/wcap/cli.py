import argparse

from wcap.api import DIMENSIONS, WAIT, capture, get_browser


def main(args=None):
    parser = argparse.ArgumentParser(description='Create and download screenshot for URL.')
    parser.add_argument('url', metavar='URL', type=str, help='Web page URL')
    parser.add_argument('image', metavar='IMAGE', type=str, help='Image file name')
    parser.add_argument('--dimensions', '-d', type=str, default=DIMENSIONS)
    parser.add_argument('--binary-location', '-b', type=str, default=None)
    parser.add_argument('--wait', '-w', type=int, default=WAIT)

    argv = parser.parse_args(args)
    browser = get_browser(binary_location=argv.binary_location)
    capture(browser, argv.url, argv.image, argv.dimensions, argv.wait)
    browser.close()


if __name__ == '__main__':
    main()
