# -*- coding: utf-8 -*-
"""
This is the Windows backend for keyboard events, and is implemented by
invoking the Win32 API through the ctypes module. This is error prone
and can introduce very unpythonic failure modes, such as segfaults and
low level memory leaks. But it is also dependency-free, very performant
well documented on Microsoft's website and scattered examples.

# TODO:
- Keypad numbers still print as numbers even when numlock is off.
- No way to specify if user wants a keypad key or not in `map_char`.
"""
from __future__ import unicode_literals
import re
import atexit
import traceback
from threading import Lock
from collections import defaultdict
import time

from directkeys._keyboard_event import KeyboardEvent, KEY_DOWN, KEY_UP
from ._canonical_names import normalize_name

_altgr_right_alt_scan_code = None
_altgr_right_alt_flags = None

try:
    # Force Python2 to convert to unicode and not to str.
    chr = unichr
except NameError:
    pass

# This part is just declaring Win32 API structures using ctypes. In C
# this would be simply #include "windows.h".

import ctypes
from ctypes import c_short, c_char, c_uint8, c_int32, c_int, c_uint, c_uint32, c_long, Structure, WINFUNCTYPE, POINTER
from ctypes.wintypes import WORD, DWORD, BOOL, HHOOK, MSG, LPWSTR, WCHAR, WPARAM, LPARAM, LONG, HMODULE, LPCWSTR, HINSTANCE, HWND
LPMSG = POINTER(MSG)
ULONG_PTR = POINTER(DWORD)

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
GetModuleHandleW = kernel32.GetModuleHandleW
GetModuleHandleW.restype = HMODULE
GetModuleHandleW.argtypes = [LPCWSTR]

#https://github.com/boppreh/mouse/issues/1
#user32 = ctypes.windll.user32
user32 = ctypes.WinDLL('user32', use_last_error = True)

VK_PACKET = 0xE7

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_KEYUP = 0x02
KEYEVENTF_UNICODE = 0x04

class KBDLLHOOKSTRUCT(Structure):
    _fields_ = [("vk_code", DWORD),
                ("scan_code", DWORD),
                ("flags", DWORD),
                ("time", c_int),
                ("dwExtraInfo", ULONG_PTR)]

# Included for completeness.
class MOUSEINPUT(ctypes.Structure):
    _fields_ = (('dx', LONG),
                ('dy', LONG),
                ('mouseData', DWORD),
                ('dwFlags', DWORD),
                ('time', DWORD),
                ('dwExtraInfo', ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (('wVk', WORD),
                ('wScan', WORD),
                ('dwFlags', DWORD),
                ('time', DWORD),
                ('dwExtraInfo', ULONG_PTR))

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (('uMsg', DWORD),
                ('wParamL', WORD),
                ('wParamH', WORD))

class _INPUTunion(ctypes.Union):
    _fields_ = (('mi', MOUSEINPUT),
                ('ki', KEYBDINPUT),
                ('hi', HARDWAREINPUT))

class INPUT(ctypes.Structure):
    _fields_ = (('type', DWORD),
                ('union', _INPUTunion))

LowLevelKeyboardProc = WINFUNCTYPE(c_int, WPARAM, LPARAM, POINTER(KBDLLHOOKSTRUCT))

SetWindowsHookEx = user32.SetWindowsHookExW
SetWindowsHookEx.argtypes = [c_int, LowLevelKeyboardProc, HINSTANCE , DWORD]
SetWindowsHookEx.restype = HHOOK

CallNextHookEx = user32.CallNextHookEx
#CallNextHookEx.argtypes = [c_int , c_int, c_int, POINTER(KBDLLHOOKSTRUCT)]
CallNextHookEx.restype = c_int

UnhookWindowsHookEx = user32.UnhookWindowsHookEx
UnhookWindowsHookEx.argtypes = [HHOOK]
UnhookWindowsHookEx.restype = BOOL

GetMessage = user32.GetMessageW
GetMessage.argtypes = [LPMSG, HWND, c_uint, c_uint]
GetMessage.restype = BOOL

TranslateMessage = user32.TranslateMessage
TranslateMessage.argtypes = [LPMSG]
TranslateMessage.restype = BOOL

DispatchMessage = user32.DispatchMessageA
DispatchMessage.argtypes = [LPMSG]


keyboard_state_type = c_uint8 * 256

GetKeyboardState = user32.GetKeyboardState
GetKeyboardState.argtypes = [keyboard_state_type]
GetKeyboardState.restype = BOOL

GetAsyncKeyState = user32.GetAsyncKeyState
GetAsyncKeyState.argtypes = [c_int]
GetAsyncKeyState.restype = c_short

GetKeyNameText = user32.GetKeyNameTextW
GetKeyNameText.argtypes = [c_long, LPWSTR, c_int]
GetKeyNameText.restype = c_int

MapVirtualKey = user32.MapVirtualKeyW
MapVirtualKey.argtypes = [c_uint, c_uint]
MapVirtualKey.restype = c_uint

ToUnicode = user32.ToUnicode
ToUnicode.argtypes = [c_uint, c_uint, keyboard_state_type, LPWSTR, c_int, c_uint]
ToUnicode.restype = c_int

SendInput = user32.SendInput
SendInput.argtypes = [c_uint, POINTER(INPUT), c_int]
SendInput.restype = c_uint

# https://msdn.microsoft.com/en-us/library/windows/desktop/ms646307(v=vs.85).aspx
MAPVK_VK_TO_CHAR = 2
MAPVK_VK_TO_VSC = 0
MAPVK_VSC_TO_VK = 1
MAPVK_VK_TO_VSC_EX = 4
MAPVK_VSC_TO_VK_EX = 3 

VkKeyScan = user32.VkKeyScanW
VkKeyScan.argtypes = [WCHAR]
VkKeyScan.restype = c_short

LLKHF_INJECTED = 0x00000010

WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x104 # Used for ALT key
WM_SYSKEYUP = 0x105


# This marks the end of Win32 API declarations. The rest is ours.

keyboard_event_types = {
    WM_KEYDOWN: KEY_DOWN,
    WM_KEYUP: KEY_UP,
    WM_SYSKEYDOWN: KEY_DOWN,
    WM_SYSKEYUP: KEY_UP,
}

# List taken from the official documentation, but stripped of the OEM-specific keys.
# Keys are virtual key codes, values are pairs (name, is_keypad).
official_virtual_keys = {
    0x03: ('control-break processing', False),
    0x08: ('backspace', False),
    0x09: ('tab', False),
    0x0c: ('clear', False),
    0x0d: ('enter', False),
    0x10: ('shift', False),
    0x11: ('ctrl', False),
    0x12: ('alt', False),
    0x13: ('pause', False),
    0x14: ('caps lock', False),
    0x15: ('ime kana mode', False),
    0x15: ('ime hanguel mode', False),
    0x15: ('ime hangul mode', False),
    0x17: ('ime junja mode', False),
    0x18: ('ime final mode', False),
    0x19: ('ime hanja mode', False),
    0x19: ('ime kanji mode', False),
    0x1b: ('esc', False),
    0x1c: ('ime convert', False),
    0x1d: ('ime nonconvert', False),
    0x1e: ('ime accept', False),
    0x1f: ('ime mode change request', False),
    0x20: ('spacebar', False),
    0x21: ('page up', False),
    0x22: ('page down', False),
    0x23: ('end', False),
    0x24: ('home', False),
    0x25: ('left', False),
    0x26: ('up', False),
    0x27: ('right', False),
    0x28: ('down', False),
    0x29: ('select', False),
    0x2a: ('print', False),
    0x2b: ('execute', False),
    0x2c: ('print screen', False),
    0x2d: ('insert', False),
    0x2e: ('delete', False),
    0x2f: ('help', False),
    0x30: ('0', False),
    0x31: ('1', False),
    0x32: ('2', False),
    0x33: ('3', False),
    0x34: ('4', False),
    0x35: ('5', False),
    0x36: ('6', False),
    0x37: ('7', False),
    0x38: ('8', False),
    0x39: ('9', False),
    0x41: ('a', False),
    0x42: ('b', False),
    0x43: ('c', False),
    0x44: ('d', False),
    0x45: ('e', False),
    0x46: ('f', False),
    0x47: ('g', False),
    0x48: ('h', False),
    0x49: ('i', False),
    0x4a: ('j', False),
    0x4b: ('k', False),
    0x4c: ('l', False),
    0x4d: ('m', False),
    0x4e: ('n', False),
    0x4f: ('o', False),
    0x50: ('p', False),
    0x51: ('q', False),
    0x52: ('r', False),
    0x53: ('s', False),
    0x54: ('t', False),
    0x55: ('u', False),
    0x56: ('v', False),
    0x57: ('w', False),
    0x58: ('x', False),
    0x59: ('y', False),
    0x5a: ('z', False),
    0x5b: ('left windows', False),
    0x5c: ('right windows', False),
    0x5d: ('applications', False),
    0x5f: ('sleep', False),
    0x60: ('0', True),
    0x61: ('1', True),
    0x62: ('2', True),
    0x63: ('3', True),
    0x64: ('4', True),
    0x65: ('5', True),
    0x66: ('6', True),
    0x67: ('7', True),
    0x68: ('8', True),
    0x69: ('9', True),
    0x6a: ('*', True),
    0x6b: ('+', True),
    0x6c: ('separator', True),
    0x6d: ('-', True),
    0x6e: ('decimal', True),
    0x6f: ('/', True),
    0x70: ('f1', False),
    0x71: ('f2', False),
    0x72: ('f3', False),
    0x73: ('f4', False),
    0x74: ('f5', False),
    0x75: ('f6', False),
    0x76: ('f7', False),
    0x77: ('f8', False),
    0x78: ('f9', False),
    0x79: ('f10', False),
    0x7a: ('f11', False),
    0x7b: ('f12', False),
    0x7c: ('f13', False),
    0x7d: ('f14', False),
    0x7e: ('f15', False),
    0x7f: ('f16', False),
    0x80: ('f17', False),
    0x81: ('f18', False),
    0x82: ('f19', False),
    0x83: ('f20', False),
    0x84: ('f21', False),
    0x85: ('f22', False),
    0x86: ('f23', False),
    0x87: ('f24', False),
    0x90: ('num lock', False),
    0x91: ('scroll lock', False),
    0xa0: ('left shift', False),
    0xa1: ('right shift', False),
    0xa2: ('left ctrl', False),
    0xa3: ('right ctrl', False),
    0xa4: ('left menu', False),
    0xa5: ('right menu', False),
    0xa6: ('browser back', False),
    0xa7: ('browser forward', False),
    0xa8: ('browser refresh', False),
    0xa9: ('browser stop', False),
    0xaa: ('browser search key', False),
    0xab: ('browser favorites', False),
    0xac: ('browser start and home', False),
    0xad: ('volume mute', False),
    0xae: ('volume down', False),
    0xaf: ('volume up', False),
    0xb0: ('next track', False),
    0xb1: ('previous track', False),
    0xb2: ('stop media', False),
    0xb3: ('play/pause media', False),
    0xb4: ('start mail', False),
    0xb5: ('select media', False),
    0xb6: ('start application 1', False),
    0xb7: ('start application 2', False),
    0xbb: ('+', False),
    0xbc: (',', False),
    0xbd: ('-', False),
    0xbe: ('.', False),
    #0xbe:('/', False), # Used for miscellaneous characters; it can vary by directkeys. For the US standard keyboard, the '/?.
    0xe5: ('ime process', False),
    0xf6: ('attn', False),
    0xf7: ('crsel', False),
    0xf8: ('exsel', False),
    0xf9: ('erase eof', False),
    0xfa: ('play', False),
    0xfb: ('zoom', False),
    0xfc: ('reserved ', False),
    0xfd: ('pa1', False),
    0xfe: ('clear', False),
}

tables_lock = Lock()
to_name = defaultdict(list)
from_name = defaultdict(list)
scan_code_to_vk = {}

distinct_modifiers = [
    (),
    ('shift',),
    ('alt gr',),
    ('num lock',),
    ('shift', 'num lock'),
    ('caps lock',),
    ('shift', 'caps lock'),
    ('alt gr', 'num lock'),
]

name_buffer = ctypes.create_unicode_buffer(32)
unicode_buffer = ctypes.create_unicode_buffer(32)
keyboard_state = keyboard_state_type()
def get_event_names(scan_code, vk, is_extended, modifiers):
    is_keypad = (scan_code, vk, is_extended) in keypad_keys
    is_official = vk in official_virtual_keys
    if is_keypad and is_official:
        yield official_virtual_keys[vk][0]

    keyboard_state[0x10] = 0x80 * ('shift' in modifiers)
    keyboard_state[0x11] = 0x80 * ('alt gr' in modifiers)
    keyboard_state[0x12] = 0x80 * ('alt gr' in modifiers)
    keyboard_state[0x14] = 0x01 * ('caps lock' in modifiers)
    keyboard_state[0x90] = 0x01 * ('num lock' in modifiers)
    keyboard_state[0x91] = 0x01 * ('scroll lock' in modifiers)
    unicode_ret = ToUnicode(vk, scan_code, keyboard_state, unicode_buffer, len(unicode_buffer), 0)
    if unicode_ret and unicode_buffer.value:
        yield unicode_buffer.value
        # unicode_ret == -1 -> is dead key
        # ToUnicode has the side effect of setting global flags for dead keys.
        # Therefore we need to call it twice to clear those flags.
        # If your 6 and 7 keys are named "^6" and "^7", this is the reason.
        ToUnicode(vk, scan_code, keyboard_state, unicode_buffer, len(unicode_buffer), 0)

    name_ret = GetKeyNameText(scan_code << 16 | is_extended << 24, name_buffer, 1024)
    if name_ret and name_buffer.value:
        yield name_buffer.value

    char = user32.MapVirtualKeyW(vk, MAPVK_VK_TO_CHAR) & 0xFF
    if char != 0:
        yield chr(char)

    if not is_keypad and is_official:
        yield official_virtual_keys[vk][0]

def _setup_name_tables():
    """
    Ensures the scan code/virtual key code/name translation tables are
    filled.
    """
    with tables_lock:
        if to_name: return

        # Go through every possible scan code, and map them to virtual key codes.
        # Then vice-versa.
        all_scan_codes = [(sc, user32.MapVirtualKeyExW(sc, MAPVK_VSC_TO_VK_EX, 0)) for sc in range(0x100)]
        all_vks =        [(user32.MapVirtualKeyExW(vk, MAPVK_VK_TO_VSC_EX, 0), vk) for vk in range(0x100)]
        for scan_code, vk in all_scan_codes + all_vks:
            # `to_name` and `from_name` entries will be a tuple (scan_code, vk, extended, shift_state).
            if (scan_code, vk, 0, 0, 0) in to_name:
                continue

            if scan_code not in scan_code_to_vk:
                scan_code_to_vk[scan_code] = vk

            # Brute force all combinations to find all possible names.
            for extended in [0, 1]:
                for modifiers in distinct_modifiers:
                    entry = (scan_code, vk, extended, modifiers)
                    # Get key names from ToUnicode, GetKeyNameText, MapVirtualKeyW and official virtual keys.
                    names = list(get_event_names(*entry))
                    if names:
                        # Also map lowercased key names, but only after the properly cased ones.
                        lowercase_names = [name.lower() for name in names]
                        to_name[entry] = names + lowercase_names
                        # Remember the "id" of the name, as the first techniques
                        # have better results and therefore priority.
                        for i, name in enumerate(map(normalize_name, names + lowercase_names)):
                            from_name[name].append((i, entry))


        # TODO: single quotes on US INTL is returning the dead key (?), and therefore
        # not typing properly.

        # Alt gr is way outside the usual range of keys (0..127) and on my
        # computer is named as 'ctrl'.
        # Therefore we add it manually and hope
        # Windows is consistent in its inconsistency.
        for extended in [0, 1]:
            for modifiers in distinct_modifiers:
                to_name[(541, 162, extended, modifiers)] = ['alt gr']
                from_name['alt gr'].append((1, (541, 162, extended, modifiers)))

    modifiers_preference = defaultdict(lambda: 10)
    modifiers_preference.update({(): 0, ('shift',): 1, ('alt gr',): 2, ('ctrl',): 3, ('alt',): 4})
    def order_key(line):
        i, entry = line
        scan_code, vk, extended, modifiers = entry
        return modifiers_preference[modifiers], i, extended, vk, scan_code
    for name, entries in list(from_name.items()):
        from_name[name] = sorted(set(entries), key=order_key)

# COLE ESTAS DUAS FUNÇÕES DEPOIS DE _setup_name_tables()

def get_modifiers(altgr_is_pressed):
    """
    Retorna uma tupla com os nomes dos modificadores atualmente ativos.
    """
    return (
        ('shift',) * (user32.GetKeyState(0x10) & 0x8000) +
        ('alt gr',) * altgr_is_pressed +
        ('num lock',) * (user32.GetKeyState(0x90) & 1) +
        ('caps lock',) * (user32.GetKeyState(0x14) & 1) +
        ('scroll lock',) * (user32.GetKeyState(0x91) & 1)
    )

def get_name(scan_code, vk, is_extended, modifiers):
    """
    Obtém o nome mais provável para um evento de tecla, dados os modificadores.
    """
    entry = (scan_code, vk, is_extended, modifiers)
    if entry not in to_name:
        # Popula a tabela se a combinação for nova
        to_name[entry] = list(get_event_names(*entry))

    names = to_name[entry]
    return names[0] if names else None

# O resto do arquivo continua aqui (init = _setup_name_tables, keypad_keys = [...], etc.)

def _remove_alt_gr_mapping():
    """
    Remove ativamente o mapeamento sintético 'alt gr' das tabelas de nomes
    se elas já tiverem sido criadas.
    """
    with tables_lock:
        if 'alt gr' in from_name:
            # Remove a entrada da tabela de tradução de nome para código
            del from_name['alt gr']
            
            # Encontra e remove todas as entradas da tabela de tradução de código para nome
            # que correspondem ao 'alt gr' sintético (scan_code=541, vk_code=162).
            keys_to_remove = [
                key for key in to_name 
                if key[0] == 541 and key[1] == 162
            ]
            for key in keys_to_remove:
                del to_name[key]

# Called by keyboard/__init__.py
init = _setup_name_tables

# List created manually.
keypad_keys = [
    # (scan_code, virtual_key_code, is_extended)
    (126, 194, 0),
    (126, 194, 0),
    (28, 13, 1),
    (28, 13, 1),
    (53, 111, 1),
    (53, 111, 1),
    (55, 106, 0),
    (55, 106, 0),
    (69, 144, 1),
    (69, 144, 1),
    (71, 103, 0),
    (71, 36, 0),
    (72, 104, 0),
    (72, 38, 0),
    (73, 105, 0),
    (73, 33, 0),
    (74, 109, 0),
    (74, 109, 0),
    (75, 100, 0),
    (75, 37, 0),
    (76, 101, 0),
    (76, 12, 0),
    (77, 102, 0),
    (77, 39, 0),
    (78, 107, 0),
    (78, 107, 0),
    (79, 35, 0),
    (79, 97, 0),
    (80, 40, 0),
    (80, 98, 0),
    (81, 34, 0),
    (81, 99, 0),
    (82, 45, 0),
    (82, 96, 0),
    (83, 110, 0),
    (83, 46, 0),
]

shift_is_pressed = False
altgr_is_pressed = False
ignore_next_right_alt = False
shift_vks = set([0x10, 0xa0, 0xa1])
def prepare_intercept(callback):
    """
    Registers a Windows low level keyboard hook. The provided callback will
    be invoked for each high-level keyboard event, and is expected to return
    True if the key event should be passed to the next program, or False if
    the event is to be blocked.

    No event is processed until the Windows messages are pumped (see
    start_intercept).
    """
    _setup_name_tables()
    
    def rebuild_name_tables():
        """
        Força a limpeza e reconstrução das tabelas de nomes.
        Chamado pelo __init__.py quando a configuração de abstração muda.
        """
        _clear_name_tables()
        _setup_name_tables()

    # Adicionado 'flags' como parâmetro da função 'process_key'.
    # A função 'process_key' agora irá verificar o switch.
    def process_key(event_type, vk, scan_code, is_extended, flags):
        """
        Callback que processa os eventos, lendo o estado de abstração do módulo principal.
        """
        # Importação local para evitar ciclo e ler o estado atualizado.
        import directkeys
        
        global altgr_is_pressed, shift_is_pressed

        # Se a abstração estiver DESLIGADA, ignora o Ctrl sintético.
        if not directkeys._ABSTRACT_ALT_GR and scan_code == 541:
            return True # Suprime o evento

        # Se a abstração estiver LIGADA, combina os eventos.
        if directkeys._ABSTRACT_ALT_GR:
            global _altgr_right_alt_scan_code, _altgr_right_alt_flags
            if _altgr_right_alt_scan_code is not None and event_type == KEY_DOWN:
                if scan_code == 541: # É o Ctrl sintético
                    altgr_is_pressed = True
                    event = KeyboardEvent('down', _altgr_right_alt_scan_code, name='alt gr', is_keypad=is_extended, flags=_altgr_right_alt_flags)
                    callback(event)
                    _altgr_right_alt_scan_code = None
                    _altgr_right_alt_flags = None
                    return True # Suprime o Ctrl sintético
                else: # Não era, libera o Right Alt que estava pendente.
                    event = KeyboardEvent('down', _altgr_right_alt_scan_code, name='right alt', is_keypad=is_extended, flags=_altgr_right_alt_flags)
                    callback(event)
                    _altgr_right_alt_scan_code = None
                    _altgr_right_alt_flags = None
            
            if vk == 165: # É um Right Alt (VK 165)
                if event_type == KEY_DOWN: # Pressionado, segura e espera o Ctrl.
                    _altgr_right_alt_scan_code = scan_code
                    _altgr_right_alt_flags = flags
                    return True # Suprime o Right Alt temporariamente
                else: # Solto, conclui o evento 'alt gr'.
                    altgr_is_pressed = False
                    event = KeyboardEvent('up', scan_code, name='alt gr', is_keypad=is_extended, flags=flags)
                    callback(event)
                    return True
            
            # Ignora o KeyUp do Ctrl sintético.
            if scan_code == 541 and event_type == KEY_UP:
                return True

        # Lógica Padrão para todas as outras teclas.
        if vk in shift_vks:
            shift_is_pressed = event_type == KEY_DOWN

        modifiers = get_modifiers(altgr_is_pressed)
        
        if not directkeys._ABSTRACT_ALT_GR and vk == 165:
            name = 'alt gr'
        else:
            name = get_name(scan_code, vk, is_extended, modifiers)

        event = KeyboardEvent(event_type=event_type, scan_code=scan_code, name=name, is_keypad=is_extended, flags=flags)
        return callback(event)

    def low_level_keyboard_handler(nCode, wParam, lParam):
        try:
            vk = lParam.contents.vk_code
            fake_alt = (LLKHF_INJECTED | 0x20)
            if vk != VK_PACKET and lParam.contents.flags & fake_alt != fake_alt:
                event_type = KEY_UP if wParam & 0x01 else KEY_DOWN
                
                raw_flags = lParam.contents.flags
                processed_flags = raw_flags & 1 # Isola o bit LLKHF_EXTENDED
                is_extended = processed_flags
                scan_code = lParam.contents.scan_code
                
                should_continue = process_key(event_type, vk, scan_code, is_extended, processed_flags)

                if not should_continue:
                    return -1
        except Exception as e:
            print('Error in keyboard hook:')
            traceback.print_exc()

        return CallNextHookEx(None, nCode, wParam, lParam)

    WH_KEYBOARD_LL = c_int(13)
    keyboard_callback = LowLevelKeyboardProc(low_level_keyboard_handler)
    handle =  GetModuleHandleW(None)
    thread_id = DWORD(0)
    keyboard_hook = SetWindowsHookEx(WH_KEYBOARD_LL, keyboard_callback, handle, thread_id)

    # Register to remove the hook when the interpreter exits. Unfortunately a
    # try/finally block doesn't seem to work here.
    atexit.register(UnhookWindowsHookEx, keyboard_callback)

def _clear_name_tables():
    """ Limpa as tabelas de nomes para que possam ser reconstruídas. """
    with tables_lock:
        to_name.clear()
        from_name.clear()
        scan_code_to_vk.clear()

def listen(callback):
    prepare_intercept(callback)
    msg = LPMSG()
    while not GetMessage(msg, 0, 0, 0):
        TranslateMessage(msg)
        DispatchMessage(msg)

def map_name(name):
    _setup_name_tables()

    entries = from_name.get(name)
    if not entries:
        raise ValueError('Key name {} is not mapped to any known key.'.format(repr(name)))
    for i, entry in entries:
        scan_code, vk, is_extended, modifiers = entry
        yield scan_code or -vk, modifiers

def _send_event(code, event_type):
    if code == 541:
        # Alt-gr is made of ctrl+alt. Just sending even 541 doesn't do anything.
        user32.keybd_event(0x11, code, event_type, 0)
        user32.keybd_event(0x12, code, event_type, 0)
    elif code > 0:
        vk = scan_code_to_vk.get(code, 0)
        user32.keybd_event(vk, code, event_type, 0)
    else:
        # Negative scan code is a way to indicate we don't have a scan code,
        # and the value actually contains the Virtual key code.
        user32.keybd_event(-code, 0, event_type, 0)

def press(code):
    _send_event(code, 0)

def release(code):
    _send_event(code, 2)

def type_unicode(character):
    # This code and related structures are based on
    # http://stackoverflow.com/a/11910555/252218
    surrogates = bytearray(character.encode('utf-16le'))
    presses = []
    releases = []
    for i in range(0, len(surrogates), 2):
        higher, lower = surrogates[i:i+2]
        structure = KEYBDINPUT(0, (lower << 8) + higher, KEYEVENTF_UNICODE, 0, None)
        presses.append(INPUT(INPUT_KEYBOARD, _INPUTunion(ki=structure)))
        structure = KEYBDINPUT(0, (lower << 8) + higher, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0, None)
        releases.append(INPUT(INPUT_KEYBOARD, _INPUTunion(ki=structure)))
    inputs = presses + releases
    nInputs = len(inputs)
    LPINPUT = INPUT * nInputs
    pInputs = LPINPUT(*inputs)
    cbSize = c_int(ctypes.sizeof(INPUT))
    SendInput(nInputs, pInputs, cbSize)

if __name__ == '__main__':
    _setup_name_tables()
    import pprint
    pprint.pprint(to_name)
    pprint.pprint(from_name)
    #listen(lambda e: print(e.to_json()) or True)

def force_reset_keyboard():
    """
    Força o sistema operacional (Windows) a liberar quaisquer teclas modificadoras
    que possam ter ficado "presas".

    Para cada tecla detectada como presa, simula 5 cliques (pressionar e soltar)
    rapidamente para garantir que o sistema operacional atualize seu estado.
    """
    # Lista de virtual key codes para as principais teclas modificadoras
    vk_codes = [
        0x10, 0xA0, 0xA1,  # Shift, Left Shift, Right Shift
        0x11, 0xA2, 0xA3,  # Ctrl, Left Ctrl, Right Ctrl
        0x12, 0xA4, 0xA5,  # Alt, Left Alt, Right Alt (AltGr)
        0x5B, 0x5C        # Left Windows, Right Windows
    ]
    
    for vk in vk_codes:
        # Verifica se a tecla está "presa" (bit mais significativo está 1)
        if user32.GetKeyState(vk) & 0x8000:
            for _ in range(5):
                # Envia um evento de KEY DOWN (pressionar)
                user32.keybd_event(vk, 0, 0, 0)
                # Envia um evento de KEY UP (soltar)
                user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
                # Pequena pausa para o SO processar
                time.sleep(0.01)

# Esta função você já deve ter no final do arquivo, mantenha-a.
def _reset_internal_state():
    """
    Limpa as variáveis de estado internas da biblioteca usadas para o tratamento
    do AltGr, garantindo um estado limpo entre execuções ou testes.
    """
    global _altgr_right_alt_scan_code, _altgr_right_alt_flags, altgr_is_pressed, ignore_next_right_alt
    _altgr_right_alt_scan_code = None
    _altgr_right_alt_flags = None
    altgr_is_pressed = False
    ignore_next_right_alt = False

def get_stuck_keys():
    """
    Verifica o estado físico de todas as teclas modificadoras principais usando
    GetAsyncKeyState e retorna uma lista com os nomes daquelas que estão presas.
    """
    stuck_keys = []
    vk_codes_with_names = {
        0x10: 'shift', 0xA0: 'left shift', 0xA1: 'right shift',
        0x11: 'ctrl', 0xA2: 'left ctrl', 0xA3: 'right ctrl',
        0x12: 'alt', 0xA4: 'left alt', 0xA5: 'right alt',
        0x5B: 'left windows', 0x5C: 'right windows'
    }
    
    for vk, name in vk_codes_with_names.items():
        # A verificação de bit mais significativo (0x8000) funciona para ambas as funções.
        # A diferença é que GetAsyncKeyState verifica o estado físico atual.
        if GetAsyncKeyState(vk) & 0x8000:
            stuck_keys.append(name)
            
    return stuck_keys
