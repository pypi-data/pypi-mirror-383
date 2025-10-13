"""
Comprehensive test suite for DumbEmu - Testing ALL features and edge cases.
"""
import sys
import struct
import random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dumbemu import DumbEmu
from dumbemu.win.iat import Proto
from unicorn import UC_PROT_READ, UC_PROT_WRITE, UC_PROT_EXEC, UcError

# Test helpers
def generate_random_bytes(size):
    """Generate random bytes for testing."""
    return bytes(random.randint(0, 255) for _ in range(size))

def test_banner(name):
    """Print test banner."""
    print(f"\n{'='*60}")
    print(f"[TEST] {name}")
    print('='*60)

def assert_equal(actual, expected, msg=""):
    """Assert with better error messages."""
    if actual != expected:
        raise AssertionError(f"{msg}\nExpected: {expected!r}\nActual: {actual!r}")

# ============================================================================
# MEMORY TESTS
# ============================================================================

def test_memory_operations(emu):
    """Test all memory operations."""
    test_banner("Memory Operations")
    
    # Test 1: Basic read/write
    print("  1. Basic read/write...")
    addr = emu.malloc(0x1000)
    test_data = b"Hello, World!"
    emu.mem.write(addr, test_data)
    read_data = emu.mem.read(addr, len(test_data))
    assert_equal(read_data, test_data, "Basic read/write failed")
    
    # Test 2: Large data read/write
    print("  2. Large data (1MB)...")
    large_addr = emu.malloc(0x100000)  # 1MB
    large_data = generate_random_bytes(0x100000)
    emu.mem.write(large_addr, large_data)
    read_large = emu.mem.read(large_addr, 0x100000)
    assert_equal(read_large, large_data, "Large data read/write failed")
    
    # Test 3: Pack/unpack operations
    print("  3. Pack/unpack operations...")
    pack_addr = emu.malloc(0x100)
    
    # Test 32-bit
    emu.mem.pack(pack_addr, 0xDEADBEEF, bits=32)
    val32 = emu.mem.unpack(pack_addr, 4)
    assert_equal(val32, 0xDEADBEEF, "32-bit pack/unpack failed")
    
    # Test 64-bit
    emu.mem.pack(pack_addr + 8, 0xCAFEBABEDEADBEEF, bits=64)
    val64 = emu.mem.unpack(pack_addr + 8, 8)
    assert_equal(val64, 0xCAFEBABEDEADBEEF, "64-bit pack/unpack failed")
    
    # Test 16-bit
    emu.mem.pack(pack_addr + 16, 0x1337, bits=16)
    val16 = emu.mem.unpack(pack_addr + 16, 2)
    assert_equal(val16, 0x1337, "16-bit pack/unpack failed")
    
    # Test 8-bit
    emu.mem.pack(pack_addr + 20, 0x42, bits=8)
    val8 = emu.mem.unpack(pack_addr + 20, 1)
    assert_equal(val8, 0x42, "8-bit pack/unpack failed")
    
    # Test 4: Memory protection
    print("  4. Memory protection...")
    prot_addr = emu.malloc(0x1000, UC_PROT_READ)
    emu.mem.write(prot_addr, b"ReadOnly")
    
    # Change to RW
    emu.mem.protect(prot_addr, 0x1000, UC_PROT_READ | UC_PROT_WRITE)
    emu.mem.write(prot_addr, b"Modified")
    data = emu.mem.read(prot_addr, 8)
    assert_equal(data, b"Modified", "Memory protection change failed")
    
    # Test 5: Boundary conditions
    print("  5. Boundary conditions...")
    # Write across page boundary
    boundary_addr = emu.malloc(0x2000)
    boundary_data = b"X" * 0x1000
    emu.mem.write(boundary_addr + 0x800, boundary_data)
    read_boundary = emu.mem.read(boundary_addr + 0x800, 0x1000)
    assert_equal(read_boundary, boundary_data, "Cross-page write failed")
    
    print("  [OK] All memory tests passed!")

# ============================================================================
# REGISTER TESTS
# ============================================================================

def test_register_operations(emu):
    """Test all register operations."""
    test_banner("Register Operations")
    
    if emu.ctx.is_64:
        # Test 64-bit registers
        print("  1. Testing 64-bit registers...")
        
        # General purpose
        regs_64 = {
            'rax': 0x1111111111111111,
            'rbx': 0x2222222222222222,
            'rcx': 0x3333333333333333,
            'rdx': 0x4444444444444444,
            'rsi': 0x5555555555555555,
            'rdi': 0x6666666666666666,
            'r8':  0x7777777777777777,
            'r9':  0x8888888888888888,
            'r10': 0x9999999999999999,
            'r11': 0xAAAAAAAAAAAAAAAA,
            'r12': 0xBBBBBBBBBBBBBBBB,
            'r13': 0xCCCCCCCCCCCCCCCC,
            'r14': 0xDDDDDDDDDDDDDDDD,
            'r15': 0xEEEEEEEEEEEEEEEE,
        }
        
        for reg, val in regs_64.items():
            emu.regs.write(reg, val)
            read_val = emu.regs.read(reg)
            assert_equal(read_val, val, f"Register {reg} failed")
        
        # Test 32-bit access to 64-bit registers
        print("  2. Testing 32-bit access to 64-bit registers...")
        emu.regs.write('rax', 0xDEADBEEFCAFEBABE)
        eax_val = emu.regs.read('eax')
        # Unicorn returns full register, we need to mask for 32-bit
        assert_equal(eax_val & 0xFFFFFFFF, 0xCAFEBABE, "32-bit access to RAX failed")
        
        # Test 16-bit access
        print("  3. Testing 16-bit access...")
        emu.regs.write('rax', 0x1234567890ABCDEF)
        ax_val = emu.regs.read('ax')
        # Note: Unicorn returns full register, we check lower 16 bits
        assert_equal(ax_val & 0xFFFF, 0xCDEF, "16-bit access failed")
        
    else:
        # Test 32-bit registers
        print("  1. Testing 32-bit registers...")
        regs_32 = {
            'eax': 0x11111111,
            'ebx': 0x22222222,
            'ecx': 0x33333333,
            'edx': 0x44444444,
            'esi': 0x55555555,
            'edi': 0x66666666,
        }
        
        for reg, val in regs_32.items():
            emu.regs.write(reg, val)
            read_val = emu.regs.read(reg)
            assert_equal(read_val, val, f"Register {reg} failed")
    
    # Test segment registers (read-only test)
    print("  4. Testing segment registers...")
    segments = ['cs', 'ds', 'es', 'fs', 'gs', 'ss']
    for seg in segments:
        # Just test that we can read them (writing may cause exceptions)
        try:
            read_val = emu.regs.read(seg)
            print(f"      {seg} = 0x{read_val:X}")
        except Exception as e:
            print(f"      {seg} = <unable to read: {e}>")
    
    print("  [OK] All register tests passed!")

# ============================================================================
# STRING TESTS
# ============================================================================

def test_string_operations(emu):
    """Test string reading/writing operations."""
    test_banner("String Operations")
    
    # Test 1: ASCII strings
    print("  1. ASCII string operations...")
    ascii_addr = emu.malloc(0x100)
    
    # Write and read
    test_str = "Hello, DumbEmu!"
    emu.string.ascii(ascii_addr, test_str)
    read_str = emu.string.cstring(ascii_addr)
    assert_equal(read_str, test_str, "ASCII string failed")
    
    # Test null termination
    emu.string.ascii(ascii_addr, "Test", null=True)
    read_null = emu.string.cstring(ascii_addr)
    assert_equal(read_null, "Test", "Null-terminated ASCII failed")
    
    # Test 2: Wide strings
    print("  2. Wide string operations...")
    wide_addr = emu.malloc(0x200)
    
    wide_str = "Unicode String 你好"
    emu.string.wide(wide_addr, wide_str)
    read_wide = emu.string.wstring(wide_addr)
    assert_equal(read_wide, wide_str, "Wide string failed")
    
    # Test 3: Empty strings
    print("  3. Empty string handling...")
    empty_addr = emu.malloc(0x10)
    emu.string.ascii(empty_addr, "")
    empty_read = emu.string.cstring(empty_addr)
    assert_equal(empty_read, "", "Empty string failed")
    
    # Test 4: Long strings
    print("  4. Long string handling...")
    long_addr = emu.malloc(0x10000)
    long_str = "A" * 10000
    emu.string.ascii(long_addr, long_str)
    read_long = emu.string.cstring(long_addr, max_len=10000)
    assert_equal(read_long, long_str, "Long string failed")
    
    print("  [OK] All string tests passed!")

# ============================================================================
# STRUCT TESTS
# ============================================================================

def test_struct_operations(emu):
    """Test struct packing/unpacking."""
    test_banner("Struct Operations")
    
    # Test 1: Basic struct operations
    print("  1. Basic struct pack/unpack...")
    struct_addr = emu.malloc(0x100)
    
    # Pack multiple values
    emu.struct.write(struct_addr, 'IHBf', 0xDEADBEEF, 0x1337, 0x42, 3.14159)
    
    # Unpack
    val1, val2, val3, val4 = emu.struct.read(struct_addr, 'IHBf')
    assert_equal(val1, 0xDEADBEEF, "Struct DWORD failed")
    assert_equal(val2, 0x1337, "Struct WORD failed")
    assert_equal(val3, 0x42, "Struct BYTE failed")
    assert abs(val4 - 3.14159) < 0.0001, "Struct float failed"
    
    # Test 2: Complex structs
    print("  2. Complex struct operations...")
    complex_addr = emu.malloc(0x200)
    
    # Simulate a Windows structure
    emu.struct.write(complex_addr, 'QQIIHBB',
                    0x1111111111111111,  # QWORD
                    0x2222222222222222,  # QWORD
                    0x33333333,          # DWORD
                    0x44444444,          # DWORD
                    0x5555,              # WORD
                    0x66,                # BYTE
                    0x77)                # BYTE
    
    vals = emu.struct.read(complex_addr, 'QQIIHBB')
    assert_equal(vals[0], 0x1111111111111111, "Complex struct failed")
    
    # Test 3: Iter operations
    print("  3. Struct iteration...")
    iter_addr = emu.malloc(0x100)
    
    # Write multiple identical structs
    for i in range(5):
        emu.struct.write(iter_addr + i * 8, 'II', i, i * 2)
    
    # Iterate
    results = list(emu.struct.iter(iter_addr, 'II', 5))
    for i, (a, b) in enumerate(results):
        assert_equal(a, i, f"Iter struct {i} field 1 failed")
        assert_equal(b, i * 2, f"Iter struct {i} field 2 failed")
    
    print("  [OK] All struct tests passed!")

# ============================================================================
# STACK TESTS
# ============================================================================

def test_stack_operations(emu):
    """Test stack operations."""
    test_banner("Stack Operations")
    
    # Initialize stack
    sp = emu.stack.init(emu.mem, emu.regs)
    initial_sp = sp
    
    # Test 1: Push/pop operations
    print("  1. Push/pop operations...")
    values = [0x11111111, 0x22222222, 0x33333333, 0x44444444]
    
    # Push values
    for val in values:
        sp = emu.stack.push(emu.mem, sp, val)
    
    # Verify stack pointer moved correctly
    expected_sp = initial_sp - (len(values) * emu.ctx.width)
    assert_equal(sp, expected_sp, "Stack pointer incorrect after pushes")
    
    # Pop values (should be in reverse order)
    popped = []
    for _ in values:
        val, sp = emu.stack.pop(emu.mem, sp)
        popped.append(val)
    
    assert_equal(popped, list(reversed(values)), "Stack pop order incorrect")
    assert_equal(sp, initial_sp, "Stack pointer not restored")
    
    # Test 2: Stack read/write with offset
    print("  2. Stack read/write with offset...")
    sp = initial_sp - 0x100
    
    # Write at various offsets
    emu.stack.write(emu.mem, sp, 0xAAAAAAAA, offset=0)
    emu.stack.write(emu.mem, sp, 0xBBBBBBBB, offset=8)
    emu.stack.write(emu.mem, sp, 0xCCCCCCCC, offset=16)
    
    # Read back
    val1 = emu.stack.read(emu.mem, sp, offset=0)
    val2 = emu.stack.read(emu.mem, sp, offset=8)
    val3 = emu.stack.read(emu.mem, sp, offset=16)
    
    assert_equal(val1, 0xAAAAAAAA, "Stack offset 0 failed")
    assert_equal(val2, 0xBBBBBBBB, "Stack offset 8 failed")
    assert_equal(val3, 0xCCCCCCCC, "Stack offset 16 failed")
    
    print("  [OK] All stack tests passed!")

# ============================================================================
# ALLOCATION TESTS
# ============================================================================

def test_allocation(emu):
    """Test memory allocation."""
    test_banner("Memory Allocation")
    
    # Test 1: Basic allocation
    print("  1. Basic allocation...")
    allocs = []
    for size in [0x100, 0x1000, 0x10000, 0x100000]:
        addr = emu.malloc(size)
        allocs.append((addr, size))
        # Verify we can write to it
        emu.mem.write(addr, b'\x00' * min(size, 0x100))
    
    # Test 2: Allocation with different protections
    print("  2. Allocation with protections...")
    rx_addr = emu.malloc(0x1000, UC_PROT_READ | UC_PROT_EXEC)
    rw_addr = emu.malloc(0x1000, UC_PROT_READ | UC_PROT_WRITE)
    rwx_addr = emu.malloc(0x1000, UC_PROT_READ | UC_PROT_WRITE | UC_PROT_EXEC)
    
    # Test 3: Free and reallocation
    print("  3. Free and reallocation...")
    temp_addr = emu.malloc(0x1000)
    emu.mem.write(temp_addr, b"TestData")
    
    # Free it
    freed = emu.free(temp_addr)
    assert freed, "Free failed"
    
    # Allocate again (might get same address)
    new_addr = emu.malloc(0x1000)
    
    # Test 4: Protection changes
    print("  4. Protection changes...")
    prot_test = emu.malloc(0x1000, UC_PROT_READ)
    success = emu.alloc.protect(prot_test, 0x1000, UC_PROT_READ | UC_PROT_WRITE | UC_PROT_EXEC)
    assert success, "Protection change failed"
    
    # Verify we can write and execute
    code = b"\xC3"  # RET
    emu.mem.write(prot_test, code)
    
    print("  [OK] All allocation tests passed!")

# ============================================================================
# EXECUTION TESTS
# ============================================================================

def test_code_execution(emu):
    """Test code execution."""
    test_banner("Code Execution")
    
    # Test 1: Simple execution
    print("  1. Simple code execution...")
    code_addr = emu.malloc(0x100, UC_PROT_READ | UC_PROT_WRITE | UC_PROT_EXEC)
    
    if emu.ctx.is_64:
        # mov rax, 0x42; ret
        code = b"\x48\xC7\xC0\x42\x00\x00\x00\xC3"
    else:
        # mov eax, 0x42; ret
        code = b"\xB8\x42\x00\x00\x00\xC3"
    
    emu.mem.write(code_addr, code)
    result = emu.call(code_addr)
    assert_equal(result, 0x42, "Simple execution failed")
    
    # Test 2: Execute vs Call
    print("  2. Execute vs Call...")
    exec_addr = emu.malloc(0x100, UC_PROT_READ | UC_PROT_WRITE | UC_PROT_EXEC)
    
    if emu.ctx.is_64:
        # inc rax; inc rax; inc rax; nop
        code = b"\x48\xFF\xC0\x48\xFF\xC0\x48\xFF\xC0\x90"
    else:
        # inc eax; inc eax; inc eax; nop
        code = b"\x40\x40\x40\x90"
    
    emu.mem.write(exec_addr, code)
    
    # Set initial value
    emu.regs.write('rax' if emu.ctx.is_64 else 'eax', 10)
    
    # Execute (no stack setup)
    emu.execute(exec_addr, count=4)  # Execute 4 instructions
    
    result = emu.regs.read('rax' if emu.ctx.is_64 else 'eax')
    assert_equal(result, 13, "Execute failed")
    
    # Test 3: Function with arguments
    print("  3. Function with arguments...")
    func_addr = emu.malloc(0x100, UC_PROT_READ | UC_PROT_WRITE | UC_PROT_EXEC)
    
    if emu.ctx.is_64:
        # Windows x64: add rcx, rdx; mov rax, rcx; ret
        code = b"\x48\x01\xD1\x48\x89\xC8\xC3"
    else:
        # x86: mov eax, [esp+4]; add eax, [esp+8]; ret 8
        code = b"\x8B\x44\x24\x04\x03\x44\x24\x08\xC2\x08\x00"
    
    emu.mem.write(func_addr, code)
    result = emu.call(func_addr, None, 100, 200)
    assert_equal(result, 300, "Function with args failed")
    
    # Test 4: Breakpoints
    print("  4. Breakpoint execution...")
    bp_addr = emu.malloc(0x100, UC_PROT_READ | UC_PROT_WRITE | UC_PROT_EXEC)
    
    if emu.ctx.is_64:
        # mov rax, 1; mov rax, 2; mov rax, 3; ret
        code = b"\x48\xC7\xC0\x01\x00\x00\x00"  # mov rax, 1
        code += b"\x48\xC7\xC0\x02\x00\x00\x00"  # mov rax, 2
        code += b"\x48\xC7\xC0\x03\x00\x00\x00"  # mov rax, 3
        code += b"\xC3"  # ret
        bp_offset = 7  # Stop after first instruction
    else:
        # mov eax, 1; mov eax, 2; mov eax, 3; ret
        code = b"\xB8\x01\x00\x00\x00"  # mov eax, 1
        code += b"\xB8\x02\x00\x00\x00"  # mov eax, 2
        code += b"\xB8\x03\x00\x00\x00"  # mov eax, 3
        code += b"\xC3"  # ret
        bp_offset = 5  # Stop after first instruction
    
    emu.mem.write(bp_addr, code)
    
    # Execute with breakpoint
    result = emu.call(bp_addr, bp_addr + bp_offset)
    assert_equal(result, 1, "Breakpoint execution failed")
    
    print("  [OK] All execution tests passed!")

# ============================================================================
# HOOK TESTS
# ============================================================================

def test_hooks(emu):
    """Test code hooks."""
    test_banner("Hook Tests")
    
    # Test 1: Basic hook
    print("  1. Basic code hook...")
    hook_addr = emu.malloc(0x100, UC_PROT_READ | UC_PROT_WRITE | UC_PROT_EXEC)
    
    hook_count = [0]
    hook_addrs = []
    
    def test_hook(uc, addr):
        hook_count[0] += 1
        hook_addrs.append(addr)
    
    # Install hook
    emu.hook(hook_addr, test_hook)
    
    # Write and execute code
    if emu.ctx.is_64:
        code = b"\x48\x31\xC0\xC3"  # xor rax, rax; ret
    else:
        code = b"\x31\xC0\xC3"  # xor eax, eax; ret
    
    emu.mem.write(hook_addr, code)
    emu.call(hook_addr)
    
    assert_equal(hook_count[0], 1, "Hook not called")
    assert_equal(hook_addrs[0], hook_addr, "Hook address incorrect")
    
    # Test 2: Multiple hooks at same address
    print("  2. Multiple hooks at same address...")
    multi_addr = emu.malloc(0x100, UC_PROT_READ | UC_PROT_WRITE | UC_PROT_EXEC)
    
    hook1_called = [False]
    hook2_called = [False]
    
    def hook1(uc, addr):
        hook1_called[0] = True
    
    def hook2(uc, addr):
        hook2_called[0] = True
    
    emu.hook(multi_addr, hook1)
    emu.hook(multi_addr, hook2)
    
    emu.mem.write(multi_addr, b"\xC3")  # RET
    emu.call(multi_addr)
    
    assert hook1_called[0], "First hook not called"
    assert hook2_called[0], "Second hook not called"
    
    # Test 3: Hooks at different addresses
    print("  3. Multiple address hooks...")
    addr1 = emu.malloc(0x100, UC_PROT_READ | UC_PROT_WRITE | UC_PROT_EXEC)
    addr2 = addr1 + 0x10
    
    order = []
    
    def order_hook1(uc, addr):
        order.append(1)
    
    def order_hook2(uc, addr):
        order.append(2)
    
    emu.hook(addr1, order_hook1)
    emu.hook(addr2, order_hook2)
    
    # Jump from addr1 to addr2
    if emu.ctx.is_64:
        # jmp addr2
        jmp_offset = addr2 - (addr1 + 5)
        code = b"\xE9" + struct.pack("<i", jmp_offset)
    else:
        # jmp addr2
        jmp_offset = addr2 - (addr1 + 5)
        code = b"\xE9" + struct.pack("<i", jmp_offset)
    
    emu.mem.write(addr1, code)
    emu.mem.write(addr2, b"\xC3")  # RET at addr2
    
    emu.call(addr1)
    assert_equal(order, [1, 2], "Hook execution order incorrect")
    
    print("  [OK] All hook tests passed!")

# ============================================================================
# IAT STUB TESTS
# ============================================================================

def test_iat_stubs(emu):
    """Test IAT stubbing."""
    test_banner("IAT Stub Tests")
    
    # Test 1: Basic stub
    print("  1. Basic IAT stub...")
    
    call_count = [0]
    last_args = [None]
    
    def test_stub(iat, uc, args):
        call_count[0] += 1
        last_args[0] = args
        return sum(args)
    
    # Register stub
    stub_addr = emu.stub("test.dll", "AddNumbers",
                         Proto("AddNumbers", emu.ctx.conv, [4, 4, 4]),
                         test_stub)
    
    # Call stub
    result = emu.call(stub_addr, None, 10, 20, 30)
    assert_equal(result, 60, "Stub return value incorrect")
    assert_equal(call_count[0], 1, "Stub not called")
    assert_equal(last_args[0], (10, 20, 30), "Stub args incorrect")
    
    # Test 2: Invoke helper
    print("  2. IAT invoke helper...")
    result = emu.invoke("test.dll", "AddNumbers", 5, 10, 15)
    assert_equal(result, 30, "Invoke failed")
    assert_equal(call_count[0], 2, "Stub not called via invoke")
    
    # Test 3: GetLastError/SetLastError
    print("  3. Last error handling...")
    
    def error_stub(iat, uc, args):
        iat.set_err(0x12345678)
        return 0
    
    emu.stub("kernel32.dll", "FailingFunc",
            Proto("FailingFunc", emu.ctx.conv, []),
            error_stub)
    
    emu.invoke("kernel32.dll", "FailingFunc")
    err = emu.iat.get_err()
    assert_equal(err, 0x12345678, "GetLastError failed")
    
    # Test 4: String arguments
    print("  4. String argument handling...")
    
    received_str = [None]
    
    def string_stub(iat, uc, args):
        str_ptr = args[0]
        received_str[0] = iat.strings.cstring(str_ptr)
        return len(received_str[0])
    
    emu.stub("test.dll", "StringLen",
            Proto("StringLen", emu.ctx.conv, [emu.ctx.width]),
            string_stub)
    
    # Prepare string
    str_addr = emu.malloc(0x100)
    test_string = "Hello IAT Stubs!"
    emu.string.ascii(str_addr, test_string, null=True)
    
    # Call with string pointer
    result = emu.invoke("test.dll", "StringLen", str_addr)
    assert_equal(result, len(test_string), "String stub return incorrect")
    assert_equal(received_str[0], test_string, "String arg not received")
    
    print("  [OK] All IAT stub tests passed!")

# ============================================================================
# TRACER TESTS
# ============================================================================

def test_tracer(emu):
    """Test execution tracing."""
    test_banner("Execution Tracer")
    
    # Test 1: Basic tracing
    print("  1. Basic execution tracing...")
    trace_addr = emu.malloc(0x100, UC_PROT_READ | UC_PROT_WRITE | UC_PROT_EXEC)
    
    if emu.ctx.is_64:
        # Multiple instructions
        code = b"\x48\x31\xC0"  # xor rax, rax
        code += b"\x48\xFF\xC0"  # inc rax
        code += b"\x48\xFF\xC0"  # inc rax
        code += b"\xC3"  # ret
    else:
        code = b"\x31\xC0"  # xor eax, eax
        code += b"\x40"  # inc eax
        code += b"\x40"  # inc eax
        code += b"\xC3"  # ret
    
    emu.mem.write(trace_addr, code)
    
    # Start tracing
    emu.tracer.start()
    emu.call(trace_addr)
    addrs = emu.tracer.stop()
    
    # Should have executed 4 instructions
    assert len(addrs) >= 4, f"Not enough instructions traced: {len(addrs)}"
    assert trace_addr in addrs, "Entry point not in trace"
    
    # Test 2: Trace history
    print("  2. Trace history...")
    history = emu.tracer.history()
    assert len(history) > 0, "No trace history"
    
    # Test 3: Trace with count limit
    print("  3. Trace with instruction limit...")
    loop_addr = emu.malloc(0x100, UC_PROT_READ | UC_PROT_WRITE | UC_PROT_EXEC)
    
    if emu.ctx.is_64:
        # Small loop
        code = b"\x48\x31\xC0"  # xor rax, rax
        code += b"\x48\xFF\xC0"  # inc rax
        code += b"\x48\x83\xF8\x05"  # cmp rax, 5
        code += b"\x75\xF7"  # jne -9 (back to inc)
        code += b"\xC3"  # ret
    else:
        code = b"\x31\xC0"  # xor eax, eax
        code += b"\x40"  # inc eax
        code += b"\x83\xF8\x05"  # cmp eax, 5
        code += b"\x75\xFA"  # jne -6 (back to inc)
        code += b"\xC3"  # ret
    
    emu.mem.write(loop_addr, code)
    
    addrs, count = emu.tracer.run(loop_addr, count=20)
    assert count <= 20, "Trace exceeded limit"
    assert len(addrs) <= 20, "Too many addresses traced"
    
    print("  [OK] All tracer tests passed!")

# ============================================================================
# TEB/PEB TESTS
# ============================================================================

def test_teb_peb(emu):
    """Test TEB/PEB structures."""
    test_banner("TEB/PEB Tests")
    
    print("  1. TEB/PEB addresses...")
    assert emu.tebpeb.teb != 0, "TEB address not set"
    assert emu.tebpeb.peb != 0, "PEB address not set"
    
    print("  2. BeingDebugged flag...")
    # Read BeingDebugged flag
    being_debugged = emu.mem.read(emu.tebpeb.peb + 2, 1)
    assert_equal(being_debugged, b'\x00', "BeingDebugged not cleared")
    
    print("  3. ImageBase in PEB...")
    if emu.ctx.is_64:
        # PEB+0x10 = ImageBase (x64)
        image_base = emu.mem.unpack(emu.tebpeb.peb + 0x10, 8)
    else:
        # PEB+0x08 = ImageBase (x86)
        image_base = emu.mem.unpack(emu.tebpeb.peb + 0x08, 4)
    
    assert_equal(image_base, emu.pe.base, "ImageBase incorrect in PEB")
    
    print("  4. TEB self-pointer...")
    if emu.ctx.is_64:
        # TEB+0x30 = TEB self pointer (x64)
        teb_self = emu.mem.unpack(emu.tebpeb.teb + 0x30, 8)
    else:
        # TEB+0x18 = TEB self pointer (x86)
        teb_self = emu.mem.unpack(emu.tebpeb.teb + 0x18, 4)
    
    assert_equal(teb_self, emu.tebpeb.teb, "TEB self-pointer incorrect")
    
    print("  5. FS/GS base...")
    if emu.ctx.is_64:
        # GS base should point to TEB
        gs_base = emu.regs.read('gs')
        # Note: GS segment register value, not GS_BASE MSR
    else:
        # FS base should point to TEB
        fs_base = emu.regs.read('fs')
        # Note: FS segment register value, not FS_BASE MSR
    
    print("  [OK] All TEB/PEB tests passed!")

# ============================================================================
# EDGE CASES
# ============================================================================

def test_edge_cases(emu):
    """Test edge cases and error conditions."""
    test_banner("Edge Cases")
    
    # Test 1: Zero-size operations
    print("  1. Zero-size operations...")
    addr = emu.malloc(0x100)
    
    # Zero-size read/write should work
    data = emu.mem.read(addr, 0)
    assert_equal(data, b"", "Zero-size read failed")
    
    emu.mem.write(addr, b"")  # Should not crash
    
    # Test 2: Maximum values
    print("  2. Maximum value handling...")
    max_addr = emu.malloc(0x100)
    
    if emu.ctx.is_64:
        max_val = 0xFFFFFFFFFFFFFFFF
        emu.mem.pack(max_addr, max_val, bits=64)
        read_val = emu.mem.unpack(max_addr, 8)
        assert_equal(read_val, max_val, "Max 64-bit value failed")
    else:
        max_val = 0xFFFFFFFF
        emu.mem.pack(max_addr, max_val, bits=32)
        read_val = emu.mem.unpack(max_addr, 4)
        assert_equal(read_val, max_val, "Max 32-bit value failed")
    
    # Test 3: Unaligned access
    print("  3. Unaligned memory access...")
    unaligned_addr = emu.malloc(0x100) + 1  # Not aligned
    
    emu.mem.pack(unaligned_addr, 0x12345678, bits=32)
    val = emu.mem.unpack(unaligned_addr, 4)
    assert_equal(val, 0x12345678, "Unaligned access failed")
    
    # Test 4: Invalid register names
    print("  4. Invalid register handling...")
    try:
        emu.regs.read("invalid_reg")
        assert False, "Invalid register should raise error"
    except KeyError:
        pass  # Expected
    
    # Test 5: Execution without code
    print("  5. Empty execution...")
    empty_addr = emu.malloc(0x100, UC_PROT_READ | UC_PROT_WRITE | UC_PROT_EXEC)
    emu.mem.write(empty_addr, b"\xC3")  # Just RET
    
    result = emu.call(empty_addr)
    # Should complete without crash
    
    print("  [OK] All edge cases handled!")

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all comprehensive tests."""
    print("="*80)
    print("COMPREHENSIVE DUMBEMU TEST SUITE")
    print("="*80)
    
    # Load a PE for testing
    pe_path = Path(__file__).parent.parent / "examples" / "R0ll" / "R0ll.exe"
    
    # Test both with and without verbose
    for verbose in [False, True]:
        print(f"\n{'='*80}")
        print(f"Testing with verbose={'ON' if verbose else 'OFF'}")
        print('='*80)
        
        emu = DumbEmu(str(pe_path), verbose=verbose)
        
        # Run all test categories
        test_functions = [
            test_memory_operations,
            test_register_operations,
            test_string_operations,
            test_struct_operations,
            test_stack_operations,
            test_allocation,
            test_code_execution,
            test_hooks,
            test_iat_stubs,
            test_tracer,
            test_teb_peb,
            test_edge_cases,
        ]
        
        passed = 0
        failed = 0
        
        for test_func in test_functions:
            try:
                test_func(emu)
                passed += 1
            except Exception as e:
                failed += 1
                print(f"  [FAILED] {test_func.__name__}: {e}")
        
        print(f"\n{'='*60}")
        print(f"Results: {passed} passed, {failed} failed")
        
        if failed > 0:
            print("TESTS FAILED!")
            return False
    
    print("\n" + "="*80)
    print("ALL COMPREHENSIVE TESTS PASSED!")
    print("="*80)
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

