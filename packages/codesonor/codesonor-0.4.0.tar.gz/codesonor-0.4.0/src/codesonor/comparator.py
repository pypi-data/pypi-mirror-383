"""
Repository comparison module for CodeSonor.
Enables side-by-side comparison of two repositories.
"""

from typing import Dict, Any, List, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich import box


class RepositoryComparator:
    """Compares two repositories and generates comparison reports."""
    
    def __init__(self):
        self.console = Console()
    
    def compare(self, repo1_data: Dict[str, Any], repo2_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two repositories and return comparison results.
        
        Args:
            repo1_data: Analysis data for first repository
            repo2_data: Analysis data for second repository
            
        Returns:
            Dictionary containing comparison metrics and insights
        """
        comparison = {
            'repo1': repo1_data.get('repo_name', 'Repository 1'),
            'repo2': repo2_data.get('repo_name', 'Repository 2'),
            'languages': self._compare_languages(repo1_data, repo2_data),
            'structure': self._compare_structure(repo1_data, repo2_data),
            'metrics': self._compare_metrics(repo1_data, repo2_data),
            'summary': self._generate_comparison_summary(repo1_data, repo2_data)
        }
        
        return comparison
    
    def _compare_languages(self, repo1: Dict, repo2: Dict) -> Dict[str, Any]:
        """Compare language distributions between repositories."""
        lang1 = repo1.get('languages', {})
        lang2 = repo2.get('languages', {})
        
        all_languages = set(list(lang1.keys()) + list(lang2.keys()))
        
        comparison = {}
        for lang in all_languages:
            comparison[lang] = {
                'repo1': lang1.get(lang, 0),
                'repo2': lang2.get(lang, 0),
                'difference': lang2.get(lang, 0) - lang1.get(lang, 0)
            }
        
        return comparison
    
    def _compare_structure(self, repo1: Dict, repo2: Dict) -> Dict[str, Any]:
        """Compare repository structures."""
        return {
            'total_files': {
                'repo1': repo1.get('total_files', 0),
                'repo2': repo2.get('total_files', 0),
                'difference': repo2.get('total_files', 0) - repo1.get('total_files', 0)
            },
            'total_lines': {
                'repo1': repo1.get('total_lines', 0),
                'repo2': repo2.get('total_lines', 0),
                'difference': repo2.get('total_lines', 0) - repo1.get('total_lines', 0)
            },
            'directories': {
                'repo1': len(repo1.get('structure', [])),
                'repo2': len(repo2.get('structure', [])),
                'difference': len(repo2.get('structure', [])) - len(repo1.get('structure', []))
            }
        }
    
    def _compare_metrics(self, repo1: Dict, repo2: Dict) -> Dict[str, Any]:
        """Compare code metrics between repositories."""
        metrics1 = repo1.get('metrics', {})
        metrics2 = repo2.get('metrics', {})
        
        return {
            'complexity': {
                'repo1': metrics1.get('complexity', 0),
                'repo2': metrics2.get('complexity', 0),
                'difference': metrics2.get('complexity', 0) - metrics1.get('complexity', 0)
            },
            'quality_score': {
                'repo1': metrics1.get('quality_score', 0),
                'repo2': metrics2.get('quality_score', 0),
                'difference': metrics2.get('quality_score', 0) - metrics1.get('quality_score', 0)
            }
        }
    
    def _generate_comparison_summary(self, repo1: Dict, repo2: Dict) -> str:
        """Generate a summary of key differences."""
        summaries = []
        
        # Size comparison
        files1 = repo1.get('total_files', 0)
        files2 = repo2.get('total_files', 0)
        if files1 > files2:
            summaries.append(f"Repository 1 is larger with {files1 - files2} more files")
        elif files2 > files1:
            summaries.append(f"Repository 2 is larger with {files2 - files1} more files")
        else:
            summaries.append("Both repositories have the same number of files")
        
        # Language comparison
        lang1 = set(repo1.get('languages', {}).keys())
        lang2 = set(repo2.get('languages', {}).keys())
        common = lang1 & lang2
        unique1 = lang1 - lang2
        unique2 = lang2 - lang1
        
        if common:
            summaries.append(f"Common languages: {', '.join(common)}")
        if unique1:
            summaries.append(f"Unique to Repository 1: {', '.join(unique1)}")
        if unique2:
            summaries.append(f"Unique to Repository 2: {', '.join(unique2)}")
        
        return "\n".join(summaries)
    
    def display_comparison(self, comparison: Dict[str, Any]):
        """Display comparison results in a formatted table."""
        self.console.print("\n")
        self.console.print(Panel.fit(
            f"[bold cyan]Repository Comparison[/bold cyan]\n"
            f"[yellow]{comparison['repo1']}[/yellow] vs [green]{comparison['repo2']}[/green]",
            border_style="cyan"
        ))
        
        # Structure comparison table
        structure_table = Table(title="Structure Comparison", box=box.ROUNDED)
        structure_table.add_column("Metric", style="cyan")
        structure_table.add_column(comparison['repo1'], style="yellow")
        structure_table.add_column(comparison['repo2'], style="green")
        structure_table.add_column("Difference", style="magenta")
        
        for metric, values in comparison['structure'].items():
            diff = values['difference']
            diff_str = f"+{diff}" if diff > 0 else str(diff)
            structure_table.add_row(
                metric.replace('_', ' ').title(),
                str(values['repo1']),
                str(values['repo2']),
                diff_str
            )
        
        self.console.print(structure_table)
        
        # Language comparison table
        if comparison['languages']:
            lang_table = Table(title="Language Distribution", box=box.ROUNDED)
            lang_table.add_column("Language", style="cyan")
            lang_table.add_column(comparison['repo1'], style="yellow")
            lang_table.add_column(comparison['repo2'], style="green")
            lang_table.add_column("Difference", style="magenta")
            
            for lang, values in sorted(comparison['languages'].items()):
                diff = values['difference']
                diff_str = f"+{diff}%" if diff > 0 else f"{diff}%"
                lang_table.add_row(
                    lang,
                    f"{values['repo1']}%",
                    f"{values['repo2']}%",
                    diff_str
                )
            
            self.console.print("\n")
            self.console.print(lang_table)
        
        # Summary
        self.console.print("\n")
        self.console.print(Panel(
            comparison['summary'],
            title="[bold]Comparison Summary[/bold]",
            border_style="green"
        ))
        self.console.print("\n")
