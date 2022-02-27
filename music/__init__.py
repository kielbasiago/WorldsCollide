from music.no_music import NoMusic

from memory.space import Reserve
import instruction.asm as asm

__all__ = ["Music"]
class Music:
    def __init__(self, rom, args):
        self.no_music = NoMusic(rom, args)
