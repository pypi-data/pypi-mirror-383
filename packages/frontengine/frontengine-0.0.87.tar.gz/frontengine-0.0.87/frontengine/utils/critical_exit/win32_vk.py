win32_MOVE: int = 0x0001
win32_LEFTDOWN: int = 0x0002
win32_LEFTUP: int = 0x0004
win32_RIGHTDOWN: int = 0x0008
win32_RIGHTUP: int = 0x0010
win32_MIDDLEDOWN: int = 0x0020
win32_MIDDLEUP: int = 0x0040
win32_DOWN: int = 0x0080
win32_XUP: int = 0x0100
win32_WHEEL: int = 0x0800
win32_HWHEEL: int = 0x1000
win32_ABSOLUTE: int = 0x8000
win32_XBUTTON1: int = 0x0001
win32_XBUTTON2: int = 0x0002

win32_VK_LBUTTON: int = 0x01
win32_VK_RBUTTON: int = 0x02
win32_VK_MBUTTON: int = 0x04
win32_VK_XBUTTON1: int = 0x05
win32_VK_XBUTTON2: int = 0x06

"""
windows keyboard virtual keycode
"""

win32_EventF_EXTENDEDKEY: int = 0x0001
win32_EventF_KEYUP: int = 0x0002
win32_EventF_UNICODE: int = 0x0004
win32_EventF_SCANCODE: int = 0x0008

win32_VkToVSC: int = 0
win32_VK_CANCEL: int = 0x03
win32_VK_BACK: int = 0x08  # BACKSPACE key
win32_VK_TAB: int = 0x09  # TAB key
win32_VK_CLEAR: int = 0x0C  # CLEAR key
win32_VK_RETURN: int = 0x0D  # ENTER key
win32_VK_SHIFT: int = 0x10  # SHIFT key
win32_VK_CONTROL: int = 0x11  # CTRL key
win32_VK_Menu: int = 0x12  # ALT key
win32_VK_PAUSE: int = 0x13  # PAUSE key
win32_VK_CAPITAL: int = 0x14  # CAPS LOCK key
win32_VK_KANA: int = 0x15
win32_VK_IME_ON: int = 0x16
win32_VK_JUNJA: int = 0x17
win32_VK_FINAL: int = 0x18  # ESC key
win32_VK_HANJA: int = 0x19
win32_VK_IME_OFF: int = 0x1A
win32_VK_ESCAPE: int = 0x1B
win32_VK_CONVERT: int = 0x1C
win32_VK_NONCONVERT: int = 0x1D
win32_VK_ACCEPT: int = 0x1E
win32_VK_MODECHANGE: int = 0x1F
win32_VK_SPACE: int = 0x20  # SPACEBAR
win32_VK_PRIOR: int = 0x21  # PAGE UP key
win32_VK_NEXT: int = 0x22  # PAGE DOWN key
win32_VK_END: int = 0x23  # END key
win32_VK_HOME: int = 0x24  # HOME key
win32_VK_LEFT: int = 0x25  # LEFT ARROW key
win32_VK_UP: int = 0x26
win32_VK_RIGHT: int = 0x27
win32_VK_DOWN: int = 0x28
win32_VK_SELECT: int = 0x29
win32_VK_PRINT: int = 0x2A
win32_VK_EXECUTE: int = 0x2B
win32_VK_SNAPSHOT: int = 0x2C
win32_VK_INSERT: int = 0x2D
win32_VK_DELETE: int = 0x2E
win32_VK_HELP: int = 0x2F
win32_key0: int = 0x30
win32_key1: int = 0x31
win32_key2: int = 0x32
win32_key3: int = 0x33
win32_key4: int = 0x34
win32_key5: int = 0x35
win32_key6: int = 0x36
win32_key7: int = 0x37
win32_key8: int = 0x38
win32_key9: int = 0x39
win32_keyA: int = 0x41
win32_keyB: int = 0x42
win32_keyC: int = 0x43
win32_keyD: int = 0x44
win32_keyE: int = 0x45
win32_keyF: int = 0x46
win32_keyG: int = 0x47
win32_keyH: int = 0x48
win32_keyI: int = 0x49
win32_keyJ: int = 0x4A
win32_keyK: int = 0x4B
win32_keyL: int = 0x4C
win32_keyM: int = 0X4D
win32_keyN: int = 0x4E
win32_keyO: int = 0x4F
win32_keyP: int = 0x50
win32_keyQ: int = 0x51
win32_keyR: int = 0x52
win32_keyS: int = 0x53
win32_keyT: int = 0x54
win32_keyU: int = 0x55
win32_keyV: int = 0x56
win32_keyW: int = 0x57
win32_keyX: int = 0x58
win32_keyY: int = 0x59
win32_keyZ: int = 0x5A
win32_VK_LWIN: int = 0x5B  # Left Windows key (Natural keyboard)
win32_VK_RWIN: int = 0x5C  # Right Windows key (Natural keyboard)
win32_VK_APPS: int = 0x5D  # Applications key (Natural keyboard)
win32_VK_SLEEP: int = 0x5F  # Computer Sleep key
win32_VK_NUMPAD0: int = 0x60  # Numeric keypad 0 key
win32_VK_NUMPAD1: int = 0x61
win32_VK_NUMPAD2: int = 0x62
win32_VK_NUMPAD3: int = 0x63
win32_VK_NUMPAD4: int = 0x64
win32_VK_NUMPAD5: int = 0x65
win32_VK_NUMPAD6: int = 0x66
win32_VK_NUMPAD7: int = 0x67
win32_VK_NUMPAD8: int = 0x68
win32_VK_NUMPAD9: int = 0x69
win32_VK_MULTIPLY: int = 0x6A  # Multiply key
win32_VK_ADD: int = 0x6B  # Add key
win32_VK_SEPARATOR: int = 0x6C  # Separator key
win32_VK_SUBTRACT: int = 0x6D  # Subtract key
win32_VK_DECIMAL: int = 0x6E  # Decimal key
win32_VK_DIVIDE: int = 0x6F  # VK_DIVIDE
win32_VK_F1: int = 0x70  # F1
win32_VK_F2: int = 0x71
win32_VK_F3: int = 0x72
win32_VK_F4: int = 0x73
win32_VK_F5: int = 0x74
win32_VK_F6: int = 0x75
win32_VK_F7: int = 0x76
win32_VK_F8: int = 0x77
win32_VK_F9: int = 0x78
win32_VK_F10: int = 0x79
win32_VK_F11: int = 0x7A
win32_VK_F12: int = 0x7B
win32_VK_F13: int = 0x7C
win32_VK_F14: int = 0x7D
win32_VK_F15: int = 0x7E
win32_VK_F16: int = 0x7F
win32_VK_F17: int = 0x80
win32_VK_F18: int = 0x81
win32_VK_F19: int = 0x82
win32_VK_F20: int = 0x83
win32_VK_F21: int = 0x84
win32_VK_F22: int = 0x85
win32_VK_F23: int = 0x86
win32_VK_F24: int = 0x87
win32_VK_NUMLOCK: int = 0x90  # NUM LOCK key
win32_VK_SCROLL: int = 0x91  # SCROLL LOCK key
win32_VK_LSHIFT: int = 0xA0  # Left SHIFT key
win32_VK_RSHIFT: int = 0xA1
win32_VK_LCONTROL: int = 0xA2  # Left CONTROL key
win32_VK_RCONTROL: int = 0xA3  # Right CONTROL key
win32_VK_LMENU: int = 0xA4  # Left MENU key
win32_VK_RMENU: int = 0xA5  # Right MENU key
win32_VK_BROWSER_BACK: int = 0xA6  # Browser Back key
win32_VK_BROWSER_FORWARD: int = 0xA7  # Browser Forward key
win32_VK_BROWSER_REFRESH: int = 0xA8  # Browser Refresh key
win32_VK_BROWSER_STOP: int = 0xA9  # Browser Stop key
win32_VK_BROWSER_SEARCH: int = 0xAA  # Browser Search key
win32_VK_BROWSER_FAVORITES: int = 0xAB  # Browser Favorites key
win32_VK_VOLUME_MUTE: int = 0xAD
win32_VK_VOLUME_DOWN: int = 0xAE
win32_VK_VOLUME_UP: int = 0xAF
win32_VK_MEDIA_NEXT_TRACK: int = 0xB0
win32_VK_MEDIA_PREV_TRACK: int = 0xB1
win32_VK_MEDIA_STOP: int = 0xB2
win32_VK_MEDIA_PLAY_PAUSE: int = 0xB3
win32_VK_LAUNCH_MAIL: int = 0xB4
win32_VK_LAUNCH_MEDIA_SELECT: int = 0xB5
win32_VK_LAUNCH_APP1: int = 0xB6
win32_VK_LAUNCH_APP2: int = 0xB7

keyboard_keys_table = {
    "absolute": win32_ABSOLUTE,
    "eventf_extendedkey": win32_EventF_EXTENDEDKEY,
    "eventf_keyup": win32_EventF_KEYUP,
    "eventf_scancode": win32_EventF_SCANCODE,
    "eventf_unicode": win32_EventF_UNICODE,
    "hwheel": win32_HWHEEL,
    "leftdown": win32_LEFTDOWN,
    "leftup": win32_LEFTUP,
    "middledown": win32_MIDDLEDOWN,
    "middleup": win32_MIDDLEUP,
    "move": win32_MOVE,
    "rightdown": win32_RIGHTDOWN,
    "rightup": win32_RIGHTUP,
    "accept": win32_VK_ACCEPT,
    "add": win32_VK_ADD,
    "apps": win32_VK_APPS,
    "back": win32_VK_BACK,
    "browser_back": win32_VK_BROWSER_BACK,
    "browser_favorites": win32_VK_BROWSER_FAVORITES,
    "browser_forward": win32_VK_BROWSER_FORWARD,
    "browser_refresh": win32_VK_BROWSER_REFRESH,
    "browser_search": win32_VK_BROWSER_SEARCH,
    "browser_stop": win32_VK_BROWSER_STOP,
    "cancel": win32_VK_CANCEL,
    "capital": win32_VK_CAPITAL,
    "clear": win32_VK_CLEAR,
    "control": win32_VK_CONTROL,
    "convert": win32_VK_CONVERT,
    "decimal": win32_VK_DECIMAL,
    "delete": win32_VK_DELETE,
    "divide": win32_VK_DIVIDE,
    "vk_down": win32_VK_DOWN,
    "end": win32_VK_END,
    "escape": win32_VK_ESCAPE,
    "execute": win32_VK_EXECUTE,
    "f1": win32_VK_F1,
    "f2": win32_VK_F2,
    "f3": win32_VK_F3,
    "f4": win32_VK_F4,
    "f5": win32_VK_F5,
    "f6": win32_VK_F6,
    "f7": win32_VK_F7,
    "f8": win32_VK_F8,
    "f9": win32_VK_F9,
    "f10": win32_VK_F10,
    "f11": win32_VK_F11,
    "f12": win32_VK_F12,
    "f13": win32_VK_F13,
    "f14": win32_VK_F14,
    "f15": win32_VK_F15,
    "f16": win32_VK_F16,
    "f17": win32_VK_F17,
    "f18": win32_VK_F18,
    "f19": win32_VK_F19,
    "f20": win32_VK_F20,
    "f21": win32_VK_F21,
    "f22": win32_VK_F22,
    "f23": win32_VK_F23,
    "f24": win32_VK_F24,
    "final": win32_VK_FINAL,
    "hanja": win32_VK_HANJA,
    "help": win32_VK_HELP,
    "home": win32_VK_HOME,
    "ime_off": win32_VK_IME_OFF,
    "ime_on": win32_VK_IME_ON,
    "insert": win32_VK_INSERT,
    "junja": win32_VK_JUNJA,
    "kana": win32_VK_KANA,
    "launch_app1": win32_VK_LAUNCH_APP1,
    "LAUNCH_APP2": win32_VK_LAUNCH_APP2,
    "launch_mail": win32_VK_LAUNCH_MAIL,
    "launch_media_select": win32_VK_LAUNCH_MEDIA_SELECT,
    "lbutton": win32_VK_LBUTTON,
    "lcontrol": win32_VK_LCONTROL,
    "left": win32_VK_LEFT,
    "lmenu": win32_VK_LMENU,
    "lshift": win32_VK_LSHIFT,
    "lwin": win32_VK_LWIN,
    "mbutton": win32_VK_MBUTTON,
    "media_next_track": win32_VK_MEDIA_NEXT_TRACK,
    "media_play_pause": win32_VK_MEDIA_PLAY_PAUSE,
    "media_prev_track": win32_VK_MEDIA_PREV_TRACK,
    "media_stop": win32_VK_MEDIA_STOP,
    "modechange": win32_VK_MODECHANGE,
    "multiply": win32_VK_MULTIPLY,
    "menu": win32_VK_Menu,
    "next": win32_VK_NEXT,
    "nonconvert": win32_VK_NONCONVERT,
    "numlock": win32_VK_NUMLOCK,
    "num0": win32_VK_NUMPAD0,
    "num1": win32_VK_NUMPAD1,
    "num2": win32_VK_NUMPAD2,
    "num3": win32_VK_NUMPAD3,
    "num4": win32_VK_NUMPAD4,
    "num5": win32_VK_NUMPAD5,
    "num6": win32_VK_NUMPAD6,
    "num7": win32_VK_NUMPAD7,
    "num8": win32_VK_NUMPAD8,
    "num9": win32_VK_NUMPAD9,
    "pause": win32_VK_PAUSE,
    "print": win32_VK_PRINT,
    "prior": win32_VK_PRIOR,
    "rbutton": win32_VK_RBUTTON,
    "rcontrol": win32_VK_RCONTROL,
    "return": win32_VK_RETURN,
    "right": win32_VK_RIGHT,
    "rmenu": win32_VK_RMENU,
    "rshift": win32_VK_RSHIFT,
    "rwin": win32_VK_RWIN,
    "scroll": win32_VK_SCROLL,
    "select": win32_VK_SELECT,
    "separator": win32_VK_SEPARATOR,
    "shift": win32_VK_SHIFT,
    "sleep": win32_VK_SLEEP,
    "snapshot": win32_VK_SNAPSHOT,
    "space": win32_VK_SPACE,
    "subtract": win32_VK_SUBTRACT,
    "tab": win32_VK_TAB,
    "up": win32_VK_UP,
    "volume_down": win32_VK_VOLUME_DOWN,
    "volume_mute": win32_VK_VOLUME_MUTE,
    "volume_up": win32_VK_VOLUME_UP,
    "vk_xbutton1": win32_VK_XBUTTON1,
    "vk_xbutton2": win32_VK_XBUTTON2,
    "xbutton1": win32_XBUTTON1,
    "xbutton2": win32_XBUTTON2,
    "vktovsc": win32_VkToVSC,
    "wheel": win32_WHEEL,
    "down": win32_DOWN,
    "xup": win32_XUP,
    "0": win32_key0,
    "1": win32_key1,
    "2": win32_key2,
    "3": win32_key3,
    "4": win32_key4,
    "5": win32_key5,
    "6": win32_key6,
    "7": win32_key7,
    "8": win32_key8,
    "9": win32_key9,
    "A": win32_keyA,
    "a": win32_keyA,
    "B": win32_keyB,
    "b": win32_keyB,
    "C": win32_keyC,
    "c": win32_keyC,
    "D": win32_keyD,
    "d": win32_keyD,
    "E": win32_keyE,
    "e": win32_keyE,
    "F": win32_keyF,
    "f": win32_keyF,
    "G": win32_keyG,
    "g": win32_keyG,
    "H": win32_keyH,
    "h": win32_keyH,
    "I": win32_keyI,
    "i": win32_keyI,
    "J": win32_keyJ,
    "j": win32_keyJ,
    "K": win32_keyK,
    "k": win32_keyK,
    "L": win32_keyL,
    "l": win32_keyL,
    "M": win32_keyM,
    "m": win32_keyM,
    "N": win32_keyN,
    "n": win32_keyN,
    "O": win32_keyO,
    "o": win32_keyO,
    "P": win32_keyP,
    "p": win32_keyP,
    "Q": win32_keyQ,
    "q": win32_keyQ,
    "R": win32_keyR,
    "r": win32_keyR,
    "S": win32_keyS,
    "s": win32_keyS,
    "T": win32_keyT,
    "t": win32_keyT,
    "U": win32_keyU,
    "u": win32_keyU,
    "V": win32_keyV,
    "v": win32_keyV,
    "W": win32_keyW,
    "w": win32_keyW,
    "X": win32_keyX,
    "x": win32_keyX,
    "Y": win32_keyY,
    "y": win32_keyY,
    "Z": win32_keyZ,
    "z": win32_keyZ,
}
