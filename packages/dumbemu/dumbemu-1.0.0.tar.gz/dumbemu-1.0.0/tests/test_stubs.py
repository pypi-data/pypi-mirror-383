import pytest
from dumbemu import DumbEmu
from dumbemu.win.iat import Proto
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_MODE_64

# These tests construct an emulator using a *real PE* path at runtime.
# For CI or local, point to a tiny DLL/EXE. Here we skip if no file supplied.

def _maybe_pe_path():
    import os
    return os.environ.get('DUMBEMU_TEST_IMAGE')

@pytest.mark.skipif(_maybe_pe_path() is None, reason="Set DUMBEMU_TEST_IMAGE to run integration tests")
def test_iat_stdcall_stub_pops_stack(monkeypatch):
    img = _maybe_pe_path()
    emu = DumbEmu(img)

    popped = {}

    def sum3(stubs, uc, args):
        return int(args[0] + args[1] + args[2])

    # Attach as stdcall with 3 args
    proto = Prototype('Sum3', 'stdcall', [4,4,4], ret_size=4)
    va = emu.stub('kernel32.dll', 'Sum3', proto, sum3)

    # Build stack: call import by directly entering stub
    # Push ret on stack and three args, then start at stub address
    sp = emu.cpu.ensure_stack(emu.mem)
    # right-to-left push
    for a in (3,2,1)[::-1]:
        sp -= 4
        emu.mem.pack(sp, a, 32)
    sp -= 4
    emu.mem.pack(sp, 0xCAFEBABE, 32)
    emu.uc.reg_write(emu.cpu.stack_pointer_reg, sp)

    emu.uc.emu_start(va, 0, count=10_000)
    # After stdcall, ESP should have popped args + ret (4*4 + 4)
    esp = emu.uc.reg_read(emu.cpu.stack_pointer_reg)
    assert esp == sp + 4 + 12
    assert emu.cpu.get_return_value() == 6

@pytest.mark.skipif(_maybe_pe_path() is None, reason="Set DUMBEMU_TEST_IMAGE to run integration tests")
def test_win64_stub_sets_return_value(monkeypatch):
    img = _maybe_pe_path()
    emu = DumbEmu(img)

    def add(stubs, uc, args):
        return int(args[0] + args[1] + args[2] + args[3] + args[4])

    proto = Prototype('Add5', 'win64', [8,8,8,8,8])
    va = emu.stub('kernel32.dll', 'Add5', proto, add)

    # Prepare RCX..R9 and stack arg
    sp = emu.cpu.ensure_stack(emu.mem)
    # Put stack arg (5th) above ret
    sp -= 8
    emu.mem.pack(sp, 5, 64)
    sp -= 8
    emu.mem.pack(sp, 0xCAFEBABECAFED00D, 64)
    emu.uc.reg_write(emu.cpu.stack_pointer_reg, sp)
    # regs
    for reg, val in zip(['rcx','rdx','r8','r9'], [1,1,1,1]):
        emu.uc.reg_write(emu.cpu.arch._name_to_reg(reg), val)

    emu.uc.emu_start(va, 0, count=10_000)
    assert emu.cpu.get_return_value() == 9
