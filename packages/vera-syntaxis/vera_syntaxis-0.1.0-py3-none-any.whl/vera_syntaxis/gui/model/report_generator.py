"""Report Generator - formats and exports analysis reports."""

from pathlib import Path
from typing import List, Dict
from datetime import datetime

from vera_syntaxis.violations import Violation


class ReportGenerator:
    """Generates formatted reports from analysis results."""
    
    # Rule ID to friendly name mapping
    RULE_NAMES = {
        "TC001": "Direct Instantiation",
        "TC002": "Law of Demeter Violation",
        "TC003": "Excessive Interaction",
        "W2902": "Illegal Layer Dependency (MVBC)",
        "CD001": "Circular Dependency",
        "GO001": "God Object",
        "FE001": "Feature Envy",
        "DC001": "Data Clump"
    }
    
    @staticmethod
    def format_violation_text(violation: Violation, include_colors: bool = False) -> str:
        """
        Format a single violation as text.
        
        Args:
            violation: The violation to format
            include_colors: Whether to include color tags
            
        Returns:
            Formatted violation string
        """
        file_str = str(violation.file_path) if violation.file_path else "unknown"
        line_str = f":{violation.line_number}" if violation.line_number else ""
        
        if include_colors:
            return (f"[{violation.rule_id}] "
                   f"{{file}}{file_str}{line_str}{{/file}} - "
                   f"{{violation}}{violation.message}{{/violation}}")
        else:
            return f"[{violation.rule_id}] {file_str}{line_str} - {violation.message}"
    
    @staticmethod
    def format_violations_by_rule(violations_by_rule: Dict[str, List[Violation]]) -> str:
        """
        Format violations grouped by rule.
        
        Args:
            violations_by_rule: Dictionary mapping rule_id to violations
            
        Returns:
            Formatted report string
        """
        if not violations_by_rule:
            return "No violations found."
        
        report_lines = []
        
        for rule_id in sorted(violations_by_rule.keys()):
            violations = violations_by_rule[rule_id]
            rule_name = ReportGenerator.RULE_NAMES.get(rule_id, rule_id)
            
            report_lines.append(f"\n{rule_name} ({rule_id})")
            report_lines.append("=" * 80)
            report_lines.append(f"Found {len(violations)} violation(s)\n")
            
            for violation in violations:
                report_lines.append(ReportGenerator.format_violation_text(violation))
            
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    @staticmethod
    def export_to_markdown(violations_by_rule: Dict[str, List[Violation]], 
                          output_path: Path,
                          project_path: Path = None) -> bool:
        """
        Export violations to a Markdown file.
        
        Args:
            violations_by_rule: Dictionary mapping rule_id to violations
            output_path: Path to save the Markdown file
            project_path: Optional project path for context
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # Header
                f.write("# Vera Syntaxis Analysis Report\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                if project_path:
                    f.write(f"**Project:** `{project_path}`\n\n")
                
                # Summary
                total_violations = sum(len(v) for v in violations_by_rule.values())
                f.write(f"**Total Violations:** {total_violations}\n\n")
                f.write("---\n\n")
                
                # Violations by rule
                if not violations_by_rule:
                    f.write("No violations found. Well done!\n")
                else:
                    for rule_id in sorted(violations_by_rule.keys()):
                        violations = violations_by_rule[rule_id]
                        rule_name = ReportGenerator.RULE_NAMES.get(rule_id, rule_id)
                        
                        f.write(f"## {rule_name} ({rule_id})\n\n")
                        f.write(f"**Count:** {len(violations)}\n\n")
                        
                        for i, violation in enumerate(violations, 1):
                            file_str = str(violation.file_path) if violation.file_path else "unknown"
                            line_str = f":{violation.line_number}" if violation.line_number else ""
                            
                            f.write(f"{i}. **Location:** `{file_str}{line_str}`\n")
                            f.write(f"   \n")
                            f.write(f"   {violation.message}\n\n")
                        
                        f.write("---\n\n")
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def format_summary(file_count: int, violations_by_rule: Dict[str, List[Violation]]) -> str:
        """
        Format a summary of the analysis.
        
        Args:
            file_count: Number of files analyzed
            violations_by_rule: Dictionary mapping rule_id to violations
            
        Returns:
            Formatted summary string
        """
        total_violations = sum(len(v) for v in violations_by_rule.values())
        
        summary_lines = [
            "Analysis Summary",
            "=" * 80,
            f"Files analyzed: {file_count}",
            f"Total violations: {total_violations}",
            ""
        ]
        
        if violations_by_rule:
            summary_lines.append("Violations by rule:")
            summary_lines.append("-" * 80)
            
            for rule_id in sorted(violations_by_rule.keys()):
                violations = violations_by_rule[rule_id]
                rule_name = ReportGenerator.RULE_NAMES.get(rule_id, rule_id)
                summary_lines.append(f"  {rule_name} ({rule_id}): {len(violations)}")
        else:
            summary_lines.append("No violations found. Well done!")
        
        return "\n".join(summary_lines)
