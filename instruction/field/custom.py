from memory.space import Bank, START_ADDRESS_SNES, Reserve, Write, Read
from instruction.event import EVENT_CODE_START, _Instruction, _Branch
import instruction.asm as asm
import instruction.c0 as c0
from enum import IntEnum

def _set_opcode_address(opcode, address):
    FIRST_OPCODE = 0x35
    opcode_table_address = 0x098c4 + (opcode - FIRST_OPCODE) * 2
    space = Reserve(opcode_table_address, opcode_table_address + 1, f"field opcode table, {opcode} {hex(address)}")
    space.write(
        (address & 0xffff).to_bytes(2, "little"),
    )

def _add_esper_increment():
    import data.event_word as event_word
    src = [
        asm.INC(event_word.address(event_word.ESPERS_FOUND), asm.ABS),
        Read(0xadd4, 0xadd6),   # advance event script
    ]
    space = Write(Bank.C0, src, "add esper command increment espers found event word")
    increment_found = space.start_address

    space = Reserve(0xadd4, 0xadd6, "add esper command jmp to increment event word", asm.NOP())
    space.write(asm.JMP(increment_found, asm.ABS))
_add_esper_increment()

class RemoveDeath(_Instruction):
    def __init__(self, character):
        import instruction.field as field
        from instruction.c0 import character_data_offset

        self.current_status = 0x1614 # character status effects address
        self.death_mask = field.Status.DEATH >> 8
        # add a special command specifically for removing death. 
        # This is used in special events (like Moogle Defense), where we want to revive even with permadeath
        # Code based on C0/AE2D - AE44 (gen. act. 88 to Remove status effects)
        src = [
            asm.JSR(character_data_offset, asm.ABS),
            asm.CPY(0x0250, asm.IMM16),
            asm.BCS("DONE"),
            asm.A16(),
            asm.LDA(self.current_status, asm.ABS_Y),
            asm.AND(~self.death_mask, asm.IMM16), # clear the DEATH bit
            asm.STA(self.current_status, asm.ABS_Y),
            asm.TDC(),
            asm.A8(),
            "DONE",
            asm.LDA(0x02, asm.IMM8),        # command size
            asm.JMP(0x9b5c, asm.ABS),       # next command
        ]
        space = Write(Bank.C0, src, "custom remove_death command")
        address = space.start_address

        opcode = 0x6f
        _set_opcode_address(opcode, address)

        RemoveDeath.__init__ = lambda self, character : super().__init__(opcode, character)
        self.__init__(character)

class SetEquipmentAndCommands(_Instruction):
    def __init__(self, to_character, from_character):
        from instruction.c0 import character_data_offset

        # subset of SetProperties vanilla command (0x40), which only sets equipment, commands, and character ID
        src = [
            #C0/A07C:	20AD9D  	JSR $9DAD		
            asm.JSR(character_data_offset, asm.ABS),
            # C0/A07F:	A916    	LDA #$16
            asm.LDA(0x16, asm.IMM8),
            # C0/A081:	8D0242  	STA $4202
            asm.STA(0x4202, asm.ABS),
            # C0/A084:	A5EC    	LDA $EC
            asm.LDA(0xEC, asm.DIR),
            # C0/A086:	8D0342  	STA $4203
            asm.STA(0x4203, asm.ABS),
            # C0/A089:	EA      	NOP
            asm.NOP(),
            # C0/A08A:	EA      	NOP
            asm.NOP(),
            # C0/A08B:	EA      	NOP
            asm.NOP(),
            # C0/A08C:	AE1642  	LDX $4216
            asm.LDX(0x4216, asm.ABS),
            # Commands
            # C0/A08F:	BFA27CED	LDA $ED7CA2,X	(command 1)
            asm.LDA(0xED7CA2, asm.LNG_X),
            # C0/A093:	991616  	STA $1616,Y
            asm.STA(0x1616, asm.ABS_Y),
            # C0/A096:	BFA37CED	LDA $ED7CA3,X	(command 2)
            asm.LDA(0xED7CA3, asm.LNG_X),
            # C0/A09A:	991716  	STA $1617,Y
            asm.STA(0x1617, asm.ABS_Y),
            # C0/A09D:	BFA47CED	LDA $ED7CA4,X	(command 3)
            asm.LDA(0xED7CA4, asm.LNG_X),
            # C0/A0A1:	991816  	STA $1618,Y
            asm.STA(0x1618, asm.ABS_Y),
            # C0/A0A4:	BFA57CED	LDA $ED7CA5,X	(command 4)
            asm.LDA(0xED7CA5, asm.LNG_X),
            # C0/A0A8:	991916  	STA $1619,Y
            asm.STA(0x1619, asm.ABS_Y),
            # Equipment
            # C0/A0CC:	BFAF7CED	LDA $ED7CAF,X	(R-hand)
            asm.LDA(0xED7CAF, asm.LNG_X),
            # C0/A0D0:	991F16  	STA $161F,Y
            asm.STA(0x161F, asm.ABS_Y),
            # C0/A0D3:	BFB07CED	LDA $ED7CB0,X	(L-hand)
            asm.LDA(0xED7CB0, asm.LNG_X),
            # C0/A0D7:	992016  	STA $1620,Y
            asm.STA(0x1620, asm.ABS_Y),
            # C0/A0DA:	BFB17CED	LDA $ED7CB1,X	(Body)
            asm.LDA(0xED7CB1, asm.LNG_X),
            # C0/A0DE:	992116  	STA $1621,Y
            asm.STA(0x1621, asm.ABS_Y),
            # C0/A0E1:	BFB27CED	LDA $ED7CB2,X	(Head)
            asm.LDA(0xED7CB2, asm.LNG_X),
            # C0/A0E5:	992216  	STA $1622,Y
            asm.STA(0x1622, asm.ABS_Y),
            # C0/A0E8:	BFB37CED	LDA $ED7CB3,X	(Relic 1)
            asm.LDA(0xED7CB3, asm.LNG_X),
            # C0/A0EC:	992316  	STA $1623,Y
            asm.STA(0x1623, asm.ABS_Y),
            # C0/A0EF:	BFB47CED	LDA $ED7CB4,X	(Relic 2)
            asm.LDA(0xED7CB4, asm.LNG_X),
            # C0/A0F3:	992416  	STA $1624,Y
            asm.STA(0x1624, asm.ABS_Y),

            # C0/A10D:	A5EC    	LDA $EC        (load parameter)
            asm.LDA(0xec, asm.DIR),
            # C0/A10F:	990016  	STA $1600,Y    (save character ID)
            asm.STA(0x1600, asm.ABS_Y),

            # C0/A17A:	A903    	LDA #$03
            asm.LDA(0x03, asm.IMM8),        # command size
            # C0/A17C:	4C5C9B  	JMP $9B5C
            asm.JMP(0x9b5c, asm.ABS),       # next command
        ]
        space = Write(Bank.C0, src, "custom swap equipment and commands command")
        address = space.start_address

        opcode = 0xa3
        _set_opcode_address(opcode, address)

        SetEquipmentAndCommands.__init__ = lambda self, to_character, from_character : super().__init__(opcode, to_character, from_character)
        self.__init__(to_character, from_character)

class ToggleWorlds(_Instruction):
    def __init__(self):
        fade_load_map = 0xab47

        src = [
            asm.LDA(0x1f69, asm.ABS),           # a = low 8 bits of parent map
            asm.XOR(1, asm.IMM8),               # toggle last bit of parent map id
            asm.STA(0x1f69, asm.ABS),           # update parent map
            asm.JMP(fade_load_map, asm.ABS),    # jump to original fade load map command
        ]
        space = Write(Bank.C0, src, "custom toggle worlds instruction")
        address = space.start_address

        opcode = 0x6d
        _set_opcode_address(opcode, address)

        # same args as airship lift-off load map
        # special map 0x1ff, return to parent map at same position/direction
        args = [0xff, 0x25, 0x00, 0x00, 0x01]

        ToggleWorlds.__init__ = lambda self : super().__init__(opcode, *args)
        self.__init__()

class LoadEsperFound(_Instruction):
    def __init__(self, esper):
        import data.event_bit as event_bit
        result_byte = event_bit.address(event_bit.multipurpose(0))
        src = [
            asm.LDA(0xeb, asm.DIR),
            asm.JSR(c0.esper_found, asm.ABS),
            asm.STA(result_byte, asm.ABS),
            asm.LDA(0x02, asm.IMM8),        # command size
            asm.JMP(0x9b5c, asm.ABS),       # next command
        ]
        space = Write(Bank.C0, src, "custom load esper found instruction")
        address = space.start_address

        opcode = 0x83
        _set_opcode_address(opcode, address)

        LoadEsperFound.__init__ = lambda self, esper : super().__init__(opcode, esper)
        self.__init__(esper)

class LoadPartiesWithCharacters(_Instruction):
    ''' Sets bits 0-2 in event word when those parties have characters.'''
    def __init__(self):
        import data.event_bit as event_bit
        result_byte = event_bit.address(event_bit.multipurpose(0))
        src = [
            asm.STZ(result_byte, asm.ABS),
            asm.LDX(0x0000, asm.IMM16),
            "START_CHARACTER_LOOP",
            asm.LDA(0x1850, asm.ABS_X), # load the character data 
            asm.AND(0x47, asm.IMM8),    # isolate the enabled bit and party bits (note: there are 3 party bits, but we only use 2.)
            "CHECK_PARTY_1",
            asm.CMP(0x41, asm.IMM8),
            asm.BNE("CHECK_PARTY_2"),
            # character enabled and in party 1
            asm.LDA(result_byte, asm.ABS),
            asm.ORA(0x01, asm.IMM8), # set bit 0 in the result to indicate party 1 has an enabled character
            asm.STA(result_byte, asm.ABS),
            asm.BRA("NEXT_CHARACTER"),
            "CHECK_PARTY_2",
            asm.CMP(0x42, asm.IMM8),
            asm.BNE("CHECK_PARTY_3"),
            # character enabled and in party 2
            asm.LDA(result_byte, asm.ABS),
            asm.ORA(0x02, asm.IMM8), # set bit 1 in the result to indicate party 2 has an enabled character 
            asm.STA(result_byte, asm.ABS),
            asm.BRA("NEXT_CHARACTER"),
            "CHECK_PARTY_3",
            asm.CMP(0x43, asm.IMM8),
            asm.BNE("NEXT_CHARACTER"),
            # character enabled and in party 3
            asm.LDA(result_byte, asm.ABS),
            asm.ORA(0x04, asm.IMM8), # set bit 2 in the result to indicate party 3 has an enabled character
            asm.STA(result_byte, asm.ABS),
            # end of loop iteration -- increment X for another go
            "NEXT_CHARACTER",
            asm.INX(),
            asm.CPX(0x000f, asm.IMM16), # did we check all 16 characters?
            asm.BNE("START_CHARACTER_LOOP"), # if not, check the next one
            asm.LDA(0x01, asm.IMM8),        # command size
            asm.JMP(0x9b5c, asm.ABS),       # next command
        ]

        space = Write(Bank.C0, src, "custom load parties with characters instruction")
        address = space.start_address

        opcode = 0xe5
        _set_opcode_address(opcode, address)

        LoadPartiesWithCharacters.__init__ = lambda self : super().__init__(opcode)
        self.__init__()

class RecruitCharacter(_Instruction):
    def __init__(self, character):
        recruit_character_function = START_ADDRESS_SNES + c0.recruit_character
        src = [
            asm.JSL(recruit_character_function),
            asm.LDA(0x02, asm.IMM8),        # command size
            asm.JMP(0x9b5c, asm.ABS),       # next command
        ]
        space = Write(Bank.C0, src, "custom recruit_character command")
        address = space.start_address

        opcode = 0x76
        _set_opcode_address(opcode, address)

        RecruitCharacter.__init__ = lambda self, character : super().__init__(opcode, character)
        self.__init__(character)

    def __str__(self):
        return super().__str__(self.args[0])

class _InvokeBattleType(_Instruction):
    # invoke battle with given type (front/back/pincer/side) regardless of formation settings
    def __init__(self, pack, battle_type, background):
        self.pack = pack
        self.battle_type = battle_type

        # i did not see anywhere in the event script using the sound flag and only 7 (removed)
        #   scenes using battle animation flag
        # this custom function replaces the battle sound/animation flags with battle type bits
        # front = 0, back = 1, pincer = 2, side = 3
        super().__init__(self.write(), pack - 0x100, background | (battle_type << 6))

    def __str__(self):
        return super().__str__(f"{str(self.pack)}, {str(self.battle_type)}")

    def write(self):
        src = [
            asm.A8(),
            asm.LDA(0xec, asm.DIR),         # a = type bits and background
            asm.AND(0xc0, asm.IMM8),        # a = battle type bits
            asm.ROL(),
            asm.ROL(),
            asm.ROL(),                      # shift type bits to the beginning of the byte
            asm.ORA(0x04, asm.IMM8),        # add 4 to indicate a battle type is given (even if type is zero)
            asm.TAY(),                      # y = battle type (y is unused by battle setup function)
            asm.LDA(0xc0, asm.IMM8),        # a = mask for sound/animation flags
            asm.TRB(0xec, asm.DIR),         # overwrite custom battle type bits with sound/animation true
            asm.JSR(0xa5a7, asm.ABS),       # battle setup (formation, background, music, transition animation)
            asm.TYA(),                      # a = battle type
            asm.STA(0x11e3, asm.ABS),       # store battle type in upper byte of battle background
            asm.JMP(0xa57b, asm.ABS),       # jmp to original invoke battle command code (after setup)
        ]
        space = Write(Bank.C0, src, "custom invoke_battle_type command")
        invoke_battle_type_address = space.start_address

        src = [
            asm.LDA(0x11e3, asm.ABS),       # a = battle type
            asm.CMP(0x00, asm.IMM8),        # compare to zero and set carry flag if a >= 0 (for sbc)
            asm.BEQ("LOAD_BATTLE_TYPE"),    # branch if battle type is zero
            asm.SBC(0x04, asm.IMM8),        # subtract 4 (the flag value i added)
            asm.STA(0x201f, asm.ABS),       # store battle type in correct battle ram location
            asm.LDA(0x00, asm.IMM8),
            asm.STA(0x11e3, asm.ABS),       # set upper byte of battle bg to 0 to prevent possible side-effects
            asm.RTS(),

            "LOAD_BATTLE_TYPE",
            Read(0x22e3a, 0x22e3c),
            asm.JMP(0x2e3d, asm.ABS),       # jmp back to normal battle type loading code
        ]
        space = Write(Bank.C2, src, "custom event instruction battle type check")
        battle_type_check = space.start_address

        space = Reserve(0x22e3a, 0x22e3c, "battle load relic effects 2", asm.NOP())
        space.write(
            asm.JMP(battle_type_check, asm.ABS),    # jmp to custom event instruction battle type check
        )

        opcode = 0x6e
        _set_opcode_address(opcode, invoke_battle_type_address)

        _InvokeBattleType.write = lambda self : opcode
        return self.write()

class BranchChance(_Branch):
    def __init__(self, chance, destination):
        self.chance = chance
        if chance > 255 or chance < 0:
            raise ValueError(f"branch_chance: invalid chance {chance}")
        elif chance <= 1:
            chance = int(chance * 255) # convert from decimal
        super().__init__(self.write(), [chance], destination)

    def __str__(self):
        return super().__str__(f"{self.chance:0.3}")

    def write(self):
        # after rng, jump inside event command 0xbd (50% branch command) to execute the result
        yes_branch = 0xb291
        no_branch = 0xb278

        src = [
            asm.JSR(c0.rng, asm.ABS),       # a = random number 0 to 255
            asm.CMP(0xeb, asm.DIR),         # compare to given chance
            asm.BLT("BRANCH"),              # if random number < chance

            # increment $e5 to account for branch_chance having 1 extra argument than 0xbd
            asm.INC(0xe5, asm.DIR),
            asm.JMP(no_branch, asm.ABS),

            "BRANCH",
            asm.LDX(0xec, asm.DIR),         # x = low bytes of destination
            asm.STX(0xe5, asm.DIR),
            asm.LDA(0xee, asm.DIR),         # a = high byte of destination
            asm.JMP(yes_branch, asm.ABS),
        ]
        space = Write(Bank.C0, src, "custom branch_chance command")
        address = space.start_address

        opcode = 0xa5
        _set_opcode_address(opcode, address)

        BranchChance.write = lambda self : opcode
        return self.write()

class LongCall(_Instruction):
    # call function outside of event code
    # input: 24 bit address of the function to call and an optional argument to call it with

    ARG_ADDRESS = 0xee
    def __init__(self, function_address, arg = 0):
        src = [
            asm.TDC(),
            asm.LDA(0x05, asm.IMM8),        # command size
            asm.JMP(0x9b5c, asm.ABS),       # next command
        ]
        space = Write(Bank.C0, src, "custom long call return")
        return_address = space.start_address

        src = [
            # copy jsl behavior, bank/address will be popped from stack by rtl
            asm.PHK(),                              # push program bank register
            asm.A16(),
            asm.LDA(return_address - 1, asm.IMM16), # -1 because rtl pulls pc from stack and increments it
            asm.PHA(),                              # push address to return to

            # store 24 bit address to call, and jump to it
            asm.LDA(0xeb, asm.DIR),
            asm.STA(0x05f4, asm.ABS),               # 0x05f4 is same address field.Call uses in c0
            asm.A8(),
            asm.LDA(0xed, asm.DIR),
            asm.STA(0x05f6, asm.ABS),

            asm.JMP(0x05f4, asm.ABS_24),
        ]
        space = Write(Bank.C0, src, "custom long call")
        address = space.start_address

        opcode = 0x8f # overwrite learn all swdtech
        _set_opcode_address(opcode, address)

        LongCall.__init__ = (lambda self, function_address, arg = 0 :
                             super().__init__(opcode, function_address.to_bytes(3, "little"), arg))
        self.__init__(function_address, arg)

CHEST_BLOCK_SIZE = 5
class CollectTreasure(_Instruction):
    def __init__(self, map_id, x, y):
        src = [
            "REMOTE_TREASURE",
            asm.A16(),                      # REP #$20
            asm.LDA(0xeb, asm.DIR),         # LDA $EB ; load map
            asm.ASL(),                      # ASL A
            asm.TAX(),                      # TAX
            asm.LDA(0xed82f6, asm.LNG_X),   # LDA $ED82F6,X  ; load the pointer for the *next room*
            asm.STA(0x1e, asm.DIR),         # STA $1E   $1e = next room pointer
            asm.LDA(0xed82f4, asm.LNG_X),   # LDA $ED82F4,X  ; load the pointer for our current room
            asm.TAX(),                      # TAX       x = current room pointer
            asm.TDC(),                      # TDC
            asm.A8(),                       # SEP #$20
            asm.CPX(0x1e, asm.DIR),         # CPX $1E  ; do the two pointers match? if they do, this map has no treasure
            asm.BEQ("TREASURE_WRAPUP1"),     # We chose a map without a treasure chest - branch and exit if so

            "TREASURE_LOOP_AGAIN",          # treasure_loop_again:
            asm.LDA(0xed8634, asm.LNG_X),   # LDA $ED8634,X  ; load X coordinate of chest
            asm.CMP(0xed, asm.DIR),         # CMP $ED  ; does it match?
            asm.BNE("NO_CHEST"),            # BNE no_chest  ; we do have to have some kind of fail-safe in place
            asm.LDA(0xed8635, asm.LNG_X),   # LDA $ED8635,X  ; load Y coordinate of chest
            asm.CMP(0xee, asm.DIR),         # CMP $EE  ; does it match?
            asm.BEQ("TREASURE_FOUND"),      # BEQ treasure_found  ; we have matched X and Y, let's get the contents

            "NO_CHEST",                     # no_chest:
            asm.INX(),                      # INX
            asm.INX(),                      # INX
            asm.INX(),                      # INX
            asm.INX(),                      # INX
            asm.INX(),                      # INX
            asm.CPX(0x1e, asm.DIR),         # CPX $1E
            asm.BNE("TREASURE_LOOP_AGAIN"), # BNE treasure_loop_again
                                            # ; coming in, upper A is already 00
            "TREASURE_WRAPUP1",             # treasure_wrapup1: this is a duplicate as the jump to the other is too far to safely make
            asm.TDC(),                      # TDC
            asm.LDA(0x05, asm.IMM8),        # command size
            asm.JMP(0x9b5c, asm.ABS),       # next command

            "TREASURE_FOUND",               # treasure_found:
            asm.A16(),                      # REP #$20
            asm.LDA(0xed8638, asm.LNG_X),   # LDA $ED8638,X  ; load contents
            asm.STA(0x1a, asm.DIR),         # STA $1A
            asm.LDA(0xed8636, asm.LNG_X),   # LDA $ED8636,X  ; load the byte and bit
            asm.STA(0x1e, asm.DIR),         # STA $1E
            asm.AND(0x0007, asm.IMM16),     # AND #$0007
            asm.TAX(),                      # TAX
            asm.LDA(0x1e, asm.DIR),         # LDA $1E
            asm.AND(0x01f8, asm.IMM16),     # AND #$01F8
            asm.LSR(),                      # LSR A
            asm.LSR(),                      # LSR A
            asm.LSR(),                      # LSR A
            asm.TAY(),                      # TAY
            asm.TDC(),                      # TDC
            asm.A8(),                       # SEP #$20
            asm.LDA(0x1e40, asm.ABS_Y),     # LDA $1E40,Y
            asm.AND(0xc0bafc, asm.LNG_X),   # AND $C0BAFC,X  ; is this bit set?
            asm.BNE("TREASURE_WRAPUP"),     # chest has already been looted  ; branch and exit if so
            asm.LDA(0x1e40, asm.ABS_Y),     # LDA $1E40,Y
            asm.ORA(0xc0bafc, asm.LNG_X),   # ORA $C0BAFC,X  ; set this bit, meaning we have now opened this box
            asm.STA(0x1e40, asm.ABS_Y),     # STA $1E40,Y
            asm.LDA(0x1f, asm.DIR),         # LDA $1F
            asm.BPL("NOT_GIL_TREASURE"),    # BPL not_gil_treasure
            asm.LDA(0x1a, asm.DIR),         # LDA $1A  ; load amount
            asm.STA(0x4202, asm.ABS),       # STA $4202
            asm.LDA(0x64, asm.IMM8),        # LDA #$64
            asm.STA(0x4203, asm.ABS),       # STA $4203  ; multiply it by 100
            asm.NOP(),                      # NOP
            asm.NOP(),                      # NOP
            asm.NOP(),                      # NOP
            asm.NOP(),                      # NOP
            asm.REP(0x21),                  # REP #$21
            asm.LDA(0x4216, asm.ABS),       # LDA $4216  ; load product
            asm.ADC(0x1860, asm.ABS),       # ADC $1860
            asm.STA(0x1860, asm.ABS),       # STA $1860
            asm.TDC(),                      # TDC
            asm.A8(),                       # SEP #$20
            asm.BCC("GIL_NO_WRAP"),         # BCC gil_no_wrap  ; branch if result didn't wrap. meaning whatever we picked up didn't add to the third byte
            asm.INC(0x1862, asm.ABS),       # INC $1862

            "GIL_NO_WRAP",                  # gil_no_wrap:
            asm.LDA(0x7f, asm.IMM8),        # LDA #$7F
            asm.CMP(0x1860, asm.ABS),       # CMP $1860
            asm.LDA(0x96, asm.IMM8),        # LDA #$96
            asm.SBC(0x1861, asm.ABS),       # SBC $1861
            asm.LDA(0x98, asm.IMM8),        # LDA #$98
            asm.SBC(0x1862, asm.ABS),       # SBC $1862
            asm.BCS("TREASURE_WRAPUP"),     # BCS treasure_wrapup  ; if carry is still set, we didn't overflow our GP. time to finish up
            asm.LDX(0x967f, asm.IMM16),     # LDX #$967F
            asm.STX(0x1860, asm.ABS),       # STX $1860
            asm.LDA(0x98, asm.IMM8),        # LDA #$98
            asm.STA(0x1862, asm.ABS),       # STA $1862
            asm.BRA("TREASURE_WRAPUP"),     # BRA treasure_wrapup

            "NOT_GIL_TREASURE",             # not_gil_treasure:
            asm.BIT(0x40, asm.IMM8),        # BIT #$40  ; item?
            asm.BEQ("TREASURE_WRAPUP"),     # BEQ treasure_wrapup  ; if it isn't an item, it's an "Empty" or a MiaB, neither of which we need to do anything about here. not handling MiaB may be an oversight, but let's assume the end-user is smart enough not to remotely open one of those
            asm.LDA(0x1a, asm.DIR),         # LDA $1A
            asm.JSR(0xacfc, asm.ABS),       # JSR $ACFC  ; add the item to inventory

            "TREASURE_WRAPUP",              # treasure_wrapup:
            asm.TDC(),                      # TDC
            asm.LDA(0x05, asm.IMM8),        # command size
            asm.JMP(0x9b5c, asm.ABS),       # next command
        ]

        space = Write(Bank.C0, src, "custom loot_chest command")
        address = space.start_address

        opcode = 0xec
        _set_opcode_address(opcode, address)

        CollectTreasure.__init__ = lambda self, map_id, x, y : super().__init__(opcode, map_id.to_bytes(2, "little"), x, y)
        self.__init__(map_id, x, y)

    def __str__(self):
        return super().__str__(self.args)

# Collect the contents (only if it hasn't been collected)
# If it has been collected, make jump to target destination
class BranchIfTreasureCollected(_Branch):
    def __init__(self, chest_bit, destination):
        src = [
            "CHECK_TREASURE",               # check_treasure:
            # ED xxxx aa bb cc
            # xxxx is treasure bit. there's only #$2F treasure bytes
            # aa bb cc is the event to jump to should a treasure already be open
            asm.A16(),                      # REP #$20
            asm.LDA(0xeb, asm.DIR),         # LDA $EB  ; load our treasure byte/bit that we want to check
            asm.PHA(),                      # PHA
            asm.AND(0x0007, asm.IMM16),     # AND #$0007  ; mask out the byte, keep the bits
            asm.TAX(),                      # TAX
            asm.PLA(),                      # PLA
            asm.AND(0x01F8, asm.IMM16),     # AND #$01F8  ; now mask out the bits, keep the byte
            asm.LSR(),                      # LSR A
            asm.LSR(),                      # LSR A
            asm.LSR(),                      # LSR A
            asm.TAY(),                      # TAY
            asm.LDA(0x1e40, asm.ABS_Y),     # LDA $1E40,Y  ; load the treasure we are checking for
            asm.AND(0xc0bafc, asm.ABS_X),   # AND $C0BAFC,X  ; is the bit we are checking for set? meaning, is this box already open?
            asm.A8(),                       # SEP #$20
            asm.BNE("BRANCH_TO_DEST"),      # BNE check_succeeds  ; branch if so!
            asm.BRA("RETURN"),
            "BRANCH_TO_DEST",               # check_succeeds:
            asm.TDC(),                      # TDC
            asm.LDX(0xed, asm.DIR),         # LDX $ED load address
            asm.STX(0xe5, asm.DIR),         # STX $E5 store first 4 bytes
            asm.LDA(0xef, asm.DIR),         # LDA $EF st
            asm.CLC(),                      # CLC
            asm.ADC(0xca, asm.IMM8),        # ADC #$CA
            asm.STA(0xe7, asm.DIR),         # STA $E7
            asm.JMP(0x9a6d, asm.ABS),       # JMP $9A6D
            "RETURN",
            asm.TDC(),                      # TDC
            asm.LDA(0x06, asm.IMM8),        # LDA #$06
            asm.JMP(0x9b5c, asm.ABS),       # JMP $9B5C - next command
        ]

        space = Write(Bank.C0, src, "custom loot_treasure command")
        address = space.start_address

        opcode = 0xed
        _set_opcode_address(opcode, address)

        BranchIfTreasureCollected.__init__ = lambda self, chest_bit, destination : super().__init__(opcode, [chest_bit.to_bytes(2, "little")], destination)

        self.__init__(chest_bit, destination)

    def __str__(self):
        return super().__str__(self.args)
