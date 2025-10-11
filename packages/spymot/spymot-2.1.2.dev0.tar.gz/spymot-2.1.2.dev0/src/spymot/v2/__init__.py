"""
Spymot V2: Enhanced protein motif detection system.

This module provides access to the enhanced Spymot functionality including:
- 94.6% motif coverage (316+ patterns)
- Context-aware detection
- Advanced cancer relevance scoring
- Rich JSON output with biological interpretation
- Production-ready features
"""

# Import V2 modules from the actual V2 directory
import sys
from pathlib import Path

# Add V2 directory to path for imports
v2_path = Path(__file__).parent.parent.parent.parent / "V2"
if str(v2_path) not in sys.path:
    sys.path.insert(0, str(v2_path))

try:
    # Import V2 modules
    from enhanced_analyzer import EnhancedSpymotAnalyzer
    from context_aware_detector import ContextAwareDetector
    from enhanced_motifs_db import EnhancedMotifDatabase
    
    # Import scripts
    from scripts.enhanced_cli import main as enhanced_cli_main
    from scripts.enhanced_demo import main as demo_main
    from scripts.interactive_cli import main as interactive_main
    
    __all__ = [
        "EnhancedSpymotAnalyzer",
        "ContextAwareDetector",
        "EnhancedMotifDatabase",
        "enhanced_cli_main",
        "demo_main", 
        "interactive_main"
    ]
    
    V2_AVAILABLE = True
    
except ImportError as e:
    # V2 not available
    __all__ = []
    V2_AVAILABLE = False
    V2_ERROR = str(e)
