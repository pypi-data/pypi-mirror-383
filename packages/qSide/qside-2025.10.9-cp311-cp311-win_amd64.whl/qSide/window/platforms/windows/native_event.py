import ctypes
from ctypes.wintypes import POINT

import win32con
import win32gui

from qtpy.QtCore import QByteArray, QPoint, Qt, QEvent
from qtpy.QtGui import QMouseEvent
from qtpy.QtWidgets import QWidget, QPushButton, QApplication

from .c_structures import LPNCCALCSIZE_PARAMS
from .titlebar import MaximizeButtonState
from .utils import is_maximized, is_full_screen


def _native_event(widget: QWidget, event_type: QByteArray, message: int):
    msg = ctypes.wintypes.MSG.from_address(message.__int__())

    geo = widget.geometry()
    r = widget.devicePixelRatioF()

    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    x = int(pt.x / r) - geo.x()
    y = int(pt.y / r) - geo.y()

    user32 = ctypes.windll.user32
    dpi = user32.GetDpiForWindow(msg.hWnd)
    borderWidth = user32.GetSystemMetricsForDpi(win32con.SM_CXSIZEFRAME, dpi)# + user32.GetSystemMetricsForDpi(92, dpi)
    borderHeight = user32.GetSystemMetricsForDpi(win32con.SM_CYSIZEFRAME, dpi)# + user32.GetSystemMetricsForDpi(92, dpi)

    if msg.message == win32con.WM_NCHITTEST:
        if widget.isResizable() and not is_maximized(msg.hWnd):
            w, h = geo.width(), geo.height()
            lx = x < borderWidth
            rx = x >= w - borderWidth
            ty = y < borderHeight
            by = y >= h - borderHeight

            if lx and ty:
                return True, win32con.HTTOPLEFT
            if rx and by:
                return True, win32con.HTBOTTOMRIGHT
            if rx and ty:
                return True, win32con.HTTOPRIGHT
            if lx and by:
                return True, win32con.HTBOTTOMLEFT
            if ty:
                return True, win32con.HTTOP
            if by:
                return True, win32con.HTBOTTOM
            if lx:
                return True, win32con.HTLEFT
            if rx:
                return True, win32con.HTRIGHT

        if widget.childAt(QPoint(x, y)) is widget._titleBar.maximizeButton:
            widget._titleBar.maximizeButton.setState(MaximizeButtonState.Hover)
            return True, win32con.HTMAXBUTTON

        if widget.childAt(x, y) not in widget._titleBar.findChildren(QPushButton):
            return False, 0
            # if borderHeight < y < widget._titleBar.height():
            #     return True, win32con.HTCAPTION

    elif msg.message == win32con.WM_MOVE:
        win32gui.SetWindowPos(msg.hWnd, None, 0, 0, 0, 0, win32con.SWP_NOMOVE |
                              win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)

    elif msg.message in [0x2A2, win32con.WM_MOUSELEAVE]:
        widget._titleBar.maximizeButton.setState(MaximizeButtonState.Normal)
    elif msg.message in [win32con.WM_NCLBUTTONDOWN, win32con.WM_NCLBUTTONDBLCLK]:
        if widget.childAt(QPoint(x, y)) is widget._titleBar.maximizeButton:
            QApplication.sendEvent(widget._titleBar.maximizeButton, QMouseEvent(
                QEvent.MouseButtonPress, QPoint(), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier))
            return True, 0
    elif msg.message in [win32con.WM_NCLBUTTONUP, win32con.WM_NCRBUTTONUP]:
        if widget.childAt(QPoint(x, y)) is widget._titleBar.maximizeButton:
            QApplication.sendEvent(widget._titleBar.maximizeButton, QMouseEvent(
                QEvent.MouseButtonRelease, QPoint(), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier))

    elif msg.message == win32con.WM_NCCALCSIZE:
        rect = ctypes.cast(msg.lParam, LPNCCALCSIZE_PARAMS).contents.rgrc[0]

        isMax = is_maximized(msg.hWnd)
        isFull = is_full_screen(msg.hWnd)

        # adjust the size of client rect
        if isMax and not isFull:
            rect.top += borderHeight
            rect.left += borderWidth
            rect.right -= borderWidth
            rect.bottom -= borderHeight

        result = 0 if not msg.wParam else win32con.WVR_REDRAW
        return True, win32con.WVR_REDRAW

    return False, 0
