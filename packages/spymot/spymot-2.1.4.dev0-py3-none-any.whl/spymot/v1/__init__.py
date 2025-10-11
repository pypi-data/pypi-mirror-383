"""
Spymot V1: Original foundational protein motif detection system.

This module provides access to the original Spymot functionality including:
- Basic motif detection
- AlphaFold integration
- Simple CLI interface
- Core motif database
"""

# Import V1 modules from the actual V1 directory
import sys
from pathlib import Path

# Add V1 directory to path for imports
v1_path = Path(__file__).parent.parent.parent.parent / "V1"
if str(v1_path) not in sys.path:
    sys.path.insert(0, str(v1_path))

try:
    # Import V1 modules
    from spymot.analyzer import analyze_sequence, analyze_by_pdb
    from spymot.motifs import scan_motifs, get_motif_statistics
    from spymot.targeting import predict_targeting
    from spymot.afdb import get_prediction_meta, fetch_pdb_text, mean_plddt_over_region
    from spymot.utils import read_fasta, validate_sequence
    from spymot.cli import main as cli_main, interactive
    
    __all__ = [
        "analyze_sequence",
        "analyze_by_pdb",
        "scan_motifs", 
        "get_motif_statistics",
        "predict_targeting",
        "get_prediction_meta",
        "fetch_pdb_text",
        "mean_plddt_over_region",
        "read_fasta",
        "validate_sequence",
        "cli_main",
        "interactive"
    ]
    
    V1_AVAILABLE = True
    
except ImportError as e:
    # V1 not available
    __all__ = []
    V1_AVAILABLE = False
    V1_ERROR = str(e)
