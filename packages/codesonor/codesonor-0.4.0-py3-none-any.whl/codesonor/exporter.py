"""
Export functionality for CodeSonor analysis results.
Supports JSON, HTML, and Markdown export formats.
"""

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class ExportManager:
    """Handles exporting analysis results to various formats."""
    
    def __init__(self):
        self.supported_formats = ['json', 'html', 'markdown', 'md']
    
    def export(self, data: Dict[str, Any], output_path: Path, format: str = 'json'):
        """
        Export analysis data to specified format.
        
        Args:
            data: Analysis data to export
            output_path: Output file path
            format: Export format (json, html, markdown)
        """
        format = format.lower()
        
        if format not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format}. Supported: {', '.join(self.supported_formats)}")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'json':
            self._export_json(data, output_path)
        elif format == 'html':
            self._export_html(data, output_path)
        elif format in ['markdown', 'md']:
            self._export_markdown(data, output_path)
    
    def _export_json(self, data: Dict[str, Any], output_path: Path):
        """Export as JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _export_markdown(self, data: Dict[str, Any], output_path: Path):
        """Export as Markdown."""
        md_content = self._generate_markdown(data)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def _export_html(self, data: Dict[str, Any], output_path: Path):
        """Export as HTML."""
        html_content = self._generate_html(data)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_markdown(self, data: Dict[str, Any]) -> str:
        """Generate Markdown report."""
        lines = []
        
        # Header
        lines.append(f"# CodeSonor Analysis Report")
        lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Repository Info
        if 'repo_name' in data:
            lines.append(f"## Repository: {data['repo_name']}\n")
        
        # Quality Score
        if 'quality_score' in data:
            score_data = data['quality_score']
            lines.append(f"## Quality Score\n")
            lines.append(f"**Overall Score:** {score_data.get('overall_score', 'N/A')}/100 "
                        f"(Grade: {score_data.get('grade', 'N/A')})\n")
            
            # Component Scores
            if 'component_scores' in score_data:
                lines.append("### Component Scores\n")
                for component, score in score_data['component_scores'].items():
                    lines.append(f"- **{component.replace('_', ' ').title()}:** {score:.1f}/100")
                lines.append("")
            
            # Recommendations
            if 'recommendations' in score_data and score_data['recommendations']:
                lines.append("### Recommendations\n")
                for rec in score_data['recommendations']:
                    lines.append(f"- {rec}")
                lines.append("")
        
        # Languages
        if 'languages' in data:
            lines.append("## Language Distribution\n")
            for lang, percentage in sorted(data['languages'].items(), key=lambda x: x[1], reverse=True):
                lines.append(f"- **{lang}:** {percentage}%")
            lines.append("")
        
        # Structure
        if 'structure' in data:
            lines.append("## Repository Structure\n")
            for item in data['structure'][:20]:  # Limit to top 20
                lines.append(f"- {item}")
            if len(data['structure']) > 20:
                lines.append(f"- ... and {len(data['structure']) - 20} more")
            lines.append("")
        
        # Metrics
        if 'total_files' in data or 'total_lines' in data:
            lines.append("## Metrics\n")
            if 'total_files' in data:
                lines.append(f"- **Total Files:** {data['total_files']}")
            if 'total_lines' in data:
                lines.append(f"- **Total Lines:** {data['total_lines']:,}")
            lines.append("")
        
        # AI Summary
        if 'ai_summary' in data:
            lines.append("## AI Analysis\n")
            lines.append(data['ai_summary'])
            lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_html(self, data: Dict[str, Any]) -> str:
        """Generate HTML report."""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeSonor Analysis Report</title>
    <style>
        :root {{
            --primary-color: #2563eb;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
            --bg-color: #f9fafb;
            --card-bg: #ffffff;
            --text-color: #1f2937;
            --border-color: #e5e7eb;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        header {{
            background: linear-gradient(135deg, var(--primary-color), #3b82f6);
            color: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .timestamp {{
            opacity: 0.9;
            font-size: 0.95em;
        }}
        
        .card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border: 1px solid var(--border-color);
        }}
        
        .card h2 {{
            color: var(--primary-color);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--border-color);
        }}
        
        .score-card {{
            text-align: center;
            padding: 30px;
        }}
        
        .score-circle {{
            display: inline-block;
            width: 200px;
            height: 200px;
            border-radius: 50%;
            background: conic-gradient(var(--primary-color) calc(var(--score) * 1%), var(--border-color) 0);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 20px auto;
            position: relative;
        }}
        
        .score-inner {{
            width: 170px;
            height: 170px;
            background: white;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}
        
        .score-value {{
            font-size: 3em;
            font-weight: bold;
            color: var(--primary-color);
        }}
        
        .score-grade {{
            font-size: 1.5em;
            color: #6b7280;
        }}
        
        .component-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .component-item {{
            background: var(--bg-color);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid var(--primary-color);
        }}
        
        .component-name {{
            font-weight: 600;
            margin-bottom: 5px;
            text-transform: capitalize;
        }}
        
        .component-score {{
            font-size: 1.5em;
            color: var(--primary-color);
        }}
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: var(--border-color);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 8px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: var(--primary-color);
            transition: width 0.3s;
        }}
        
        .language-list {{
            list-style: none;
        }}
        
        .language-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .language-item:last-child {{
            border-bottom: none;
        }}
        
        .language-name {{
            font-weight: 500;
        }}
        
        .language-percentage {{
            background: var(--primary-color);
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.9em;
        }}
        
        .recommendations {{
            list-style: none;
        }}
        
        .recommendation {{
            padding: 12px;
            margin-bottom: 10px;
            background: #fef3c7;
            border-left: 4px solid var(--warning-color);
            border-radius: 4px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }}
        
        .metric-box {{
            text-align: center;
            padding: 20px;
            background: var(--bg-color);
            border-radius: 8px;
        }}
        
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: var(--primary-color);
        }}
        
        .metric-label {{
            color: #6b7280;
            margin-top: 5px;
        }}
        
        .summary-text {{
            line-height: 1.8;
            padding: 20px;
            background: var(--bg-color);
            border-radius: 8px;
            white-space: pre-wrap;
        }}
        
        footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #6b7280;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 CodeSonor Analysis Report</h1>
            <div class="timestamp">Generated: {timestamp}</div>
            {repo_name}
        </header>
        
        {quality_section}
        
        {languages_section}
        
        {metrics_section}
        
        {summary_section}
        
        <footer>
            Generated by <strong>CodeSonor</strong> - AI-Powered Repository Analysis
        </footer>
    </div>
</body>
</html>
"""
        
        # Build sections
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        repo_name = f"<h2>{data.get('repo_name', 'Unknown Repository')}</h2>" if 'repo_name' in data else ""
        
        # Quality section
        quality_section = ""
        if 'quality_score' in data:
            score_data = data['quality_score']
            overall_score = score_data.get('overall_score', 0)
            grade = score_data.get('grade', 'N/A')
            
            components_html = ""
            if 'component_scores' in score_data:
                for component, score in score_data['component_scores'].items():
                    components_html += f"""
                    <div class="component-item">
                        <div class="component-name">{component.replace('_', ' ')}</div>
                        <div class="component-score">{score:.1f}</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {score}%"></div>
                        </div>
                    </div>
                    """
            
            recommendations_html = ""
            if 'recommendations' in score_data and score_data['recommendations']:
                recommendations_html = "<ul class='recommendations'>"
                for rec in score_data['recommendations']:
                    recommendations_html += f"<li class='recommendation'>{rec}</li>"
                recommendations_html += "</ul>"
            
            quality_section = f"""
            <div class="card score-card" style="--score: {overall_score}">
                <h2>Quality Score</h2>
                <div class="score-circle">
                    <div class="score-inner">
                        <div class="score-value">{overall_score}</div>
                        <div class="score-grade">Grade: {grade}</div>
                    </div>
                </div>
                <div class="component-grid">
                    {components_html}
                </div>
                {recommendations_html}
            </div>
            """
        
        # Languages section
        languages_section = ""
        if 'languages' in data:
            lang_items = ""
            for lang, percentage in sorted(data['languages'].items(), key=lambda x: x[1], reverse=True):
                lang_items += f"""
                <li class="language-item">
                    <span class="language-name">{lang}</span>
                    <span class="language-percentage">{percentage}%</span>
                </li>
                """
            
            languages_section = f"""
            <div class="card">
                <h2>Language Distribution</h2>
                <ul class="language-list">
                    {lang_items}
                </ul>
            </div>
            """
        
        # Metrics section
        metrics_section = ""
        if 'total_files' in data or 'total_lines' in data:
            metrics_html = ""
            if 'total_files' in data:
                metrics_html += f"""
                <div class="metric-box">
                    <div class="metric-value">{data['total_files']}</div>
                    <div class="metric-label">Total Files</div>
                </div>
                """
            if 'total_lines' in data:
                metrics_html += f"""
                <div class="metric-box">
                    <div class="metric-value">{data['total_lines']:,}</div>
                    <div class="metric-label">Total Lines</div>
                </div>
                """
            
            metrics_section = f"""
            <div class="card">
                <h2>Metrics</h2>
                <div class="metrics-grid">
                    {metrics_html}
                </div>
            </div>
            """
        
        # Summary section
        summary_section = ""
        if 'ai_summary' in data:
            summary_section = f"""
            <div class="card">
                <h2>AI Analysis</h2>
                <div class="summary-text">{data['ai_summary']}</div>
            </div>
            """
        
        return html_template.format(
            timestamp=timestamp,
            repo_name=repo_name,
            quality_section=quality_section,
            languages_section=languages_section,
            metrics_section=metrics_section,
            summary_section=summary_section
        )
