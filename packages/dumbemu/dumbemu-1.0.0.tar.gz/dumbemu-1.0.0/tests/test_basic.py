"""Basic test to verify DumbEmu works without hanging."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dumbemu import DumbEmu
from dumbemu.win.iat import Proto

def main():
    """Run basic test."""
    print("=" * 60)
    print("DumbEmu Basic Test")
    print("=" * 60)
    
    # Load a PE file
    pe_path = Path(__file__).parent.parent / "examples" / "R0ll" / "R0ll.exe"
    if not pe_path.exists():
        print("[FAIL] R0ll.exe not found")
        return False
        
    print(f"\n[TEST] Loading {pe_path.name}")
    emu = DumbEmu(str(pe_path))
    print(f"  [OK] PE loaded, base=0x{emu.pe.base:08X}")
    
    # Test memory
    print("\n[TEST] Memory operations")
    addr = emu.malloc(0x100)
    print(f"  [OK] Allocated at 0x{addr:08X}")
    
    emu.write(addr, b"Hello")
    data = emu.read(addr, 5)
    assert data == b"Hello"
    print(f"  [OK] R/W: {data}")
    
    # Test registers
    print("\n[TEST] Register operations")
    # Use appropriate registers based on architecture
    if emu.ctx.is_64:
        emu.regs.write('rax', 0x1337)
        val = emu.regs.read('rax')
        print(f"  [OK] RAX = 0x{val:04X}")
    else:
        emu.regs.write('eax', 0x1337)
        val = emu.regs.read('eax')
        print(f"  [OK] EAX = 0x{val:04X}")
    
    # Test strings
    print("\n[TEST] String operations")
    str_addr = emu.malloc(0x100)
    emu.string.ascii(str_addr, "Test")
    s = emu.string.cstring(str_addr)
    assert s == "Test"
    print(f"  [OK] ASCII: '{s}'")
    
    emu.string.wide(str_addr, "Wide")
    s = emu.string.wstring(str_addr)
    assert s == "Wide"
    print(f"  [OK] Wide: '{s}'")
    
    # Test simple stub
    print("\n[TEST] IAT stub")
    def my_stub(emu, iat, args):
        print(f"  [OK] Stub called with {len(args)} args")
        return 0x42
    
    stub_addr = emu.stub("test", "func", Proto("test_func", 1, "stdcall"), my_stub)
    print(f"  [OK] Stub registered at 0x{stub_addr:08X}")
    
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
