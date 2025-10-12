from pynput import keyboard
from typing import Callable

class Input:
    def __init__(self) -> None:
        self.held_keys = set()
        
        self.on_press_hooks = set()
        self.on_release_hooks = set()

        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def on_press(self, key: keyboard.Key | keyboard.KeyCode | None):
        self.held_keys.add(key)
        for function in self.on_press_hooks:
            function(key)

    def on_release(self,key):
        self.held_keys.discard(key)
        for function in self.on_release_hooks:
            function(key)

    def hook_to_keypress(self, function: Callable[[keyboard.Key | keyboard.KeyCode | None], None]):
        self.on_press_hooks.add(function)
    def unhook_from_keypress(self, function: Callable[[keyboard.Key | keyboard.KeyCode | None], None]):
        self.on_press_hooks.discard(function)

    def hook_to_keyrelease(self, function: Callable[[keyboard.Key], None]):
        self.on_release_hooks.add(function)
    def unhook_from_keyrelease(self, function: Callable[[keyboard.Key], None]):
        self.on_release_hooks.discard(function)

    def is_char_held(self, key: str) -> bool:
        for held in self.held_keys:
            try:
                if key == held.char:
                    return True
            except AttributeError:
                continue
        
        return False


    def is_key_held(self, key: keyboard.Key | keyboard.KeyCode | None) -> bool:
        return key in self.held_keys