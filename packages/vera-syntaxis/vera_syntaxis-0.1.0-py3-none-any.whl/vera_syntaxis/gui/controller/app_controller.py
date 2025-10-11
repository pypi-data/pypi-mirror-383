"""Application Controller - coordinates Model and View."""

import threading
from pathlib import Path
from tkinter import filedialog, messagebox

from vera_syntaxis.gui.model.analysis_model import AnalysisModel, AnalysisStatus
from vera_syntaxis.gui.model.report_generator import ReportGenerator
from vera_syntaxis.gui.model.preferences import PreferencesManager
from vera_syntaxis.gui.view.progress_dialog import ProgressDialog


class AppController:
    """Main application controller (MVC Controller)."""
    
    def __init__(self, view):
        """
        Initialize the controller.
        
        Args:
            view: The MainWindow view
        """
        self.view = view
        self.model = AnalysisModel()
        self.report_generator = ReportGenerator()
        self.preferences = PreferencesManager()
        
        self.current_folder = None
        self.analysis_thread = None
        self.progress_dialog = None
        
        # Apply saved preferences
        self._apply_preferences()
    
    def _apply_preferences(self):
        """Apply saved preferences to view."""
        geometry = self.preferences.get_window_geometry()
        self.view.root.geometry(geometry)
        
        # Try to load last folder
        last_folder = self.preferences.get_last_folder()
        if last_folder and last_folder.exists():
            self.current_folder = last_folder
            self.view.status_bar.set_status(f"Last folder: {last_folder}")
            self.view.menu_bar.enable_analyze(True)
            self.view.toolbar.enable_analyze(True)
    
    def on_open_folder(self):
        """Handle open folder action."""
        initial_dir = str(self.current_folder) if self.current_folder else str(Path.home())
        
        folder = filedialog.askdirectory(
            title="Select Project Folder",
            initialdir=initial_dir
        )
        
        if folder:
            folder_path = Path(folder)
            self.current_folder = folder_path
            self.model.set_project_path(folder_path)
            self.preferences.set_last_folder(folder_path)
            
            self.view.status_bar.set_status(f"Selected: {folder_path}")
            self.view.menu_bar.enable_analyze(True)
            self.view.toolbar.enable_analyze(True)
            
            # Clear previous results
            self.view.report_tabs.clear_all_tabs()
            self.view.status_bar.set_file_count(0)
            self.view.status_bar.set_violation_count(0)
    
    def on_analyze(self):
        """Handle analyze action."""
        if not self.current_folder:
            messagebox.showwarning("No Folder", "Please select a folder first.")
            return
        
        # Disable buttons during analysis
        self.view.menu_bar.enable_analyze(False)
        self.view.toolbar.enable_analyze(False)
        
        # Create progress dialog
        self.progress_dialog = ProgressDialog(self.view.root, "Analyzing Project")
        self.progress_dialog.set_cancel_callback(self._on_cancel_analysis)
        
        # Start analysis in background thread
        self.analysis_thread = threading.Thread(target=self._run_analysis, daemon=True)
        self.analysis_thread.start()
        
        # Monitor thread completion
        self.view.root.after(100, self._check_analysis_complete)
    
    def _on_cancel_analysis(self):
        """Handle analysis cancellation."""
        self.model.request_cancel()
    
    def _run_analysis(self):
        """Run analysis in background thread."""
        def progress_callback(status, message, percent):
            if self.progress_dialog:
                self.progress_dialog.update_progress(message, percent)
        
        result = self.model.run_analysis(progress_callback)
        return result
    
    def _check_analysis_complete(self):
        """Check if analysis thread has completed."""
        if self.analysis_thread and self.analysis_thread.is_alive():
            # Still running, check again soon
            self.view.root.after(100, self._check_analysis_complete)
        else:
            # Analysis complete
            self._on_analysis_complete()
    
    def _on_analysis_complete(self):
        """Handle analysis completion."""
        # Close progress dialog
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        # Re-enable buttons
        self.view.menu_bar.enable_analyze(True)
        self.view.toolbar.enable_analyze(True)
        
        result = self.model.result
        
        if result.status == AnalysisStatus.CANCELLED:
            self.view.status_bar.set_status("Analysis cancelled")
            messagebox.showinfo("Cancelled", "Analysis was cancelled.")
            return
        
        if result.status == AnalysisStatus.ERROR:
            self.view.status_bar.set_status(f"Error: {result.error_message}")
            messagebox.showerror("Analysis Error", f"An error occurred:\n{result.error_message}")
            return
        
        # Update status
        self.view.status_bar.set_file_count(result.file_count)
        self.view.status_bar.set_violation_count(len(result.violations))
        self.view.status_bar.set_status(f"Analysis complete: {len(result.violations)} violations found")
        
        # Generate and display reports
        self._update_reports()
        
        # Enable save
        self.view.menu_bar.enable_save_report(True)
        
        messagebox.showinfo("Complete", 
                          f"Analysis complete!\n\n"
                          f"Files: {result.file_count}\n"
                          f"Violations: {len(result.violations)}")
    
    def _update_reports(self):
        """Update all report tabs with results."""
        violations_by_rule = self.model.get_violations_by_rule()
        
        # Update Summary tab
        summary = self.report_generator.format_summary(
            self.model.result.file_count,
            violations_by_rule
        )
        self.view.report_tabs.update_tab("Summary", summary)
        
        # Update Pattern Opportunities tab
        pattern_report = self._format_pattern_opportunities()
        self.view.report_tabs.update_tab("Pattern Opportunities", pattern_report)
        
        # Update individual linter tabs
        for tab_name, rule_ids in self.view.report_tabs.TAB_CONFIG[2:]:  # Skip Summary and Pattern Opportunities
            if not rule_ids:  # Skip tabs with no rule_ids (like Pattern Opportunities)
                continue
                
            tab_violations = {}
            for rule_id in rule_ids:
                if rule_id in violations_by_rule:
                    tab_violations[rule_id] = violations_by_rule[rule_id]
            
            report = self.report_generator.format_violations_by_rule(tab_violations)
            self.view.report_tabs.update_tab(tab_name, report)
    
    def _format_pattern_opportunities(self) -> str:
        """Format pattern opportunities for display."""
        opportunities = self.model.result.pattern_opportunities
        
        if not opportunities:
            return "No pattern opportunities detected.\n\nGood architectural design!"
        
        # Group by pattern type
        by_pattern = {}
        for opp in opportunities:
            pattern_name = opp.pattern_name
            if pattern_name not in by_pattern:
                by_pattern[pattern_name] = []
            by_pattern[pattern_name].append(opp)
        
        # Format output
        lines = [
            "Pattern Opportunities",
            "=" * 80,
            f"Found {len(opportunities)} opportunities to apply design patterns",
            ""
        ]
        
        for pattern_name in sorted(by_pattern.keys()):
            opps = by_pattern[pattern_name]
            lines.append(f"\n{pattern_name} ({len(opps)} opportunities)")
            lines.append("-" * 80)
            
            # Sort by confidence (highest first)
            opps.sort(key=lambda o: o.confidence, reverse=True)
            
            for i, opp in enumerate(opps, 1):
                confidence_pct = int(opp.confidence * 100)
                lines.append(f"\n{i}. {opp.file_path}:{opp.line_number} - Confidence: {confidence_pct}%")
                lines.append(f"   {opp.description}")
                lines.append(f"   Benefit: {opp.benefit}")
                
                if opp.example_code:
                    lines.append(f"\n   Example Refactoring:")
                    for code_line in opp.example_code.split('\n'):
                        lines.append(f"   {code_line}")
                
                lines.append("")
        
        return "\n".join(lines)
    
    def on_save_report(self):
        """Handle save report action."""
        if not self.model.result.violations:
            messagebox.showwarning("No Data", "No analysis results to save.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Report",
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        
        if filename:
            violations_by_rule = self.model.get_violations_by_rule()
            success = self.report_generator.export_to_markdown(
                violations_by_rule,
                Path(filename),
                self.current_folder
            )
            
            if success:
                messagebox.showinfo("Saved", f"Report saved to:\n{filename}")
            else:
                messagebox.showerror("Error", "Failed to save report.")
    
    def on_copy(self):
        """Handle copy action."""
        # Get current tab content and copy to clipboard
        current_tab = self.view.report_tabs.get_current_tab_name()
        text_widget = self.view.report_tabs.text_widgets.get(current_tab)
        
        if text_widget:
            try:
                text = text_widget.get('1.0', 'end-1c')
                self.view.root.clipboard_clear()
                self.view.root.clipboard_append(text)
                self.view.status_bar.set_status("Copied to clipboard")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy: {e}")
    
    def on_filter_changed(self, filter_type: str, filter_text: str):
        """
        Handle filter changes.
        
        Args:
            filter_type: Type of filter ("all", "by file", "by severity")
            filter_text: Filter text
        """
        # TODO: Implement filtering logic
        self.view.status_bar.set_status(f"Filter: {filter_type} - {filter_text}")
    
    def on_edit_config(self):
        """Handle edit configuration action."""
        from vera_syntaxis.gui.view.config_editor import ConfigEditorDialog
        import tomli as toml
        
        # Load current configuration
        current_config = {}
        if self.current_folder:
            config_file = self.current_folder / "pyproject.toml"
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        data = toml.load(f)
                        if "tool" in data and "vera_syntaxis" in data["tool"]:
                            current_config = data["tool"]["vera_syntaxis"]
                except Exception as e:
                    messagebox.showwarning("Config Load Error", 
                                          f"Could not load configuration:\n{e}")
        
        # Show config editor
        editor = ConfigEditorDialog(self.view.root, current_config, self.current_folder)
        result = editor.show()
        
        if result:
            # User saved configuration
            if not self.current_folder:
                messagebox.showinfo("No Project", 
                                   "Please select a project folder first to save configuration.")
                return
            
            # Save to pyproject.toml
            config_file = self.current_folder / "pyproject.toml"
            try:
                # Load existing pyproject.toml or create new
                if config_file.exists():
                    with open(config_file, 'r') as f:
                        data = toml.load(f)
                else:
                    data = {}
                
                # Update vera_syntaxis section
                if "tool" not in data:
                    data["tool"] = {}
                data["tool"]["vera_syntaxis"] = result
                
                # Write back
                with open(config_file, 'w') as f:
                    toml.dump(data, f)
                
                self.view.status_bar.set_status("Configuration saved successfully")
                
                # Ask if user wants to re-run analysis
                if self.model.result.violations:
                    if messagebox.askyesno("Re-run Analysis", 
                                          "Configuration saved. Re-run analysis with new settings?"):
                        self.on_analyze()
                        
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save configuration:\n{e}")
    
    def on_exit(self):
        """Handle exit action."""
        # Save window geometry
        geometry = self.view.root.geometry()
        self.preferences.set_window_geometry(geometry)
        
        self.view.root.quit()
