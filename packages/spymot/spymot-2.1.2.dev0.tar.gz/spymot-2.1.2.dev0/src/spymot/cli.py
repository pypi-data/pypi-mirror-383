"""
Main command-line interface for Spymot package.
Provides unified access to both V1 and V2 functionality.
"""

import click
import sys
from pathlib import Path
from typing import Optional

from ._version import __version__

@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__, '-v', '--version')
def main():
    """
    🧬 Spymot - Advanced Protein Motif Detection with AlphaFold Structural Validation
    
    A comprehensive protein analysis platform for cancer biology research, 
    drug discovery, and functional genomics.
    
    Choose your version:
    • V1: Original foundational system with basic motif detection
    • V2: Enhanced production system with 94.6% motif coverage
    
    Examples:
      spymot v1 analyze protein.fasta --format json
      spymot v2 analyze protein.fasta --database all --cancer-only
      spymot interactive
    """
    pass

@main.group()
def v1():
    """V1: Original Spymot functionality (basic motif detection)"""
    pass

@main.group() 
def v2():
    """V2: Enhanced Spymot functionality (comprehensive analysis)"""
    pass

@main.command()
@click.option('--version', 'version_choice', 
              type=click.Choice(['v1', 'v2']), 
              default='v2',
              help='Choose Spymot version')
def interactive(version_choice: str):
    """Launch interactive analysis mode"""
    try:
        if version_choice == 'v1':
            from .v1.cli import interactive as v1_interactive
            v1_interactive()
        else:
            from .v2.scripts.interactive_cli import main as v2_interactive
            v2_interactive()
    except ImportError as e:
        click.echo(f"❌ Error: {e}", err=True)
        click.echo(f"Make sure {version_choice} is properly installed.", err=True)
        sys.exit(1)

@v1.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('--id', 'uniprot_id', help='UniProt ID hint for structure mapping')
@click.option('-o', '--output', type=click.Path(path_type=Path), help='Output file path')
@click.option('--format', 'output_format', default='json', 
              type=click.Choice(['json', 'yaml', 'txt']), help='Output format')
@click.option('--database', 'motif_db_type', default='all',
              type=click.Choice(['all', 'cancer', 'signals', 'hardcoded']),
              help='Which motif databases to use')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def analyze(input_file: Path, uniprot_id: Optional[str], output: Optional[Path],
           output_format: str, motif_db_type: str, verbose: bool):
    """Analyze protein sequence using V1 functionality"""
    try:
        from .v1.cli import analyze as v1_analyze
        v1_analyze(input_file, uniprot_id, output, output_format, True, False, 0.0, motif_db_type, False, verbose)
    except ImportError as e:
        click.echo(f"❌ Error: V1 functionality not available: {e}", err=True)
        sys.exit(1)

@v1.command()
@click.argument('pdb_id', type=str)
@click.option('-o', '--output', type=click.Path(path_type=Path), help='Output file path')
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'yaml', 'txt']), help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def pdb(pdb_id: str, output: Optional[Path], output_format: str, verbose: bool):
    """Analyze protein by PDB structure ID using V1 functionality"""
    try:
        from .v1.cli import pdb as v1_pdb
        v1_pdb(pdb_id, output, output_format, verbose)
    except ImportError as e:
        click.echo(f"❌ Error: V1 functionality not available: {e}", err=True)
        sys.exit(1)

@v2.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('--id', 'uniprot_id', help='UniProt ID hint for structure mapping')
@click.option('-o', '--output', type=click.Path(path_type=Path), help='Output file path')
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'yaml', 'txt']), help='Output format')
@click.option('--database', 'motif_db_type', default='all',
              type=click.Choice(['all', 'cancer', 'signals', 'hardcoded']),
              help='Which motif databases to use')
@click.option('--cancer-only', is_flag=True, help='Show only cancer-relevant motifs')
@click.option('--min-confidence', type=float, default=0.0,
              help='Minimum confidence threshold (0.0-1.0)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def analyze(input_file: Path, uniprot_id: Optional[str], output: Optional[Path],
           output_format: str, motif_db_type: str, cancer_only: bool,
           min_confidence: float, verbose: bool):
    """Analyze protein sequence using V2 enhanced functionality"""
    try:
        from .v2.scripts.enhanced_cli import analyze as v2_analyze
        v2_analyze(input_file, uniprot_id, output, output_format, motif_db_type, 
                  cancer_only, min_confidence, verbose)
    except ImportError as e:
        click.echo(f"❌ Error: V2 functionality not available: {e}", err=True)
        sys.exit(1)

@v2.command()
@click.option('--format', 'output_format', default='txt',
              type=click.Choice(['json', 'yaml', 'txt']), help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def databases(output_format: str, verbose: bool):
    """Show information about available motif databases (V2)"""
    try:
        from .v2.scripts.enhanced_cli import databases as v2_databases
        v2_databases(output_format, verbose)
    except ImportError as e:
        click.echo(f"❌ Error: V2 functionality not available: {e}", err=True)
        sys.exit(1)

@main.command()
def info():
    """Show package information and version details"""
    from . import get_version_info
    
    info = get_version_info()
    
    click.echo("🧬 SPYMOT PACKAGE INFORMATION")
    click.echo("=" * 50)
    click.echo(f"Version: {info['version']}")
    click.echo(f"Author: {info['author']}")
    click.echo(f"Description: {info['description']}")
    click.echo(f"License: {info['license']}")
    click.echo(f"URL: {info['url']}")
    click.echo()
    click.echo("Available Components:")
    click.echo(f"  • V1 (Original): {'✅ Available' if info['v1_available'] else '❌ Not Available'}")
    click.echo(f"  • V2 (Enhanced): {'✅ Available' if info['v2_available'] else '❌ Not Available'}")
    click.echo()
    click.echo("Usage Examples:")
    click.echo("  spymot v1 analyze protein.fasta --format json")
    click.echo("  spymot v2 analyze protein.fasta --database all --cancer-only")
    click.echo("  spymot interactive --version v2")

if __name__ == '__main__':
    main()
