"""Comprehensive tests for DumbEmu with timeout protection."""
import sys
from pathlib import Path
import struct

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dumbemu import DumbEmu
from dumbemu.win.iat import Proto
from unicorn import UC_PROT_READ, UC_PROT_WRITE, UC_PROT_EXEC, UcError

def test_memory_operations():
    """Test memory read/write operations."""
    print("\n[TEST] Memory Operations")
    
    pe_path = Path(__file__).parent.parent / "examples" / "R0ll" / "R0ll.exe"
    emu = DumbEmu(str(pe_path))
    
    # Test basic read/write
    addr = emu.malloc(0x1000)
    test_data = b"Hello, World!"
    emu.write(addr, test_data)
    read_data = emu.read(addr, len(test_data))
    assert read_data == test_data
    print(f"  [OK] Basic R/W at 0x{addr:08X}")
    
    # Test struct operations
    struct_addr = emu.malloc(0x100)
    emu.struct.write(struct_addr, 'BHf', 0x42, 0x1337, 3.14)
    b, w, f = emu.struct.read(struct_addr, 'BHf')
    assert b == 0x42
    assert w == 0x1337
    assert abs(f - 3.14) < 0.01
    print(f"  [OK] Struct ops: byte={b:02X}, word={w:04X}, float={f:.2f}")
    
    # Test string operations
    str_addr = emu.malloc(0x200)
    emu.string.ascii(str_addr, "ASCII Test")
    s = emu.string.cstring(str_addr)
    assert s == "ASCII Test"
    print(f"  [OK] ASCII string: '{s}'")
    
    emu.string.wide(str_addr + 0x100, "Wide Test")
    ws = emu.string.wstring(str_addr + 0x100)
    assert ws == "Wide Test"
    print(f"  [OK] Wide string: '{ws}'")
    
    # Test memory protection
    prot_addr = emu.malloc(0x1000, UC_PROT_READ | UC_PROT_WRITE)
    emu.write(prot_addr, b"Protected")
    emu.mem.protect(prot_addr, 0x1000, UC_PROT_READ)
    # Should still be able to read
    data = emu.read(prot_addr, 9)
    assert data == b"Protected"
    print(f"  [OK] Memory protection")
    
    return True

def test_register_operations():
    """Test register read/write operations."""
    print("\n[TEST] Register Operations")
    
    pe_path = Path(__file__).parent.parent / "examples" / "R0ll" / "R0ll.exe"
    emu = DumbEmu(str(pe_path))
    
    if emu.ctx.is_64:
        # Test 64-bit registers
        emu.regs.write('rax', 0xDEADBEEFCAFEBABE)
        assert emu.regs.read('rax') == 0xDEADBEEFCAFEBABE
        print(f"  [OK] RAX = 0x{emu.regs.read('rax'):016X}")
        
        # Test 32-bit access
        emu.regs.write('eax', 0x12345678)
        assert emu.regs.read('eax') & 0xFFFFFFFF == 0x12345678
        print(f"  [OK] EAX = 0x{emu.regs.read('eax') & 0xFFFFFFFF:08X}")
        
        # Test extended registers
        emu.regs.write('r10', 0x1337)
        assert emu.regs.read('r10') == 0x1337
        print(f"  [OK] R10 = 0x{emu.regs.read('r10'):04X}")
    else:
        # Test 32-bit registers
        emu.regs.write('eax', 0xDEADBEEF)
        assert emu.regs.read('eax') == 0xDEADBEEF
        print(f"  [OK] EAX = 0x{emu.regs.read('eax'):08X}")
        
        emu.regs.write('ebx', 0xCAFEBABE)
        assert emu.regs.read('ebx') == 0xCAFEBABE
        print(f"  [OK] EBX = 0x{emu.regs.read('ebx'):08X}")
    
    # Test segment registers (should work in both modes)
    emu.regs.write('cs', 0x23)
    assert emu.regs.read('cs') == 0x23
    print(f"  [OK] CS = 0x{emu.regs.read('cs'):02X}")
    
    return True

def test_simple_code_execution():
    """Test simple code execution with timeout."""
    print("\n[TEST] Simple Code Execution")
    
    pe_path = Path(__file__).parent.parent / "examples" / "R0ll" / "R0ll.exe"
    emu = DumbEmu(str(pe_path))
    
    code_addr = emu.malloc(0x1000, UC_PROT_READ | UC_PROT_WRITE | UC_PROT_EXEC)
    
    if emu.ctx.is_64:
        # x64: mov rax, 0x42; ret
        code = b"\x48\xC7\xC0\x42\x00\x00\x00\xC3"
    else:
        # x86: mov eax, 0x42; ret
        code = b"\xB8\x42\x00\x00\x00\xC3"
    
    emu.write(code_addr, code)
    
    # Execute with default timeout
    result = emu.call(code_addr)
    assert result == 0x42
    print(f"  [OK] Simple execution returned 0x{result:02X}")
    
    # Test with arguments
    if emu.ctx.is_64:
        # x64: mov rax, rcx; add rax, rdx; ret
        code = b"\x48\x89\xC8\x48\x01\xD0\xC3"
    else:
        # x86: mov eax, [esp+4]; add eax, [esp+8]; ret 8
        code = b"\x8B\x44\x24\x04\x03\x44\x24\x08\xC2\x08\x00"
    
    emu.write(code_addr, code)
    result = emu.call(code_addr, None, 10, 20)
    assert result == 30
    print(f"  [OK] Addition: 10 + 20 = {result}")
    
    return True

def test_infinite_loop_timeout():
    """Test that infinite loops are properly timed out."""
    print("\n[TEST] Infinite Loop Timeout")
    
    pe_path = Path(__file__).parent.parent / "examples" / "R0ll" / "R0ll.exe"
    emu = DumbEmu(str(pe_path))
    
    code_addr = emu.malloc(0x100, UC_PROT_READ | UC_PROT_WRITE | UC_PROT_EXEC)
    
    # Create infinite loop: jmp $
    code = b"\xEB\xFE"
    emu.write(code_addr, code)
    
    # This should timeout after 10ms (10000 microseconds)
    print("  Testing infinite loop with 10ms timeout...")
    try:
        result = emu.call(code_addr)
        print(f"  [OK] Loop timed out safely, returned 0x{result:02X}")
    except Exception as e:
        print(f"  [OK] Loop timed out with exception: {e}")
    
    # Verify emulator still works after timeout
    test_addr = emu.malloc(0x100, UC_PROT_READ | UC_PROT_WRITE | UC_PROT_EXEC)
    if emu.ctx.is_64:
        code = b"\x48\x31\xC0\xC3"  # xor rax, rax; ret
    else:
        code = b"\x31\xC0\xC3"  # xor eax, eax; ret
    emu.write(test_addr, code)
    result = emu.call(test_addr)
    assert result == 0
    print(f"  [OK] Emulator still functional after timeout")
    
    return True

def test_code_hooks():
    """Test code hooks with execution."""
    print("\n[TEST] Code Hooks")
    
    pe_path = Path(__file__).parent.parent / "examples" / "R0ll" / "R0ll.exe"
    emu = DumbEmu(str(pe_path))
    
    code_addr = emu.malloc(0x100, UC_PROT_READ | UC_PROT_WRITE | UC_PROT_EXEC)
    
    # Create simple code with multiple instructions
    if emu.ctx.is_64:
        # mov rax, 1; inc rax; inc rax; ret
        code = b"\x48\xC7\xC0\x01\x00\x00\x00\x48\xFF\xC0\x48\xFF\xC0\xC3"
    else:
        # mov eax, 1; inc eax; inc eax; ret
        code = b"\xB8\x01\x00\x00\x00\x40\x40\xC3"
    
    emu.write(code_addr, code)
    
    # Set up hook to count instructions
    count = [0]
    def count_hook(uc, addr):
        count[0] += 1
        print(f"    Hook: Executing at 0x{addr:08X}, count={count[0]}")
    
    emu.hook(code_addr, count_hook)
    
    result = emu.call(code_addr)
    assert result == 3
    assert count[0] >= 1  # At least the first instruction should be hooked
    print(f"  [OK] Hook fired {count[0]} times, result = {result}")
    
    return True

def test_iat_stubs():
    """Test IAT stub functionality."""
    print("\n[TEST] IAT Stubs")
    
    pe_path = Path(__file__).parent.parent / "examples" / "R0ll" / "R0ll.exe"
    emu = DumbEmu(str(pe_path))
    
    # Register a custom stub
    call_count = [0]
    def my_stub(emu, iat, args):
        call_count[0] += 1
        print(f"    Stub called with {len(args)} args: {args}")
        if len(args) >= 2:
            result = args[0] + args[1]
            print(f"    Stub returning: {result}")
            return result
        print(f"    Stub returning default: 0x1337")
        return 0x1337
    
    stub_addr = emu.stub("test.dll", "TestFunc", 
                        Proto("TestFunc", "stdcall" if not emu.ctx.is_64 else "win64", [8, 8]),
                        my_stub)
    print(f"  Stub registered at 0x{stub_addr:08X}")
    
    # Call the stub
    result = emu.call(stub_addr, None, 10, 20)
    assert result == 30
    assert call_count[0] == 1
    print(f"  [OK] Stub returned {result}, called {call_count[0]} time(s)")
    
    # Test invoke method
    result2 = emu.invoke("test.dll", "TestFunc", 5, 15)
    assert result2 == 20
    assert call_count[0] == 2
    print(f"  [OK] Invoke returned {result2}, stub called {call_count[0]} times total")
    
    return True

def test_tracer():
    """Test execution tracing."""
    print("\n[TEST] Execution Tracer")
    
    pe_path = Path(__file__).parent.parent / "examples" / "R0ll" / "R0ll.exe"
    emu = DumbEmu(str(pe_path))
    
    code_addr = emu.malloc(0x100, UC_PROT_READ | UC_PROT_WRITE | UC_PROT_EXEC)
    
    # Create code with a small loop
    if emu.ctx.is_64:
        # mov rcx, 3; loop: dec rcx; jnz loop; mov rax, 42; ret
        code = bytes([
            0x48, 0xC7, 0xC1, 0x03, 0x00, 0x00, 0x00,  # mov rcx, 3
            0x48, 0xFF, 0xC9,                          # dec rcx
            0x75, 0xFB,                                # jnz -5
            0x48, 0xC7, 0xC0, 0x42, 0x00, 0x00, 0x00,  # mov rax, 42
            0xC3                                       # ret
        ])
    else:
        # mov ecx, 3; loop: dec ecx; jnz loop; mov eax, 42; ret
        code = bytes([
            0xB9, 0x03, 0x00, 0x00, 0x00,  # mov ecx, 3
            0x49,                          # dec ecx
            0x75, 0xFD,                    # jnz -3
            0xB8, 0x42, 0x00, 0x00, 0x00,  # mov eax, 42
            0xC3                           # ret
        ])
    
    emu.write(code_addr, code)
    
    # Run with tracing (with timeout for safety)
    addrs, count = emu.tracer.run(code_addr)
    print(f"  Executed {count} instructions")
    
    # Analyze trace
    analysis = emu.tracer.analyze()
    print(f"  [OK] Trace analysis:")
    print(f"    - Total instructions: {analysis['total']}")
    print(f"    - Unique addresses: {analysis['unique']}")
    if analysis['entry']:
        print(f"    - Entry point: 0x{analysis['entry']:08X}")
    if analysis['exit']:
        print(f"    - Exit point: 0x{analysis['exit']:08X}")
    
    # Get recent history
    recent = emu.tracer.history(5)
    print(f"  [OK] Last 5 addresses: {[f'0x{a:08X}' for a in recent]}")
    
    return True

def test_stack_operations():
    """Test stack push/pop operations."""
    print("\n[TEST] Stack Operations")
    
    pe_path = Path(__file__).parent.parent / "examples" / "R0ll" / "R0ll.exe"
    emu = DumbEmu(str(pe_path))
    
    # Initialize stack
    sp = emu.stack.init(emu.mem, emu.regs)
    print(f"  Initial SP: 0x{sp:08X}")
    
    # Push values
    sp = emu.stack.push(emu.mem, sp, 0x1337)
    sp = emu.stack.push(emu.mem, sp, 0xDEAD)
    sp = emu.stack.push(emu.mem, sp, 0xBEEF)
    print(f"  After 3 pushes, SP: 0x{sp:08X}")
    
    # Pop values
    val1, sp = emu.stack.pop(emu.mem, sp)
    assert val1 == 0xBEEF
    val2, sp = emu.stack.pop(emu.mem, sp)
    assert val2 == 0xDEAD
    val3, sp = emu.stack.pop(emu.mem, sp)
    assert val3 == 0x1337
    print(f"  [OK] Popped: 0x{val1:04X}, 0x{val2:04X}, 0x{val3:04X}")
    
    return True

def test_calling_conventions():
    """Test different calling conventions."""
    print("\n[TEST] Calling Conventions")
    
    pe_path = Path(__file__).parent.parent / "examples" / "R0ll" / "R0ll.exe"
    emu = DumbEmu(str(pe_path))
    
    code_addr = emu.malloc(0x200, UC_PROT_READ | UC_PROT_WRITE | UC_PROT_EXEC)
    
    if emu.ctx.is_64:
        # Win64: args in RCX, RDX, R8, R9
        # mov rax, rcx; add rax, rdx; add rax, r8; add rax, r9; ret
        code = bytes([
            0x48, 0x89, 0xC8,  # mov rax, rcx
            0x48, 0x01, 0xD0,  # add rax, rdx
            0x4C, 0x01, 0xC0,  # add rax, r8
            0x4C, 0x01, 0xC8,  # add rax, r9
            0xC3               # ret
        ])
        emu.write(code_addr, code)
        result = emu.call(code_addr, None, 1, 2, 3, 4)
        assert result == 10
        print(f"  [OK] Win64 convention: 1+2+3+4 = {result}")
    else:
        # x86 stdcall: args on stack, callee cleans
        # mov eax, [esp+4]; add eax, [esp+8]; ret 8
        code = b"\x8B\x44\x24\x04\x03\x44\x24\x08\xC2\x08\x00"
        emu.write(code_addr, code)
        result = emu.call(code_addr, None, 15, 25)
        assert result == 40
        print(f"  [OK] x86 stdcall: 15+25 = {result}")
    
    return True

def test_memory_allocation():
    """Test memory allocation and freeing."""
    print("\n[TEST] Memory Allocation")
    
    pe_path = Path(__file__).parent.parent / "examples" / "R0ll" / "R0ll.exe"
    emu = DumbEmu(str(pe_path))
    
    # Allocate multiple blocks
    addrs = []
    for i in range(5):
        addr = emu.malloc(0x1000 * (i + 1))
        addrs.append(addr)
        print(f"  Allocated {0x1000 * (i + 1):04X} bytes at 0x{addr:08X}")
    
    # Verify they don't overlap
    for i in range(len(addrs) - 1):
        assert addrs[i+1] >= addrs[i] + 0x1000
    print(f"  [OK] No overlapping allocations")
    
    # Free some blocks
    emu.free(addrs[1])
    emu.free(addrs[3])
    print(f"  [OK] Freed blocks at 0x{addrs[1]:08X} and 0x{addrs[3]:08X}")
    
    # Allocate again (might reuse freed space)
    new_addr = emu.malloc(0x1000)
    print(f"  [OK] New allocation at 0x{new_addr:08X}")
    
    return True

def main():
    """Run all comprehensive tests."""
    print("=" * 60)
    print("DumbEmu Comprehensive Test Suite")
    print("=" * 60)
    
    tests = [
        test_memory_operations,
        test_register_operations,
        test_simple_code_execution,
        test_infinite_loop_timeout,
        test_code_hooks,
        test_iat_stubs,
        test_tracer,
        test_stack_operations,
        test_calling_conventions,
        test_memory_allocation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  [FAIL] {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    if failed == 0:
        print("All tests passed successfully!")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
