import sys

from je_auto_control.utils.exception.exceptions import AutoControlException
from je_auto_control.utils.logging.loggin_instance import autocontrol_logger

if sys.platform in ["win32", "cygwin", "msys"]:
    from je_auto_control.windows.core.utils.win32_vk import WIN32_ABSOLUTE
    from je_auto_control.windows.core.utils.win32_vk import WIN32_EventF_EXTENDEDKEY
    from je_auto_control.windows.core.utils.win32_vk import WIN32_EventF_KEYUP
    from je_auto_control.windows.core.utils.win32_vk import WIN32_EventF_SCANCODE
    from je_auto_control.windows.core.utils.win32_vk import WIN32_EventF_UNICODE
    from je_auto_control.windows.core.utils.win32_vk import WIN32_HWHEEL
    from je_auto_control.windows.core.utils.win32_vk import WIN32_LEFTDOWN
    from je_auto_control.windows.core.utils.win32_vk import WIN32_LEFTUP
    from je_auto_control.windows.core.utils.win32_vk import WIN32_MIDDLEDOWN
    from je_auto_control.windows.core.utils.win32_vk import WIN32_MIDDLEUP
    from je_auto_control.windows.core.utils.win32_vk import WIN32_MOVE
    from je_auto_control.windows.core.utils.win32_vk import WIN32_RIGHTDOWN
    from je_auto_control.windows.core.utils.win32_vk import WIN32_RIGHTUP
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_ACCEPT
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_ADD
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_APPS
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_BACK
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_BROWSER_BACK
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_BROWSER_FAVORITES
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_BROWSER_FORWARD
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_BROWSER_REFRESH
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_BROWSER_SEARCH
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_BROWSER_STOP
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_CANCEL
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_CAPITAL
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_CLEAR
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_CONTROL
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_CONVERT
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_DECIMAL
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_DELETE
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_DIVIDE
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_DOWN
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_END
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_ESCAPE
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_EXECUTE
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F1
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F10
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F11
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F12
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F13
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F14
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F15
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F16
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F17
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F18
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F19
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F2
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F20
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F21
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F22
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F23
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F24
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F3
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F4
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F5
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F6
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F7
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F8
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_F9
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_FINAL
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_HANJA
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_HELP
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_HOME
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_IME_OFF
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_IME_ON
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_INSERT
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_JUNJA
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_KANA
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_LAUNCH_APP1
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_LAUNCH_APP2
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_LAUNCH_MAIL
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_LAUNCH_MEDIA_SELECT
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_LBUTTON
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_LCONTROL
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_LEFT
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_LMENU
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_LSHIFT
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_LWIN
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_MBUTTON
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_MEDIA_NEXT_TRACK
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_MEDIA_PLAY_PAUSE
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_MEDIA_PREV_TRACK
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_MEDIA_STOP
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_MODECHANGE
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_MULTIPLY
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_Menu
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_NEXT
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_NONCONVERT
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_NUMLOCK
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_NUMPAD0
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_NUMPAD1
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_NUMPAD2
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_NUMPAD3
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_NUMPAD4
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_NUMPAD5
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_NUMPAD6
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_NUMPAD7
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_NUMPAD8
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_NUMPAD9
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_PAUSE
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_PRINT
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_PRIOR
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_RBUTTON
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_RCONTROL
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_RETURN
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_RIGHT
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_RMENU
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_RSHIFT
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_RWIN
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_SCROLL
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_SELECT
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_SEPARATOR
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_SHIFT
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_SLEEP
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_SNAPSHOT
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_SPACE
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_SUBTRACT
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_TAB
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_UP
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_VOLUME_DOWN
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_VOLUME_MUTE
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_VOLUME_UP
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_XBUTTON1
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VK_XBUTTON2
    from je_auto_control.windows.core.utils.win32_vk import WIN32_VkToVSC
    from je_auto_control.windows.core.utils.win32_vk import WIN32_WHEEL
    from je_auto_control.windows.core.utils.win32_vk import WIN32_XBUTTON1
    from je_auto_control.windows.core.utils.win32_vk import WIN32_XBUTTON2
    from je_auto_control.windows.core.utils.win32_vk import WIN32_DOWN
    from je_auto_control.windows.core.utils.win32_vk import WIN32_XUP
    from je_auto_control.windows.core.utils.win32_vk import WIN32_key0
    from je_auto_control.windows.core.utils.win32_vk import WIN32_key1
    from je_auto_control.windows.core.utils.win32_vk import WIN32_key2
    from je_auto_control.windows.core.utils.win32_vk import WIN32_key3
    from je_auto_control.windows.core.utils.win32_vk import WIN32_key4
    from je_auto_control.windows.core.utils.win32_vk import WIN32_key5
    from je_auto_control.windows.core.utils.win32_vk import WIN32_key6
    from je_auto_control.windows.core.utils.win32_vk import WIN32_key7
    from je_auto_control.windows.core.utils.win32_vk import WIN32_key8
    from je_auto_control.windows.core.utils.win32_vk import WIN32_key9
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyA
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyB
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyC
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyD
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyE
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyF
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyG
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyH
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyI
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyJ
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyK
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyL
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyM
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyN
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyO
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyP
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyQ
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyR
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyS
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyT
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyU
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyV
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyW
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyX
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyY
    from je_auto_control.windows.core.utils.win32_vk import WIN32_keyZ
    from je_auto_control.windows.keyboard import win32_ctype_keyboard_control
    from je_auto_control.windows.mouse import win32_ctype_mouse_control
    from je_auto_control.windows.mouse.win32_ctype_mouse_control import win32_mouse_left
    from je_auto_control.windows.mouse.win32_ctype_mouse_control import win32_mouse_middle
    from je_auto_control.windows.mouse.win32_ctype_mouse_control import win32_mouse_right
    from je_auto_control.windows.mouse.win32_ctype_mouse_control import win32_mouse_x1
    from je_auto_control.windows.mouse.win32_ctype_mouse_control import win32_mouse_x2
    from je_auto_control.windows.screen import win32_screen
    from je_auto_control.windows.record.win32_record import win32_recorder
    from je_auto_control.windows.core.utils import win32_keypress_check

elif sys.platform in ["darwin"]:
    from je_auto_control.osx.core.utils.osx_vk import osx_key_a, osx_key_A
    from je_auto_control.osx.core.utils.osx_vk import osx_key_b, osx_key_B
    from je_auto_control.osx.core.utils.osx_vk import osx_key_c, osx_key_C
    from je_auto_control.osx.core.utils.osx_vk import osx_key_d, osx_key_D
    from je_auto_control.osx.core.utils.osx_vk import osx_key_e, osx_key_E
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f, osx_key_F
    from je_auto_control.osx.core.utils.osx_vk import osx_key_g, osx_key_G
    from je_auto_control.osx.core.utils.osx_vk import osx_key_h, osx_key_H
    from je_auto_control.osx.core.utils.osx_vk import osx_key_i, osx_key_I
    from je_auto_control.osx.core.utils.osx_vk import osx_key_j, osx_key_J
    from je_auto_control.osx.core.utils.osx_vk import osx_key_k, osx_key_K
    from je_auto_control.osx.core.utils.osx_vk import osx_key_l, osx_key_L
    from je_auto_control.osx.core.utils.osx_vk import osx_key_m, osx_key_M
    from je_auto_control.osx.core.utils.osx_vk import osx_key_n, osx_key_N
    from je_auto_control.osx.core.utils.osx_vk import osx_key_o, osx_key_O
    from je_auto_control.osx.core.utils.osx_vk import osx_key_p, osx_key_P
    from je_auto_control.osx.core.utils.osx_vk import osx_key_q, osx_key_Q
    from je_auto_control.osx.core.utils.osx_vk import osx_key_r, osx_key_R
    from je_auto_control.osx.core.utils.osx_vk import osx_key_s, osx_key_S
    from je_auto_control.osx.core.utils.osx_vk import osx_key_t, osx_key_T
    from je_auto_control.osx.core.utils.osx_vk import osx_key_u, osx_key_U
    from je_auto_control.osx.core.utils.osx_vk import osx_key_v, osx_key_V
    from je_auto_control.osx.core.utils.osx_vk import osx_key_w, osx_key_W
    from je_auto_control.osx.core.utils.osx_vk import osx_key_x, osx_key_X
    from je_auto_control.osx.core.utils.osx_vk import osx_key_y, osx_key_Y
    from je_auto_control.osx.core.utils.osx_vk import osx_key_z, osx_key_Z
    from je_auto_control.osx.core.utils.osx_vk import osx_key_1, osx_key_exclam
    from je_auto_control.osx.core.utils.osx_vk import osx_key_2, osx_key_at
    from je_auto_control.osx.core.utils.osx_vk import osx_key_3, osx_key_numbersign
    from je_auto_control.osx.core.utils.osx_vk import osx_key_4, osx_key_money
    from je_auto_control.osx.core.utils.osx_vk import osx_key_5, osx_key_percent
    from je_auto_control.osx.core.utils.osx_vk import osx_key_6, osx_key_asciicircum
    from je_auto_control.osx.core.utils.osx_vk import osx_key_7, osx_key_ampersand
    from je_auto_control.osx.core.utils.osx_vk import osx_key_8, osx_key_asterisk
    from je_auto_control.osx.core.utils.osx_vk import osx_key_9, osx_key_parenleft
    from je_auto_control.osx.core.utils.osx_vk import osx_key_0, osx_key_parenright
    from je_auto_control.osx.core.utils.osx_vk import osx_key_equal, osx_key_plus
    from je_auto_control.osx.core.utils.osx_vk import osx_key_minus, osx_key_underscore
    from je_auto_control.osx.core.utils.osx_vk import osx_key_bracketright, osx_key_braceright
    from je_auto_control.osx.core.utils.osx_vk import osx_key_bracketleft, osx_key_braceleft
    from je_auto_control.osx.core.utils.osx_vk import osx_key_apostrophe, osx_key_quotedbl
    from je_auto_control.osx.core.utils.osx_vk import osx_key_semicolon, osx_key_colon
    from je_auto_control.osx.core.utils.osx_vk import osx_key_backslash, osx_key_bar
    from je_auto_control.osx.core.utils.osx_vk import osx_key_comma, osx_key_less
    from je_auto_control.osx.core.utils.osx_vk import osx_key_salsh, osx_key_question
    from je_auto_control.osx.core.utils.osx_vk import osx_key_period, osx_key_greater
    from je_auto_control.osx.core.utils.osx_vk import osx_key_grave, osx_key_asciitilde
    from je_auto_control.osx.core.utils.osx_vk import osx_key_space
    from je_auto_control.osx.core.utils.osx_vk import osx_key_return, osx_key_newline, osx_key_enter
    from je_auto_control.osx.core.utils.osx_vk import osx_key_tab
    from je_auto_control.osx.core.utils.osx_vk import osx_key_backspace
    from je_auto_control.osx.core.utils.osx_vk import osx_key_esc
    from je_auto_control.osx.core.utils.osx_vk import osx_key_command
    from je_auto_control.osx.core.utils.osx_vk import osx_key_shift
    from je_auto_control.osx.core.utils.osx_vk import osx_key_caps_lock
    from je_auto_control.osx.core.utils.osx_vk import osx_key_option, osx_key_alt
    from je_auto_control.osx.core.utils.osx_vk import osx_key_ctrl
    from je_auto_control.osx.core.utils.osx_vk import osx_key_shift_right
    from je_auto_control.osx.core.utils.osx_vk import osx_key_option_right
    from je_auto_control.osx.core.utils.osx_vk import osx_key_control_right
    from je_auto_control.osx.core.utils.osx_vk import osx_key_fn
    from je_auto_control.osx.core.utils.osx_vk import osx_key_volume_up
    from je_auto_control.osx.core.utils.osx_vk import osx_key_volume_down
    from je_auto_control.osx.core.utils.osx_vk import osx_key_volume_mute
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f1
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f2
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f3
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f4
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f5
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f6
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f7
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f8
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f9
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f10
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f11
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f12
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f13
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f14
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f15
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f16
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f17
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f18
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f19
    from je_auto_control.osx.core.utils.osx_vk import osx_key_f20
    from je_auto_control.osx.core.utils.osx_vk import osx_key_help
    from je_auto_control.osx.core.utils.osx_vk import osx_key_home
    from je_auto_control.osx.core.utils.osx_vk import osx_key_pageup
    from je_auto_control.osx.core.utils.osx_vk import osx_key_end
    from je_auto_control.osx.core.utils.osx_vk import osx_key_pagedown
    from je_auto_control.osx.core.utils.osx_vk import osx_key_left
    from je_auto_control.osx.core.utils.osx_vk import osx_key_right
    from je_auto_control.osx.core.utils.osx_vk import osx_key_down
    from je_auto_control.osx.core.utils.osx_vk import osx_key_up
    from je_auto_control.osx.core.utils.osx_vk import osx_key_yen
    from je_auto_control.osx.core.utils.osx_vk import osx_key_eisu
    from je_auto_control.osx.core.utils.osx_vk import osx_key_kana
    from je_auto_control.osx.core.utils.osx_vk import osx_mouse_left
    from je_auto_control.osx.core.utils.osx_vk import osx_mouse_middle
    from je_auto_control.osx.core.utils.osx_vk import osx_mouse_right
    from je_auto_control.osx.mouse import osx_mouse
    from je_auto_control.osx.screen import osx_screen
    from je_auto_control.osx.keyboard import osx_keyboard
    from je_auto_control.osx.keyboard import osx_keyboard_check

elif sys.platform in ["linux", "linux2"]:
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_backspace
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_slash_b
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_tab
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_enter
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_return
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_shift
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_ctrl
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_alt
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_pause
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_capslock
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_esc
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_pgup
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_pgdn
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_pageup
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_pagedown
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_end
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_home
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_left
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_up
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_right
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_down
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_select
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_print
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_execute
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_prtsc
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_prtscr
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_prntscrn
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_insert
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_del
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_delete
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_help
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_win
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_winleft
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_winright
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_apps
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_num0
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_num1
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_num2
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_num3
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_num4
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_num5
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_num6
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_num7
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_num8
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_num9
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_multiply
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_add
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_separator
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_subtract
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_decimal
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_divide
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f1
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f2
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f3
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f4
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f5
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f6
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f7
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f8
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f9
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f10
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f11
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f12
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f13
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f14
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f15
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f16
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f17
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f18
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f19
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f20
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f21
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f22
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f23
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f24
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_numlock
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_scrolllock
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_shiftleft
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_shiftright
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_ctrlleft
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_ctrlright
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_altleft
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_altright
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_space
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_newline_n
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_newline_r
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_newline_t
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_exclam
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_numbersign
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_percent
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_dollar
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_ampersand
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_quotedbl
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_apostrophe
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_parenleft
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_parenright
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_asterisk
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_equal
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_plus
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_comma
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_minus
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_period
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_slash
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_colon
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_semicolon
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_less
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_greater
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_question
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_at
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_bracketleft
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_bracketright
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_backslash
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_asciicircum
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_underscore
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_grave
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_braceleft
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_bar
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_braceright
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_asciitilde
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_a
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_b
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_c
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_d
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_e
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_f
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_g
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_h
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_i
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_j
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_k
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_l
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_m
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_n
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_o
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_p
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_q
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_r
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_s
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_t
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_u
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_v
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_w
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_x
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_y
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_z
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_A
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_B
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_C
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_D
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_E
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_F
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_G
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_H
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_I
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_J
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_K
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_L
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_M
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_N
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_O
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_P
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_Q
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_R
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_S
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_T
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_U
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_V
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_W
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_X
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_Y
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_Z
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_1
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_2
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_3
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_4
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_5
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_6
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_7
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_8
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_9
    from je_auto_control.linux_with_x11.core.utils.x11_linux_vk import x11_linux_key_0
    from je_auto_control.linux_with_x11.mouse.x11_linux_mouse_control import x11_linux_mouse_left
    from je_auto_control.linux_with_x11.mouse.x11_linux_mouse_control import x11_linux_mouse_middle
    from je_auto_control.linux_with_x11.mouse.x11_linux_mouse_control import x11_linux_mouse_right
    from je_auto_control.linux_with_x11.mouse.x11_linux_mouse_control import x11_linux_scroll_direction_up
    from je_auto_control.linux_with_x11.mouse.x11_linux_mouse_control import x11_linux_scroll_direction_down
    from je_auto_control.linux_with_x11.mouse.x11_linux_mouse_control import x11_linux_scroll_direction_left
    from je_auto_control.linux_with_x11.mouse.x11_linux_mouse_control import x11_linux_scroll_direction_right
    from je_auto_control.linux_with_x11.keyboard import x11_linux_keyboard_control
    from je_auto_control.linux_with_x11.listener import x11_linux_listener
    from je_auto_control.linux_with_x11.mouse import x11_linux_mouse_control
    from je_auto_control.linux_with_x11.screen import x11_linux_screen
    from je_auto_control.linux_with_x11.record.x11_linux_record import x11_linux_recoder

else:
    raise AutoControlException("unknown operating system")

keyboard_keys_table = None
mouse_keys_table = None
special_mouse_keys_table = None
keyboard = None
keyboard_check = None
mouse = None
screen = None
recorder = None

if sys.platform in ["win32", "cygwin", "msys"]:
    autocontrol_logger.info("Load Windows Setting")
    keyboard_keys_table = {
        "absolute": WIN32_ABSOLUTE,
        "eventf_extendedkey": WIN32_EventF_EXTENDEDKEY,
        "eventf_keyup": WIN32_EventF_KEYUP,
        "eventf_scancode": WIN32_EventF_SCANCODE,
        "eventf_unicode": WIN32_EventF_UNICODE,
        "hwheel": WIN32_HWHEEL,
        "leftdown": WIN32_LEFTDOWN,
        "leftup": WIN32_LEFTUP,
        "middledown": WIN32_MIDDLEDOWN,
        "middleup": WIN32_MIDDLEUP,
        "move": WIN32_MOVE,
        "rightdown": WIN32_RIGHTDOWN,
        "rightup": WIN32_RIGHTUP,
        "accept": WIN32_VK_ACCEPT,
        "add": WIN32_VK_ADD,
        "apps": WIN32_VK_APPS,
        "back": WIN32_VK_BACK,
        "browser_back": WIN32_VK_BROWSER_BACK,
        "browser_favorites": WIN32_VK_BROWSER_FAVORITES,
        "browser_forward": WIN32_VK_BROWSER_FORWARD,
        "browser_refresh": WIN32_VK_BROWSER_REFRESH,
        "browser_search": WIN32_VK_BROWSER_SEARCH,
        "browser_stop": WIN32_VK_BROWSER_STOP,
        "cancel": WIN32_VK_CANCEL,
        "capital": WIN32_VK_CAPITAL,
        "clear": WIN32_VK_CLEAR,
        "control": WIN32_VK_CONTROL,
        "convert": WIN32_VK_CONVERT,
        "decimal": WIN32_VK_DECIMAL,
        "delete": WIN32_VK_DELETE,
        "divide": WIN32_VK_DIVIDE,
        "vk_down": WIN32_VK_DOWN,
        "end": WIN32_VK_END,
        "escape": WIN32_VK_ESCAPE,
        "execute": WIN32_VK_EXECUTE,
        "f1": WIN32_VK_F1,
        "f2": WIN32_VK_F2,
        "f3": WIN32_VK_F3,
        "f4": WIN32_VK_F4,
        "f5": WIN32_VK_F5,
        "f6": WIN32_VK_F6,
        "f7": WIN32_VK_F7,
        "f8": WIN32_VK_F8,
        "f9": WIN32_VK_F9,
        "f10": WIN32_VK_F10,
        "f11": WIN32_VK_F11,
        "f12": WIN32_VK_F12,
        "f13": WIN32_VK_F13,
        "f14": WIN32_VK_F14,
        "f15": WIN32_VK_F15,
        "f16": WIN32_VK_F16,
        "f17": WIN32_VK_F17,
        "f18": WIN32_VK_F18,
        "f19": WIN32_VK_F19,
        "f20": WIN32_VK_F20,
        "f21": WIN32_VK_F21,
        "f22": WIN32_VK_F22,
        "f23": WIN32_VK_F23,
        "f24": WIN32_VK_F24,
        "final": WIN32_VK_FINAL,
        "hanja": WIN32_VK_HANJA,
        "help": WIN32_VK_HELP,
        "home": WIN32_VK_HOME,
        "ime_off": WIN32_VK_IME_OFF,
        "ime_on": WIN32_VK_IME_ON,
        "insert": WIN32_VK_INSERT,
        "junja": WIN32_VK_JUNJA,
        "kana": WIN32_VK_KANA,
        "launch_app1": WIN32_VK_LAUNCH_APP1,
        "LAUNCH_APP2": WIN32_VK_LAUNCH_APP2,
        "launch_mail": WIN32_VK_LAUNCH_MAIL,
        "launch_media_select": WIN32_VK_LAUNCH_MEDIA_SELECT,
        "lbutton": WIN32_VK_LBUTTON,
        "lcontrol": WIN32_VK_LCONTROL,
        "left": WIN32_VK_LEFT,
        "lmenu": WIN32_VK_LMENU,
        "lshift": WIN32_VK_LSHIFT,
        "lwin": WIN32_VK_LWIN,
        "mbutton": WIN32_VK_MBUTTON,
        "media_next_track": WIN32_VK_MEDIA_NEXT_TRACK,
        "media_play_pause": WIN32_VK_MEDIA_PLAY_PAUSE,
        "media_prev_track": WIN32_VK_MEDIA_PREV_TRACK,
        "media_stop": WIN32_VK_MEDIA_STOP,
        "modechange": WIN32_VK_MODECHANGE,
        "multiply": WIN32_VK_MULTIPLY,
        "menu": WIN32_VK_Menu,
        "next": WIN32_VK_NEXT,
        "nonconvert": WIN32_VK_NONCONVERT,
        "numlock": WIN32_VK_NUMLOCK,
        "num0": WIN32_VK_NUMPAD0,
        "num1": WIN32_VK_NUMPAD1,
        "num2": WIN32_VK_NUMPAD2,
        "num3": WIN32_VK_NUMPAD3,
        "num4": WIN32_VK_NUMPAD4,
        "num5": WIN32_VK_NUMPAD5,
        "num6": WIN32_VK_NUMPAD6,
        "num7": WIN32_VK_NUMPAD7,
        "num8": WIN32_VK_NUMPAD8,
        "num9": WIN32_VK_NUMPAD9,
        "pause": WIN32_VK_PAUSE,
        "print": WIN32_VK_PRINT,
        "prior": WIN32_VK_PRIOR,
        "rbutton": WIN32_VK_RBUTTON,
        "rcontrol": WIN32_VK_RCONTROL,
        "return": WIN32_VK_RETURN,
        "right": WIN32_VK_RIGHT,
        "rmenu": WIN32_VK_RMENU,
        "rshift": WIN32_VK_RSHIFT,
        "rwin": WIN32_VK_RWIN,
        "scroll": WIN32_VK_SCROLL,
        "select": WIN32_VK_SELECT,
        "separator": WIN32_VK_SEPARATOR,
        "shift": WIN32_VK_SHIFT,
        "sleep": WIN32_VK_SLEEP,
        "snapshot": WIN32_VK_SNAPSHOT,
        "space": WIN32_VK_SPACE,
        "subtract": WIN32_VK_SUBTRACT,
        "tab": WIN32_VK_TAB,
        "up": WIN32_VK_UP,
        "volume_down": WIN32_VK_VOLUME_DOWN,
        "volume_mute": WIN32_VK_VOLUME_MUTE,
        "volume_up": WIN32_VK_VOLUME_UP,
        "vk_xbutton1": WIN32_VK_XBUTTON1,
        "vk_xbutton2": WIN32_VK_XBUTTON2,
        "xbutton1": WIN32_XBUTTON1,
        "xbutton2": WIN32_XBUTTON2,
        "vktovsc": WIN32_VkToVSC,
        "wheel": WIN32_WHEEL,
        "down": WIN32_DOWN,
        "xup": WIN32_XUP,
        "0": WIN32_key0,
        "1": WIN32_key1,
        "2": WIN32_key2,
        "3": WIN32_key3,
        "4": WIN32_key4,
        "5": WIN32_key5,
        "6": WIN32_key6,
        "7": WIN32_key7,
        "8": WIN32_key8,
        "9": WIN32_key9,
        "A": WIN32_keyA,
        "a": WIN32_keyA,
        "B": WIN32_keyB,
        "b": WIN32_keyB,
        "C": WIN32_keyC,
        "c": WIN32_keyC,
        "D": WIN32_keyD,
        "d": WIN32_keyD,
        "E": WIN32_keyE,
        "e": WIN32_keyE,
        "F": WIN32_keyF,
        "f": WIN32_keyF,
        "G": WIN32_keyG,
        "g": WIN32_keyG,
        "H": WIN32_keyH,
        "h": WIN32_keyH,
        "I": WIN32_keyI,
        "i": WIN32_keyI,
        "J": WIN32_keyJ,
        "j": WIN32_keyJ,
        "K": WIN32_keyK,
        "k": WIN32_keyK,
        "L": WIN32_keyL,
        "l": WIN32_keyL,
        "M": WIN32_keyM,
        "m": WIN32_keyM,
        "N": WIN32_keyN,
        "n": WIN32_keyN,
        "O": WIN32_keyO,
        "o": WIN32_keyO,
        "P": WIN32_keyP,
        "p": WIN32_keyP,
        "Q": WIN32_keyQ,
        "q": WIN32_keyQ,
        "R": WIN32_keyR,
        "r": WIN32_keyR,
        "S": WIN32_keyS,
        "s": WIN32_keyS,
        "T": WIN32_keyT,
        "t": WIN32_keyT,
        "U": WIN32_keyU,
        "u": WIN32_keyU,
        "V": WIN32_keyV,
        "v": WIN32_keyV,
        "W": WIN32_keyW,
        "w": WIN32_keyW,
        "X": WIN32_keyX,
        "x": WIN32_keyX,
        "Y": WIN32_keyY,
        "y": WIN32_keyY,
        "Z": WIN32_keyZ,
        "z": WIN32_keyZ,
    }
    mouse_keys_table = {
        "mouse_left": win32_mouse_left,
        "mouse_middle": win32_mouse_middle,
        "mouse_right": win32_mouse_right,
        "mouse_x1": win32_mouse_x1,
        "mouse_x2": win32_mouse_x2
    }
    keyboard = win32_ctype_keyboard_control
    keyboard_check = win32_keypress_check
    mouse = win32_ctype_mouse_control
    screen = win32_screen
    recorder = win32_recorder

    if None in [keyboard_keys_table, mouse_keys_table, keyboard_check, keyboard, mouse, screen, recorder]:
        raise AutoControlException("Can't init auto control")

elif sys.platform in ["darwin"]:
    autocontrol_logger.info("Load MacOS Setting")
    keyboard_keys_table = {
        "a": osx_key_a,
        "A": osx_key_A,
        "b": osx_key_b,
        "B": osx_key_B,
        "c": osx_key_c,
        "C": osx_key_C,
        "d": osx_key_d,
        "D": osx_key_D,
        "e": osx_key_e,
        "E": osx_key_E,
        "f": osx_key_f,
        "F": osx_key_F,
        "g": osx_key_g,
        "G": osx_key_G,
        "h": osx_key_h,
        "H": osx_key_H,
        "i": osx_key_i,
        "I": osx_key_I,
        "j": osx_key_j,
        "J": osx_key_J,
        "k": osx_key_k,
        "K": osx_key_K,
        "l": osx_key_l,
        "L": osx_key_L,
        "m": osx_key_m,
        "M": osx_key_M,
        "n": osx_key_n,
        "N": osx_key_N,
        "o": osx_key_o,
        "O": osx_key_O,
        "p": osx_key_p,
        "P": osx_key_P,
        "q": osx_key_q,
        "Q": osx_key_Q,
        "r": osx_key_r,
        "R": osx_key_R,
        "s": osx_key_s,
        "S": osx_key_S,
        "t": osx_key_t,
        "T": osx_key_T,
        "u": osx_key_u,
        "U": osx_key_U,
        "v": osx_key_v,
        "V": osx_key_V,
        "w": osx_key_w,
        "W": osx_key_W,
        "x": osx_key_x,
        "X": osx_key_X,
        "y": osx_key_y,
        "Y": osx_key_Y,
        "z": osx_key_z,
        "Z": osx_key_Z,
        "1": osx_key_1,
        "!": osx_key_exclam,
        "2": osx_key_2,
        "@": osx_key_at,
        "3": osx_key_3,
        "#": osx_key_numbersign,
        "4": osx_key_4,
        "$": osx_key_money,
        "5": osx_key_5,
        "%": osx_key_percent,
        "6": osx_key_6,
        "^": osx_key_asciicircum,
        "7": osx_key_7,
        "&": osx_key_ampersand,
        "8": osx_key_8,
        "*": osx_key_asterisk,
        "9": osx_key_9,
        "(": osx_key_parenleft,
        "0": osx_key_0,
        ")": osx_key_parenright,
        "=": osx_key_equal,
        "+": osx_key_plus,
        "-": osx_key_minus,
        "_": osx_key_underscore,
        "]": osx_key_bracketright,
        "}": osx_key_braceright,
        "[": osx_key_bracketleft,
        "{": osx_key_braceleft,
        "'": osx_key_apostrophe,
        '"': osx_key_quotedbl,
        ";": osx_key_semicolon,
        ":": osx_key_colon,
        "\\": osx_key_backslash,
        "|": osx_key_bar,
        ",": osx_key_comma,
        "<": osx_key_less,
        "/": osx_key_salsh,
        "?": osx_key_question,
        ".": osx_key_period,
        ">": osx_key_greater,
        "`": osx_key_grave,
        "~": osx_key_asciitilde,
        "space": osx_key_space,
        "return": osx_key_return,
        "newline": osx_key_newline,
        "enter": osx_key_enter,
        "tab": osx_key_tab,
        "backspace": osx_key_backspace,
        "esc": osx_key_esc,
        "command": osx_key_command,
        "shift": osx_key_shift,
        "caps_lock": osx_key_caps_lock,
        "option": osx_key_option,
        "alt": osx_key_alt,
        "ctrl": osx_key_ctrl,
        "shift_right": osx_key_shift_right,
        "option_right": osx_key_option_right,
        "control_right": osx_key_control_right,
        "fn": osx_key_fn,
        "volume_up": osx_key_volume_up,
        "volume_down": osx_key_volume_down,
        "volume_mute": osx_key_volume_mute,
        "f1": osx_key_f1,
        "f2": osx_key_f2,
        "f3": osx_key_f3,
        "f4": osx_key_f4,
        "f5": osx_key_f5,
        "f6": osx_key_f6,
        "f7": osx_key_f7,
        "f8": osx_key_f8,
        "f9": osx_key_f9,
        "f10": osx_key_f10,
        "f11": osx_key_f11,
        "f12": osx_key_f12,
        "f13": osx_key_f13,
        "f14": osx_key_f14,
        "f15": osx_key_f15,
        "f16": osx_key_f16,
        "f17": osx_key_f17,
        "f18": osx_key_f18,
        "f19": osx_key_f19,
        "f20": osx_key_f20,
        "help": osx_key_help,
        "home": osx_key_home,
        "pageup": osx_key_pageup,
        "end": osx_key_end,
        "pagedown": osx_key_pagedown,
        "left": osx_key_left,
        "right": osx_key_right,
        "down": osx_key_down,
        "up": osx_key_up,
        "yen": osx_key_yen,
        "eisu": osx_key_eisu,
        "kana": osx_key_kana,
    }
    mouse_keys_table = {
        "mouse_left": osx_mouse_left,
        "mouse_middle": osx_mouse_middle,
        "mouse_right": osx_mouse_right,
    }
    keyboard = osx_keyboard
    keyboard_check = osx_keyboard_check
    mouse = osx_mouse
    screen = osx_screen
    if None in [keyboard_keys_table, mouse_keys_table, keyboard_check, keyboard, mouse, screen]:
        raise AutoControlException("Can't init auto control")

elif sys.platform in ["linux", "linux2"]:
    autocontrol_logger.info("Load Linux x11 Setting")
    keyboard_keys_table = {
        "backspace": x11_linux_key_backspace,
        "\b": x11_linux_key_slash_b,
        "tab": x11_linux_key_tab,
        "enter": x11_linux_key_enter,
        "return": x11_linux_key_return,
        "shift": x11_linux_key_shift,
        "ctrl": x11_linux_key_ctrl,
        "alt": x11_linux_key_alt,
        "pause": x11_linux_key_pause,
        "capslock": x11_linux_key_capslock,
        "esc": x11_linux_key_esc,
        "pgup": x11_linux_key_pgup,
        "pgdn": x11_linux_key_pgdn,
        "pageup": x11_linux_key_pageup,
        "pagedown": x11_linux_key_pagedown,
        "end": x11_linux_key_end,
        "home": x11_linux_key_home,
        "left": x11_linux_key_left,
        "up": x11_linux_key_up,
        "right": x11_linux_key_right,
        "down": x11_linux_key_down,
        "select": x11_linux_key_select,
        "print": x11_linux_key_print,
        "execute": x11_linux_key_execute,
        "prtsc": x11_linux_key_prtsc,
        "prtscr": x11_linux_key_prtscr,
        "prntscrn": x11_linux_key_prntscrn,
        "insert": x11_linux_key_insert,
        "del": x11_linux_key_del,
        "delete": x11_linux_key_delete,
        "help": x11_linux_key_help,
        "win": x11_linux_key_win,
        "winleft": x11_linux_key_winleft,
        "winright": x11_linux_key_winright,
        "apps": x11_linux_key_apps,
        "num0": x11_linux_key_num0,
        "num1": x11_linux_key_num1,
        "num2": x11_linux_key_num2,
        "num3": x11_linux_key_num3,
        "num4": x11_linux_key_num4,
        "num5": x11_linux_key_num5,
        "num6": x11_linux_key_num6,
        "num7": x11_linux_key_num7,
        "num8": x11_linux_key_num8,
        "num9": x11_linux_key_num9,
        "multiply": x11_linux_key_multiply,
        "add": x11_linux_key_add,
        "separator": x11_linux_key_separator,
        "subtract": x11_linux_key_subtract,
        "decimal": x11_linux_key_decimal,
        "divide": x11_linux_key_divide,
        "f1": x11_linux_key_f1,
        "f2": x11_linux_key_f2,
        "f3": x11_linux_key_f3,
        "f4": x11_linux_key_f4,
        "f5": x11_linux_key_f5,
        "f6": x11_linux_key_f6,
        "f7": x11_linux_key_f7,
        "f8": x11_linux_key_f8,
        "f9": x11_linux_key_f9,
        "f10": x11_linux_key_f10,
        "f11": x11_linux_key_f11,
        "f12": x11_linux_key_f12,
        "f13": x11_linux_key_f13,
        "f14": x11_linux_key_f14,
        "f15": x11_linux_key_f15,
        "f16": x11_linux_key_f16,
        "f17": x11_linux_key_f17,
        "f18": x11_linux_key_f18,
        "f19": x11_linux_key_f19,
        "f20": x11_linux_key_f20,
        "f21": x11_linux_key_f21,
        "f22": x11_linux_key_f22,
        "f23": x11_linux_key_f23,
        "f24": x11_linux_key_f24,
        "numlock": x11_linux_key_numlock,
        "scrolllock": x11_linux_key_scrolllock,
        "shiftleft": x11_linux_key_shiftleft,
        "shiftright": x11_linux_key_shiftright,
        "ctrlleft": x11_linux_key_ctrlleft,
        "ctrlright": x11_linux_key_ctrlright,
        "altleft": x11_linux_key_altleft,
        "altright": x11_linux_key_altright,
        "space": x11_linux_key_space,
        "\n": x11_linux_key_newline_n,
        "\r": x11_linux_key_newline_r,
        "\t": x11_linux_key_newline_t,
        "!": x11_linux_key_exclam,
        "#": x11_linux_key_numbersign,
        "%": x11_linux_key_percent,
        "$": x11_linux_key_dollar,
        "&": x11_linux_key_ampersand,
        '"': x11_linux_key_quotedbl,
        "'": x11_linux_key_apostrophe,
        "(": x11_linux_key_parenleft,
        ")": x11_linux_key_parenright,
        "*": x11_linux_key_asterisk,
        "=": x11_linux_key_equal,
        "+": x11_linux_key_plus,
        ",": x11_linux_key_comma,
        "-": x11_linux_key_minus,
        ".": x11_linux_key_period,
        "/": x11_linux_key_slash,
        ":": x11_linux_key_colon,
        ";": x11_linux_key_semicolon,
        "<": x11_linux_key_less,
        ">": x11_linux_key_greater,
        "?": x11_linux_key_question,
        "@": x11_linux_key_at,
        "[": x11_linux_key_bracketleft,
        "]": x11_linux_key_bracketright,
        "\\": x11_linux_key_backslash,
        "^": x11_linux_key_asciicircum,
        "_": x11_linux_key_underscore,
        "`": x11_linux_key_grave,
        "{": x11_linux_key_braceleft,
        "|": x11_linux_key_bar,
        "}": x11_linux_key_braceright,
        "~": x11_linux_key_asciitilde,
        "a": x11_linux_key_a,
        "b": x11_linux_key_b,
        "c": x11_linux_key_c,
        "d": x11_linux_key_d,
        "e": x11_linux_key_e,
        "f": x11_linux_key_f,
        "g": x11_linux_key_g,
        "h": x11_linux_key_h,
        "i": x11_linux_key_i,
        "j": x11_linux_key_j,
        "k": x11_linux_key_k,
        "l": x11_linux_key_l,
        "m": x11_linux_key_m,
        "n": x11_linux_key_n,
        "o": x11_linux_key_o,
        "p": x11_linux_key_p,
        "q": x11_linux_key_q,
        "r": x11_linux_key_r,
        "s": x11_linux_key_s,
        "t": x11_linux_key_t,
        "u": x11_linux_key_u,
        "v": x11_linux_key_v,
        "w": x11_linux_key_w,
        "x": x11_linux_key_x,
        "y": x11_linux_key_y,
        "z": x11_linux_key_z,
        "A": x11_linux_key_A,
        "B": x11_linux_key_B,
        "C": x11_linux_key_C,
        "D": x11_linux_key_D,
        "E": x11_linux_key_E,
        "F": x11_linux_key_F,
        "G": x11_linux_key_G,
        "H": x11_linux_key_H,
        "I": x11_linux_key_I,
        "J": x11_linux_key_J,
        "K": x11_linux_key_K,
        "L": x11_linux_key_L,
        "M": x11_linux_key_M,
        "N": x11_linux_key_N,
        "O": x11_linux_key_O,
        "P": x11_linux_key_P,
        "Q": x11_linux_key_Q,
        "R": x11_linux_key_R,
        "S": x11_linux_key_S,
        "T": x11_linux_key_T,
        "U": x11_linux_key_U,
        "V": x11_linux_key_V,
        "W": x11_linux_key_W,
        "X": x11_linux_key_X,
        "Y": x11_linux_key_Y,
        "Z": x11_linux_key_Z,
        "1": x11_linux_key_1,
        "2": x11_linux_key_2,
        "3": x11_linux_key_3,
        "4": x11_linux_key_4,
        "5": x11_linux_key_5,
        "6": x11_linux_key_6,
        "7": x11_linux_key_7,
        "8": x11_linux_key_8,
        "9": x11_linux_key_9,
        "0": x11_linux_key_0,
    }
    mouse_keys_table = {
        "mouse_left": x11_linux_mouse_left,
        "mouse_middle": x11_linux_mouse_middle,
        "mouse_right": x11_linux_mouse_right
    }
    special_mouse_keys_table = {
        "scroll_up": x11_linux_scroll_direction_up,
        "scroll_down": x11_linux_scroll_direction_down,
        "scroll_left": x11_linux_scroll_direction_left,
        "scroll_right": x11_linux_scroll_direction_right
    }
    keyboard = x11_linux_keyboard_control
    keyboard_check = x11_linux_listener
    mouse = x11_linux_mouse_control
    screen = x11_linux_screen
    recorder = x11_linux_recoder
    if None in [keyboard_keys_table, mouse_keys_table, special_mouse_keys_table, keyboard, mouse, screen, recorder]:
        raise AutoControlException("Can't init auto control")

if None in [keyboard_keys_table, mouse_keys_table, keyboard, mouse, screen]:
    raise AutoControlException("Can't init auto control")
