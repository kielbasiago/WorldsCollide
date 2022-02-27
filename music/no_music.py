from memory.space import Reserve
import instruction.asm as asm

class NoMusic:
    def __init__(self, rom, args):
        self.rom = rom
        self.args = args

        if args.no_music:
            self.mod()

    def mod(self):
        # various sound effects in the game, (wind, phantom train noises, etc.)
        excludeTracks = [
            0x0,
            0x1e,
            0x25,
            0x38,
            0x39,
            0x3a,
            0x3c,
            0x3f,
            0x40,
            0x48,
            0x49,
            0x4A,
        ]


        start_addr = 0x85CA0

        for _ in [x for x in range(0x00, 0x54) if x not in excludeTracks]:
            bytes = self.rom.get_bytes_endian_swap(start_addr, 2)
            length_of_song = (bytes[0] << 8) + bytes[1]
            print("next song:", hex(start_addr))
            space = Reserve(start_addr + 2, start_addr + 2 + length_of_song, "Replace song with rests")
            space.write([0xb6 for x in range(0, length_of_song)])
            start_addr += 2 + length_of_song