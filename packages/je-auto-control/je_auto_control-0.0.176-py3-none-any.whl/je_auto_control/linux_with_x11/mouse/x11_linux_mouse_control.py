import sys
import time
from typing import Tuple

from je_auto_control.utils.exception.exception_tags import linux_import_error
from je_auto_control.utils.exception.exceptions import AutoControlException

if sys.platform not in ["linux", "linux2"]:
    raise AutoControlException(linux_import_error)

from Xlib import X, protocol
from Xlib.ext.xtest import fake_input

from je_auto_control.linux_with_x11.core.utils.x11_linux_display import display

x11_linux_mouse_left = 1
x11_linux_mouse_middle = 2
x11_linux_mouse_right = 3
x11_linux_scroll_direction_up = 4
x11_linux_scroll_direction_down = 5
x11_linux_scroll_direction_left = 6
x11_linux_scroll_direction_right = 7


def position() -> Tuple[int, int]:
    """
    get mouse current position
    """
    coord = display.screen().root.query_pointer()._data
    return coord["root_x"], coord["root_y"]


def set_position(x: int, y: int) -> None:
    """
    :param x we want to set mouse x position
    :param y we want to set mouse y position
    """
    time.sleep(0.01)
    fake_input(display, X.MotionNotify, x=x, y=y)
    display.sync()


def press_mouse(mouse_keycode: int) -> None:
    """
    :param mouse_keycode mouse keycode we want to press
    """
    time.sleep(0.01)
    fake_input(display, X.ButtonPress, mouse_keycode)
    display.sync()


def release_mouse(mouse_keycode: int) -> None:
    """
    :param mouse_keycode which mouse keycode we want to release
    """
    time.sleep(0.01)
    fake_input(display, X.ButtonRelease, mouse_keycode)
    display.sync()


def click_mouse(mouse_keycode: int, x=None, y=None) -> None:
    """
    :param mouse_keycode which mouse keycode we want to click
    :param x set mouse x position
    :param y set mouse y position
    """
    if x and y is not None:
        set_position(x, y)
    press_mouse(mouse_keycode)
    release_mouse(mouse_keycode)


def scroll(scroll_value: int, scroll_direction: int) -> None:
    """"
    :param scroll_value scroll unit
    :param scroll_direction what direction you want to scroll
    scroll_direction = 4 : direction up
    scroll_direction = 5 : direction down
    scroll_direction = 6 : direction left
    scroll_direction = 7 : direction right
    """
    total = 0
    for i in range(scroll_value):
        click_mouse(scroll_direction)
        total = total + i

def send_mouse_event_to_window(window_id, mouse_keycode: int, x: int = None, y: int = None):
    window = display.create_resource_object('window', window_id)
    for ev_type in (X.ButtonPress, X.ButtonRelease):
        ev = protocol.event.ButtonPress(
            time=X.CurrentTime,
            root=display.screen().root,
            window=window,
            same_screen=1,
            child=X.NONE,
            root_x=x, root_y=y, event_x=x, event_y=y,
            state=0,
            detail=mouse_keycode
        )
        ev.type = ev_type
        window.send_event(ev, propagate=True)
    display.flush()



