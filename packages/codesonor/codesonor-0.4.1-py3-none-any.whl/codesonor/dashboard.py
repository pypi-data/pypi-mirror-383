"""
Interactive terminal dashboard for CodeSonor.
Provides real-time metrics visualization and keyboard navigation.
"""

import time
from typing import Dict, Any, Optional
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from datetime import datetime


class InteractiveDashboard:
    """Interactive terminal dashboard for real-time metrics."""
    
    def __init__(self):
        """Initialize interactive dashboard."""
        self.console = Console()
        self.is_running = False
        self.current_view = 'overview'  # overview, languages, quality, files
        self.data: Optional[Dict[str, Any]] = None
    
    def run(self, analysis_data: Dict[str, Any]):
        """
        Run interactive dashboard.
        
        Args:
            analysis_data: Repository analysis data
        """
        self.data = analysis_data
        self.is_running = True
        
        try:
            with Live(self._generate_layout(), refresh_per_second=4, console=self.console) as live:
                while self.is_running:
                    live.update(self._generate_layout())
                    time.sleep(0.25)
        except KeyboardInterrupt:
            self.is_running = False
            self.console.print("\n👋 Exiting dashboard...")
    
    def _generate_layout(self) -> Layout:
        """Generate dashboard layout."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Header
        layout["header"].update(self._create_header())
        
        # Body
        if self.current_view == 'overview':
            layout["body"].update(self._create_overview())
        elif self.current_view == 'quality':
            layout["body"].update(self._create_quality_view())
        elif self.current_view == 'languages':
            layout["body"].update(self._create_languages_view())
        
        # Footer
        layout["footer"].update(self._create_footer())
        
        return layout
    
    def _create_header(self) -> Panel:
        """Create dashboard header."""
        repo_name = self.data.get('repo_name', 'Unknown Repository') if self.data else 'Loading...'
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        header_text = f"[bold cyan]🔍 CodeSonor Dashboard[/bold cyan] | {repo_name} | {timestamp}"
        
        return Panel(
            header_text,
            style="white on blue",
            box=box.ROUNDED
        )
    
    def _create_footer(self) -> Panel:
        """Create dashboard footer with controls."""
        footer_text = (
            "[yellow]Controls:[/yellow] "
            "[cyan]q[/cyan] Quit | "
            "[cyan]r[/cyan] Refresh | "
            "[cyan]1[/cyan] Overview | "
            "[cyan]2[/cyan] Quality | "
            "[cyan]3[/cyan] Languages"
        )
        
        return Panel(
            footer_text,
            style="white on dark_blue",
            box=box.ROUNDED
        )
    
    def _create_overview(self) -> Layout:
        """Create overview panel."""
        if not self.data:
            return Panel("[yellow]Loading data...[/yellow]")
        
        layout = Layout()
        layout.split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Left panel: Stats
        stats_table = Table(title="Repository Statistics", box=box.ROUNDED, show_header=False)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        if 'total_files' in self.data:
            stats_table.add_row("📁 Total Files", str(self.data['total_files']))
        if 'total_lines' in self.data:
            stats_table.add_row("📝 Total Lines", f"{self.data['total_lines']:,}")
        if 'languages' in self.data:
            stats_table.add_row("🌐 Languages", str(len(self.data['languages'])))
        
        # Quality score
        if 'quality_score' in self.data:
            score = self.data['quality_score'].get('overall_score', 0)
            grade = self.data['quality_score'].get('grade', 'N/A')
            stats_table.add_row("⭐ Quality Score", f"{score}/100 ({grade})")
        
        layout["left"].update(Panel(stats_table, title="Statistics", border_style="cyan"))
        
        # Right panel: Top Languages
        if 'languages' in self.data:
            lang_table = Table(title="Top Languages", box=box.SIMPLE)
            lang_table.add_column("Language", style="yellow")
            lang_table.add_column("Percentage", justify="right", style="green")
            
            sorted_langs = sorted(self.data['languages'].items(), 
                                 key=lambda x: x[1], reverse=True)
            
            for lang, percentage in sorted_langs[:5]:
                lang_table.add_row(lang, f"{percentage}%")
            
            layout["right"].update(Panel(lang_table, title="Languages", border_style="yellow"))
        
        return layout
    
    def _create_quality_view(self) -> Panel:
        """Create quality score detailed view."""
        if not self.data or 'quality_score' not in self.data:
            return Panel("[yellow]No quality score data available[/yellow]")
        
        quality_data = self.data['quality_score']
        
        # Main quality table
        quality_table = Table(title="Quality Score Breakdown", box=box.ROUNDED)
        quality_table.add_column("Component", style="cyan")
        quality_table.add_column("Score", justify="right", style="green")
        quality_table.add_column("Status", justify="center")
        
        # Overall score
        overall_score = quality_data.get('overall_score', 0)
        grade = quality_data.get('grade', 'N/A')
        
        quality_table.add_row(
            "[bold]Overall[/bold]",
            f"[bold]{overall_score}/100[/bold]",
            f"[bold]Grade: {grade}[/bold]"
        )
        
        # Component scores
        if 'component_scores' in quality_data:
            for component, score in quality_data['component_scores'].items():
                status = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
                quality_table.add_row(
                    component.replace('_', ' ').title(),
                    f"{score:.1f}/100",
                    status
                )
        
        content = [quality_table]
        
        # Recommendations
        if 'recommendations' in quality_data and quality_data['recommendations']:
            rec_text = "\n".join(quality_data['recommendations'])
            content.append(f"\n[yellow]Recommendations:[/yellow]\n{rec_text}")
        
        return Panel(
            "\n".join(str(c) for c in content),
            title="Quality Analysis",
            border_style="green"
        )
    
    def _create_languages_view(self) -> Panel:
        """Create languages detailed view."""
        if not self.data or 'languages' not in self.data:
            return Panel("[yellow]No language data available[/yellow]")
        
        lang_table = Table(title="Language Distribution", box=box.ROUNDED)
        lang_table.add_column("#", style="dim", width=4)
        lang_table.add_column("Language", style="cyan")
        lang_table.add_column("Percentage", justify="right", style="yellow")
        lang_table.add_column("Visual", width=30)
        
        sorted_langs = sorted(self.data['languages'].items(), 
                             key=lambda x: x[1], reverse=True)
        
        for idx, (lang, percentage) in enumerate(sorted_langs, 1):
            # Create visual bar
            bar_length = int(percentage / 100 * 30)
            bar = "█" * bar_length + "░" * (30 - bar_length)
            
            lang_table.add_row(
                str(idx),
                lang,
                f"{percentage}%",
                f"[green]{bar}[/green]"
            )
        
        return Panel(
            lang_table,
            title="Language Analysis",
            border_style="yellow"
        )


class DashboardSimple:
    """Simplified dashboard for basic display."""
    
    def __init__(self):
        self.console = Console()
    
    def display(self, data: Dict[str, Any]):
        """
        Display dashboard in simple mode.
        
        Args:
            data: Analysis data to display
        """
        self.console.clear()
        self.console.print("\n")
        
        # Header
        self.console.print(Panel.fit(
            "[bold cyan]🔍 CodeSonor Analysis Dashboard[/bold cyan]",
            border_style="cyan"
        ))
        
        self.console.print("\n")
        
        # Stats
        stats = Table(show_header=False, box=box.SIMPLE)
        stats.add_column("Metric", style="cyan", width=20)
        stats.add_column("Value", style="green")
        
        if 'repo_name' in data:
            stats.add_row("📦 Repository", data['repo_name'])
        if 'total_files' in data:
            stats.add_row("📁 Total Files", str(data['total_files']))
        if 'total_lines' in data:
            stats.add_row("📝 Total Lines", f"{data['total_lines']:,}")
        
        self.console.print(Panel(stats, title="Overview", border_style="cyan"))
        self.console.print("\n")
        
        # Quality Score
        if 'quality_score' in data:
            quality = data['quality_score']
            score = quality.get('overall_score', 0)
            grade = quality.get('grade', 'N/A')
            
            score_text = f"[bold green]{score}/100[/bold green] (Grade: [bold]{grade}[/bold])"
            
            self.console.print(Panel(
                score_text,
                title="⭐ Quality Score",
                border_style="green"
            ))
            self.console.print("\n")
        
        # Languages
        if 'languages' in data:
            lang_table = Table(title="Language Distribution", box=box.ROUNDED)
            lang_table.add_column("Language", style="yellow")
            lang_table.add_column("Percentage", justify="right", style="green")
            lang_table.add_column("Visual", width=25)
            
            sorted_langs = sorted(data['languages'].items(), 
                                 key=lambda x: x[1], reverse=True)
            
            for lang, percentage in sorted_langs:
                bar_length = int(percentage / 100 * 25)
                bar = "█" * bar_length
                
                lang_table.add_row(lang, f"{percentage}%", f"[cyan]{bar}[/cyan]")
            
            self.console.print(lang_table)
        
        self.console.print("\n")
