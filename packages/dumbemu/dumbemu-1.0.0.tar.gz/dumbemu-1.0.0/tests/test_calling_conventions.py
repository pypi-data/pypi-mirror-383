import sys, types
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_MODE_64
from dumbemu.utils.constants import Addr
from dumbemu.context import Context
from dumbemu.mem.memory import Mem
from dumbemu.cpu.regs import Regs
from dumbemu.mem.stack import Stack
from dumbemu.cpu.x86 import X86
from dumbemu.cpu.x64 import X64

# Mock PE for testing
class MockPE:
    def __init__(self, is_64):
        self.is_64 = is_64

def test_x64_prep_registers_and_stack():
    pe = MockPE(is_64=True)
    ctx = Context(pe)
    mem = Mem(ctx)
    regs = Regs(ctx)
    stack = Stack(ctx)
    sp = stack.init(mem, regs)

    # Prepare a call with 6 args to enforce both regs + stack
    args = (1,2,3,4,5,6)
    new_sp = regs.prep(mem, sp, args)
    ctx.uc.reg_write(regs.sp, new_sp)

    # RCX..R9 should be 1..4
    assert ctx.uc.reg_read(regs.arch._to_id('rcx')) == 1
    assert ctx.uc.reg_read(regs.arch._to_id('rdx')) == 2
    assert ctx.uc.reg_read(regs.arch._to_id('r8'))  == 3
    assert ctx.uc.reg_read(regs.arch._to_id('r9'))  == 4
    # First stack arg (5) is at [rsp+8] (after return address)
    rsp = ctx.uc.reg_read(regs.sp)
    five = int.from_bytes(ctx.uc.mem_read(rsp+8, 8), 'little')
    six  = int.from_bytes(ctx.uc.mem_read(rsp+16, 8), 'little')
    assert five == 5 and six == 6

def test_x86_prep_push_order_and_ret():
    pe = MockPE(is_64=False)
    ctx = Context(pe)
    mem = Mem(ctx)
    regs = Regs(ctx)
    stack = Stack(ctx)
    sp = stack.init(mem, regs)
    args = (0x11, 0x22, 0x33)
    new_sp = regs.prep(mem, sp, args)

    # Stack (top first): [FAKE_RET][arg1][arg2][arg3]
    ret = int.from_bytes(ctx.uc.mem_read(new_sp, 4), 'little')
    a1  = int.from_bytes(ctx.uc.mem_read(new_sp+4, 4), 'little')
    a2  = int.from_bytes(ctx.uc.mem_read(new_sp+8, 4), 'little')
    a3  = int.from_bytes(ctx.uc.mem_read(new_sp+12,4), 'little')
    assert a1 == 0x11 and a2 == 0x22 and a3 == 0x33
