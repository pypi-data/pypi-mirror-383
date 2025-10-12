#!/usr/bin/env python
import time

from selenium import webdriver

DIMENSIONS = '1280x800'  # Default image dimensions width x height
WAIT = 2  # Default wait time to render web page


def get_browser(*, headless: bool = True, binary_location: str | None = None, **kwargs) -> webdriver.Firefox:
    """
    Create a Firefox webdriver instance. Auto-detects Firefox binary if not provided.

    On Ubuntu if Firefox is installed via snap, you may need to specify the binary location:

        binary_location='/snap/firefox/current/usr/lib/firefox/firefox'

    Args:
        headless: Run Firefox in headless mode (default: True)
        binary_location: Path to Firefox binary. If None, auto-detects snap installation.
        **kwargs: Additional Firefox arguments (e.g., width="1920", height="1080", etc.)

    Returns:
        Configured Firefox webdriver instance
    """
    options = webdriver.FirefoxOptions()

    if headless:
        options.add_argument('-headless')

    if binary_location is not None:
        options.binary_location = binary_location

    # Add any additional arguments from kwargs
    for key, value in kwargs.items():
        arg = f'-{key.replace("_", "-")}'  # Single leading dash for Firefox
        if value is True:
            options.add_argument(arg)
        elif value is not False and value is not None:
            options.add_argument(f'{arg}={value}')

    return webdriver.Firefox(options=options)


def capture(browser: webdriver.Firefox, url: str, image: str, dimensions: str = DIMENSIONS, wait: int = WAIT) -> None:
    width, height = (int(dim) for dim in dimensions.split('x'))
    browser.set_window_size(width, height)
    browser.get(url)
    browser.set_window_rect(x=0, y=0, width=width, height=height)
    time.sleep(wait)
    browser.save_screenshot(image)
