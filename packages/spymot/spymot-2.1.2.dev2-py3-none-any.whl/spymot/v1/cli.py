"""
V1 CLI wrapper for original Spymot functionality.
"""

import sys
from pathlib import Path

# Add V1 directory to path
v1_path = Path(__file__).parent.parent.parent.parent.parent / "V1"
if str(v1_path) not in sys.path:
    sys.path.insert(0, str(v1_path))

def main():
    """Main entry point for V1 CLI."""
    try:
        from spymot.cli import main as v1_main
        v1_main()
    except ImportError as e:
        print(f"❌ Error: V1 CLI not available: {e}", file=sys.stderr)
        sys.exit(1)

def interactive():
    """Interactive mode for V1."""
    try:
        from spymot.cli import interactive as v1_interactive
        v1_interactive()
    except ImportError as e:
        print(f"❌ Error: V1 interactive mode not available: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
