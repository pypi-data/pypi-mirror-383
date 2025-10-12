**This project is currently unmaintained. It works for many cases, and I wish to pick it up again in the future, but you might encounter some friction and limited features using it.**

---

---

directkeys
========

Take full control of your keyboard with this small Python library. Hook global events, register hotkeys, simulate key presses and much more.

## Features

- **Global event hook** on all keyboards (captures keys regardless of focus).
- **Listen** and **send** keyboard events.
- Works with **Windows** and **Linux** (requires sudo), with experimental **OS X** support (thanks @glitchassassin!).
- **Pure Python**, no C modules to be compiled.
- **Zero dependencies**. Trivial to install and deploy, just copy the files.
- **Python 2 and 3**.
- Complex hotkey support (e.g. `ctrl+shift+m, ctrl+space`) with controllable timeout.
- Includes **high level API** (e.g. [record](#directkeys.record) and [play](#directkeys.play), [add_abbreviation](#directkeys.add_abbreviation)).
- Maps keys as they actually are in your layout, with **full internationalization support** (e.g. `Ctrl+ç`).
- Events automatically captured in separate thread, doesn't block main program.
- Tested and documented.
- Doesn't break accented dead keys (I'm looking at you, pyHook).
- Mouse support available via project [mouse](https://github.com/boppreh/mouse) (`pip install mouse`).

## Usage

Install the [PyPI package](https://pypi.python.org/pypi/keyboard/):

    pip install directkeys

or clone the repository (no installation required, source files are sufficient):

    git clone https://github.com/WigoWigo10/directkeys

or [download and extract the zip](https://github.com/boppreh/keyboard/archive/master.zip) into your project folder.

Then check the [API docs below](https://github.com/boppreh/keyboard#api) to see what features are available.


## Example

Use as library:

```py
import directkeys

directkeys.press_and_release('shift+s, space')

directkeys.write('The quick brown fox jumps over the lazy dog.')

directkeys.add_hotkey('ctrl+shift+a', print, args=('triggered', 'hotkey'))

# Press PAGE UP then PAGE DOWN to type "foobar".
directkeys.add_hotkey('page up, page down', lambda: directkeys.write('foobar'))

# Blocks until you press esc.
directkeys.wait('esc')

# Record events until 'esc' is pressed.
recorded = directkeys.record(until='esc')
# Then replay back at three times the speed.
directkeys.play(recorded, speed_factor=3)

# Type @@ then press space to replace with abbreviation.
directkeys.add_abbreviation('@@', 'my.long.email@example.com')

# Block forever, like `while True`.
directkeys.wait()
```

Use as standalone module:

```bash
# Save JSON events to a file until interrupted:
python -m keyboard > events.txt

cat events.txt
# {"event_type": "down", "scan_code": 25, "name": "p", "time": 1622447562.2994788, "is_keypad": false}
# {"event_type": "up", "scan_code": 25, "name": "p", "time": 1622447562.431007, "is_keypad": false}
# ...

# Replay events
python -m keyboard < events.txt
```

## Known limitations:

- Events generated under Windows don't report device id (`event.device == None`). [#21](https://github.com/boppreh/keyboard/issues/21)
- Media keys on Linux may appear nameless (scan-code only) or not at all. [#20](https://github.com/boppreh/keyboard/issues/20)
- Key suppression/blocking only available on Windows. [#22](https://github.com/boppreh/keyboard/issues/22)
- To avoid depending on X, the Linux parts reads raw device files (`/dev/input/input*`) but this requires root.
- Other applications, such as some games, may register hooks that swallow all key events. In this case `keyboard` will be unable to report events.
- This program makes no attempt to hide itself, so don't use it for keyloggers or online gaming bots. Be responsible.
- SSH connections forward only the text typed, not keyboard events. Therefore if you connect to a server or Raspberry PI that is running `keyboard` via SSH, the server will not detect your key events.

## Common patterns and mistakes

### Preventing the program from closing

```py
import directkeys
directkeys.add_hotkey('space', lambda: print('space was pressed!'))
# If the program finishes, the hotkey is not in effect anymore.

# Don't do this! This will use 100% of your CPU.
#while True: pass

# Use this instead
directkeys.wait()

# or this
import time
while True:
    time.sleep(1000000)
```

### Waiting for a key press one time

```py
import directkeys

# Don't do this! This will use 100% of your CPU until you press the key.
#
#while not directkeys.is_pressed('space'):
#    continue
#print('space was pressed, continuing...')

# Do this instead
directkeys.wait('space')
print('space was pressed, continuing...')
```

### Repeatedly waiting for a key press

```py
import directkeys

# Don't do this!
#
#while True:
#    if directkeys.is_pressed('space'):
#        print('space was pressed!')
#
# This will use 100% of your CPU and print the message many times.

# Do this instead
while True:
    directkeys.wait('space')
    print('space was pressed! Waiting on it again...')

# or this
directkeys.add_hotkey('space', lambda: print('space was pressed!'))
directkeys.wait()
```

### Invoking code when an event happens

```py
import directkeys

# Don't do this! This will call `print('space')` immediately then fail when the key is actually pressed.
#directkeys.add_hotkey('space', print('space was pressed'))

# Do this instead
directkeys.add_hotkey('space', lambda: print('space was pressed'))

# or this
def on_space():
    print('space was pressed')
directkeys.add_hotkey('space', on_space)

# or this
while True:
    # Wait for the next event.
    event = directkeys.read_event()
    if event.event_type == directkeys.KEY_DOWN and event.name == 'space':
        print('space was pressed')
```

### 'Press any key to continue'

```py
# Don't do this! The `keyboard` module is meant for global events, even when your program is not in focus.
#import directkeys
#print('Press any key to continue...')
#directkeys.get_event()

# Do this instead
input('Press enter to continue...')

# Or one of the suggestions from here
# https://stackoverflow.com/questions/983354/how-to-make-a-script-wait-for-a-pressed-key
```



# API
#### Table of Contents

- [directkeys.**KEY\_DOWN**](#directkeys.KEY_DOWN)
- [directkeys.**KEY\_UP**](#directkeys.KEY_UP)
- [directkeys.**KeyboardEvent**](#directkeys.KeyboardEvent)
- [directkeys.**all\_modifiers**](#directkeys.all_modifiers)
- [directkeys.**sided\_modifiers**](#directkeys.sided_modifiers)
- [directkeys.**version**](#directkeys.version)
- [directkeys.**is\_modifier**](#directkeys.is_modifier)
- [directkeys.**key\_to\_scan\_codes**](#directkeys.key_to_scan_codes)
- [directkeys.**parse\_hotkey**](#directkeys.parse_hotkey)
- [directkeys.**send**](#directkeys.send) *(aliases: `press_and_release`)*
- [directkeys.**press**](#directkeys.press)
- [directkeys.**release**](#directkeys.release)
- [directkeys.**is\_pressed**](#directkeys.is_pressed)
- [directkeys.**call\_later**](#directkeys.call_later)
- [directkeys.**hook**](#directkeys.hook)
- [directkeys.**on\_press**](#directkeys.on_press)
- [directkeys.**on\_release**](#directkeys.on_release)
- [directkeys.**hook\_key**](#directkeys.hook_key)
- [directkeys.**on\_press\_key**](#directkeys.on_press_key)
- [directkeys.**on\_release\_key**](#directkeys.on_release_key)
- [directkeys.**unhook**](#directkeys.unhook) *(aliases: `unblock_key`, `unhook_key`, `unremap_key`)*
- [directkeys.**unhook\_all**](#directkeys.unhook_all)
- [directkeys.**block\_key**](#directkeys.block_key)
- [directkeys.**remap\_key**](#directkeys.remap_key)
- [directkeys.**parse\_hotkey\_combinations**](#directkeys.parse_hotkey_combinations)
- [directkeys.**add\_hotkey**](#directkeys.add_hotkey) *(aliases: `register_hotkey`)*
- [directkeys.**remove\_hotkey**](#directkeys.remove_hotkey) *(aliases: `clear_hotkey`, `unregister_hotkey`, `unremap_hotkey`)*
- [directkeys.**unhook\_all\_hotkeys**](#directkeys.unhook_all_hotkeys) *(aliases: `clear_all_hotkeys`, `remove_all_hotkeys`, `unregister_all_hotkeys`)*
- [directkeys.**remap\_hotkey**](#directkeys.remap_hotkey)
- [directkeys.**stash\_state**](#directkeys.stash_state)
- [directkeys.**restore\_state**](#directkeys.restore_state)
- [directkeys.**restore\_modifiers**](#directkeys.restore_modifiers)
- [directkeys.**write**](#directkeys.write)
- [directkeys.**wait**](#directkeys.wait)
- [directkeys.**get\_hotkey\_name**](#directkeys.get_hotkey_name)
- [directkeys.**read\_event**](#directkeys.read_event)
- [directkeys.**read\_key**](#directkeys.read_key)
- [directkeys.**read\_hotkey**](#directkeys.read_hotkey)
- [directkeys.**get\_typed\_strings**](#directkeys.get_typed_strings)
- [directkeys.**start\_recording**](#directkeys.start_recording)
- [directkeys.**stop\_recording**](#directkeys.stop_recording)
- [directkeys.**record**](#directkeys.record)
- [directkeys.**play**](#directkeys.play) *(aliases: `replay`)*
- [directkeys.**add\_word\_listener**](#directkeys.add_word_listener) *(aliases: `register_word_listener`)*
- [directkeys.**remove\_word\_listener**](#directkeys.remove_word_listener) *(aliases: `remove_abbreviation`)*
- [directkeys.**add\_abbreviation**](#directkeys.add_abbreviation) *(aliases: `register_abbreviation`)*
- [directkeys.**normalize\_name**](#directkeys.normalize_name)


<a name="directkeys.KEY_DOWN"/>

## directkeys.**KEY\_DOWN**
```py
= 'down'
```

<a name="directkeys.KEY_UP"/>

## directkeys.**KEY\_UP**
```py
= 'up'
```

<a name="directkeys.KeyboardEvent"/>

## class directkeys.**KeyboardEvent**




<a name="KeyboardEvent.device"/>

### KeyboardEvent.**device**


<a name="KeyboardEvent.event_type"/>

### KeyboardEvent.**event\_type**


<a name="KeyboardEvent.is_keypad"/>

### KeyboardEvent.**is\_keypad**


<a name="KeyboardEvent.modifiers"/>

### KeyboardEvent.**modifiers**


<a name="KeyboardEvent.name"/>

### KeyboardEvent.**name**


<a name="KeyboardEvent.scan_code"/>

### KeyboardEvent.**scan\_code**


<a name="KeyboardEvent.time"/>

### KeyboardEvent.**time**


<a name="KeyboardEvent.to_json"/>

### KeyboardEvent.**to\_json**(self, ensure\_ascii=False)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/_keyboard_event.py#L34)






<a name="directkeys.all_modifiers"/>

## directkeys.**all\_modifiers**
```py
= {'alt', 'alt gr', 'ctrl', 'left alt', 'left ctrl', 'left shift', 'left windows', 'right alt', 'right ctrl', 'right shift', 'right windows', 'shift', 'windows'}
```

<a name="directkeys.sided_modifiers"/>

## directkeys.**sided\_modifiers**
```py
= {'alt', 'ctrl', 'shift', 'windows'}
```

<a name="directkeys.version"/>

## directkeys.**version**
```py
= '0.13.5'
```

<a name="directkeys.is_modifier"/>

## directkeys.**is\_modifier**(key)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L242)


Returns True if `key` is a scan code or name of a modifier key.



<a name="directkeys.key_to_scan_codes"/>

## directkeys.**key\_to\_scan\_codes**(key, error\_if\_missing=True)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L405)


Returns a list of scan codes associated with this key (name or scan code).



<a name="directkeys.parse_hotkey"/>

## directkeys.**parse\_hotkey**(hotkey)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L435)


Parses a user-provided hotkey into nested tuples representing the
parsed structure, with the bottom values being lists of scan codes.
Also accepts raw scan codes, which are then wrapped in the required
number of nestings.

Example:

```py

parse_hotkey("alt+shift+a, alt+b, c")
#    Keys:    ^~^ ^~~~^ ^  ^~^ ^  ^
#    Steps:   ^~~~~~~~~~^  ^~~~^  ^

# ((alt_codes, shift_codes, a_codes), (alt_codes, b_codes), (c_codes,))
```



<a name="directkeys.send"/>

## directkeys.**send**(hotkey, do\_press=True, do\_release=True)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L468)


Sends OS events that perform the given *hotkey* hotkey.

- `hotkey` can be either a scan code (e.g. 57 for space), single key
(e.g. 'space') or multi-key, multi-step hotkey (e.g. 'alt+F4, enter').
- `do_press` if true then press events are sent. Defaults to True.
- `do_release` if true then release events are sent. Defaults to True.

```py

send(57)
send('ctrl+alt+del')
send('alt+F4, enter')
send('shift+s')
```

Note: keys are released in the opposite order they were pressed.



<a name="directkeys.press"/>

## directkeys.**press**(hotkey)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L501)

Presses and holds down a hotkey (see [`send`](#directkeys.send)). 


<a name="directkeys.release"/>

## directkeys.**release**(hotkey)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L505)

Releases a hotkey (see [`send`](#directkeys.send)). 


<a name="directkeys.is_pressed"/>

## directkeys.**is\_pressed**(hotkey)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L509)


Returns True if the key is pressed.

```py

is_pressed(57) #-> True
is_pressed('space') #-> True
is_pressed('ctrl+space') #-> True
```



<a name="directkeys.call_later"/>

## directkeys.**call\_later**(fn, args=(), delay=0.001)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L536)


Calls the provided function in a new thread after waiting some time.
Useful for giving the system some time to process an event, without blocking
the current execution flow.



<a name="directkeys.hook"/>

## directkeys.**hook**(callback, suppress=False, on\_remove=&lt;lambda&gt;)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L546)


Installs a global listener on all available keyboards, invoking `callback`
each time a key is pressed or released.

The event passed to the callback is of type `directkeys.KeyboardEvent`,
with the following attributes:

- `name`: an Unicode representation of the character (e.g. "&") or
description (e.g.  "space"). The name is always lower-case.
- `scan_code`: number representing the physical key, e.g. 55.
- `time`: timestamp of the time the event occurred, with as much precision
as given by the OS.

Returns the given callback for easier development.



<a name="directkeys.on_press"/>

## directkeys.**on\_press**(callback, suppress=False)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L577)


Invokes `callback` for every KEY_DOWN event. For details see [`hook`](#directkeys.hook).



<a name="directkeys.on_release"/>

## directkeys.**on\_release**(callback, suppress=False)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L583)


Invokes `callback` for every KEY_UP event. For details see [`hook`](#directkeys.hook).



<a name="directkeys.hook_key"/>

## directkeys.**hook\_key**(key, callback, suppress=False)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L589)


Hooks key up and key down events for a single key. Returns the event handler
created. To remove a hooked key use [`unhook_key(key)`](#directkeys.unhook_key) or
[`unhook_key(handler)`](#directkeys.unhook_key).

Note: this function shares state with hotkeys, so [`clear_all_hotkeys`](#directkeys.clear_all_hotkeys)
affects it as well.



<a name="directkeys.on_press_key"/>

## directkeys.**on\_press\_key**(key, callback, suppress=False)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L613)


Invokes `callback` for KEY_DOWN event related to the given key. For details see [`hook`](#directkeys.hook).



<a name="directkeys.on_release_key"/>

## directkeys.**on\_release\_key**(key, callback, suppress=False)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L619)


Invokes `callback` for KEY_UP event related to the given key. For details see [`hook`](#directkeys.hook).



<a name="directkeys.unhook"/>

## directkeys.**unhook**(remove)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L625)


Removes a previously added hook, either by callback or by the return value
of [`hook`](#directkeys.hook).



<a name="directkeys.unhook_all"/>

## directkeys.**unhook\_all**()

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L633)


Removes all keyboard hooks in use, including hotkeys, abbreviations, word
listeners, [`record`](#directkeys.record)ers and [`wait`](#directkeys.wait)s.



<a name="directkeys.block_key"/>

## directkeys.**block\_key**(key)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L645)


Suppresses all key events of the given key, regardless of modifiers.



<a name="directkeys.remap_key"/>

## directkeys.**remap\_key**(src, dst)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L652)


Whenever the key `src` is pressed or released, regardless of modifiers,
press or release the hotkey `dst` instead.



<a name="directkeys.parse_hotkey_combinations"/>

## directkeys.**parse\_hotkey\_combinations**(hotkey)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L666)


Parses a user-provided hotkey. Differently from [`parse_hotkey`](#directkeys.parse_hotkey),
instead of each step being a list of the different scan codes for each key,
each step is a list of all possible combinations of those scan codes.



<a name="directkeys.add_hotkey"/>

## directkeys.**add\_hotkey**(hotkey, callback, args=(), suppress=False, timeout=1, trigger\_on\_release=False)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L706)


Invokes a callback every time a hotkey is pressed. The hotkey must
be in the format `ctrl+shift+a, s`. This would trigger when the user holds
ctrl, shift and "a" at once, releases, and then presses "s". To represent
literal commas, pluses, and spaces, use their names ('comma', 'plus',
'space').

- `args` is an optional list of arguments to passed to the callback during
each invocation.
- `suppress` defines if successful triggers should block the keys from being
sent to other programs.
- `timeout` is the amount of seconds allowed to pass between key presses.
- `trigger_on_release` if true, the callback is invoked on key release instead
of key press.

The event handler function is returned. To remove a hotkey call
[`remove_hotkey(hotkey)`](#directkeys.remove_hotkey) or [`remove_hotkey(handler)`](#directkeys.remove_hotkey).
before the hotkey state is reset.

Note: hotkeys are activated when the last key is *pressed*, not released.
Note: the callback is executed in a separate thread, asynchronously. For an
example of how to use a callback synchronously, see [`wait`](#directkeys.wait).

Examples:

```py

# Different but equivalent ways to listen for a spacebar key press.
add_hotkey(' ', print, args=['space was pressed'])
add_hotkey('space', print, args=['space was pressed'])
add_hotkey('Space', print, args=['space was pressed'])
# Here 57 represents the keyboard code for spacebar; so you will be
# pressing 'spacebar', not '57' to activate the print function.
add_hotkey(57, print, args=['space was pressed'])

add_hotkey('ctrl+q', quit)
add_hotkey('ctrl+alt+enter, space', some_callback)
```



<a name="directkeys.remove_hotkey"/>

## directkeys.**remove\_hotkey**(hotkey\_or\_callback)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L852)


Removes a previously hooked hotkey. Must be called with the value returned
by [`add_hotkey`](#directkeys.add_hotkey).



<a name="directkeys.unhook_all_hotkeys"/>

## directkeys.**unhook\_all\_hotkeys**()

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L860)


Removes all keyboard hotkeys in use, including abbreviations, word listeners,
[`record`](#directkeys.record)ers and [`wait`](#directkeys.wait)s.



<a name="directkeys.remap_hotkey"/>

## directkeys.**remap\_hotkey**(src, dst, suppress=True, trigger\_on\_release=False)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L871)


Whenever the hotkey `src` is pressed, suppress it and send
`dst` instead.

Example:

```py

remap('alt+w', 'ctrl+up')
```



<a name="directkeys.stash_state"/>

## directkeys.**stash\_state**()

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L891)


Builds a list of all currently pressed scan codes, releases them and returns
the list. Pairs well with [`restore_state`](#directkeys.restore_state) and [`restore_modifiers`](#directkeys.restore_modifiers).



<a name="directkeys.restore_state"/>

## directkeys.**restore\_state**(scan\_codes)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L903)


Given a list of scan_codes ensures these keys, and only these keys, are
pressed. Pairs well with [`stash_state`](#directkeys.stash_state), alternative to [`restore_modifiers`](#directkeys.restore_modifiers).



<a name="directkeys.restore_modifiers"/>

## directkeys.**restore\_modifiers**(scan\_codes)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L920)


Like [`restore_state`](#directkeys.restore_state), but only restores modifier keys.



<a name="directkeys.write"/>

## directkeys.**write**(text, delay=0, restore\_state\_after=True, exact=None)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L926)


Sends artificial keyboard events to the OS, simulating the typing of a given
text. Characters not available on the keyboard are typed as explicit unicode
characters using OS-specific functionality, such as alt+codepoint.

To ensure text integrity, all currently pressed keys are released before
the text is typed, and modifiers are restored afterwards.

- `delay` is the number of seconds to wait between keypresses, defaults to
no delay.
- `restore_state_after` can be used to restore the state of pressed keys
after the text is typed, i.e. presses the keys that were released at the
beginning. Defaults to True.
- `exact` forces typing all characters as explicit unicode (e.g.
alt+codepoint or special events). If None, uses platform-specific suggested
value.



<a name="directkeys.wait"/>

## directkeys.**wait**(hotkey=None, suppress=False, trigger\_on\_release=False)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L981)


Blocks the program execution until the given hotkey is pressed or,
if given no parameters, blocks forever.



<a name="directkeys.get_hotkey_name"/>

## directkeys.**get\_hotkey\_name**(names=None)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L995)


Returns a string representation of hotkey from the given key names, or
the currently pressed keys if not given.  This function:

- normalizes names;
- removes "left" and "right" prefixes;
- replaces the "+" key name with "plus" to avoid ambiguity;
- puts modifier keys first, in a standardized order;
- sort remaining keys;
- finally, joins everything with "+".

Example:

```py

get_hotkey_name(['+', 'left ctrl', 'shift'])
# "ctrl+shift+plus"
```



<a name="directkeys.read_event"/>

## directkeys.**read\_event**(suppress=False)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L1026)


Blocks until a keyboard event happens, then returns that event.



<a name="directkeys.read_key"/>

## directkeys.**read\_key**(suppress=False)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L1037)


Blocks until a keyboard event happens, then returns that event's name or,
if missing, its scan code.



<a name="directkeys.read_hotkey"/>

## directkeys.**read\_hotkey**(suppress=True)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L1045)


Similar to [`read_key()`](#directkeys.read_key), but blocks until the user presses and releases a
hotkey (or single key), then returns a string representing the hotkey
pressed.

Example:

```py

read_hotkey()
# "ctrl+shift+p"
```



<a name="directkeys.get_typed_strings"/>

## directkeys.**get\_typed\_strings**(events, allow\_backspace=True)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L1067)


Given a sequence of events, tries to deduce what strings were typed.
Strings are separated when a non-textual key is pressed (such as tab or
enter). Characters are converted to uppercase according to shift and
capslock status. If `allow_backspace` is True, backspaces remove the last
character typed.

This function is a generator, so you can pass an infinite stream of events
and convert them to strings in real time.

Note this functions is merely an heuristic. Windows for example keeps per-
process keyboard state such as keyboard layout, and this information is not
available for our hooks.

```py

get_type_strings(record()) #-> ['This is what', 'I recorded', '']
```



<a name="directkeys.start_recording"/>

## directkeys.**start\_recording**(recorded\_events\_queue=None)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L1114)


Starts recording all keyboard events into a global variable, or the given
queue if any. Returns the queue of events and the hooked function.

Use [`stop_recording()`](#directkeys.stop_recording) or [`unhook(hooked_function)`](#directkeys.unhook) to stop.



<a name="directkeys.stop_recording"/>

## directkeys.**stop\_recording**()

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L1126)


Stops the global recording of events and returns a list of the events
captured.



<a name="directkeys.record"/>

## directkeys.**record**(until=&#x27;escape&#x27;, suppress=False, trigger\_on\_release=False)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L1138)


Records all keyboard events from all keyboards until the user presses the
given hotkey. Then returns the list of events recorded, of type
`directkeys.KeyboardEvent`. Pairs well with
[`play(events)`](#directkeys.play).

Note: this is a blocking function.
Note: for more details on the keyboard hook and events see [`hook`](#directkeys.hook).



<a name="directkeys.play"/>

## directkeys.**play**(events, speed\_factor=1.0)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L1152)


Plays a sequence of recorded events, maintaining the relative time
intervals. If speed_factor is <= 0 then the actions are replayed as fast
as the OS allows. Pairs well with [`record()`](#directkeys.record).

Note: the current keyboard state is cleared at the beginning and restored at
the end of the function.



<a name="directkeys.add_word_listener"/>

## directkeys.**add\_word\_listener**(word, callback, triggers=[&#x27;space&#x27;], match\_suffix=False, timeout=2)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L1176)


Invokes a callback every time a sequence of characters is typed (e.g. 'pet')
and followed by a trigger key (e.g. space). Modifiers (e.g. alt, ctrl,
shift) are ignored.

- `word` the typed text to be matched. E.g. 'pet'.
- `callback` is an argument-less function to be invoked each time the word
is typed.
- `triggers` is the list of keys that will cause a match to be checked. If
the user presses some key that is not a character (len>1) and not in
triggers, the characters so far will be discarded. By default the trigger
is only `space`.
- `match_suffix` defines if endings of words should also be checked instead
of only whole words. E.g. if true, typing 'carpet'+space will trigger the
listener for 'pet'. Defaults to false, only whole words are checked.
- `timeout` is the maximum number of seconds between typed characters before
the current word is discarded. Defaults to 2 seconds.

Returns the event handler created. To remove a word listener use
[`remove_word_listener(word)`](#directkeys.remove_word_listener) or [`remove_word_listener(handler)`](#directkeys.remove_word_listener).

Note: all actions are performed on key down. Key up events are ignored.
Note: word matches are **case sensitive**.



<a name="directkeys.remove_word_listener"/>

## directkeys.**remove\_word\_listener**(word\_or\_handler)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L1232)


Removes a previously registered word listener. Accepts either the word used
during registration (exact string) or the event handler returned by the
[`add_word_listener`](#directkeys.add_word_listener) or [`add_abbreviation`](#directkeys.add_abbreviation) functions.



<a name="directkeys.add_abbreviation"/>

## directkeys.**add\_abbreviation**(source\_text, replacement\_text, match\_suffix=False, timeout=2)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/__init__.py#L1240)


Registers a hotkey that replaces one typed text with another. For example

```py

add_abbreviation('tm', u'™')
```

Replaces every "tm" followed by a space with a ™ symbol (and no space). The
replacement is done by sending backspace events.

- `match_suffix` defines if endings of words should also be checked instead
of only whole words. E.g. if true, typing 'carpet'+space will trigger the
listener for 'pet'. Defaults to false, only whole words are checked.
- `timeout` is the maximum number of seconds between typed characters before
the current word is discarded. Defaults to 2 seconds.

For more details see [`add_word_listener`](#directkeys.add_word_listener).



<a name="directkeys.normalize_name"/>

## directkeys.**normalize\_name**(name)

[\[source\]](https://github.com/boppreh/keyboard/blob/master/keyboard/_canonical_names.py#L1233)


Given a key name (e.g. "LEFT CONTROL"), clean up the string and convert to
the canonical representation (e.g. "left ctrl") if one is known.



