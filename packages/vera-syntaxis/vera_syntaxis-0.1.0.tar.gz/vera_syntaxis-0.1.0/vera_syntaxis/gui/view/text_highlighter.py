"""Text highlighter using Pygments for syntax highlighting."""

import tkinter as tk
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Token


class TextHighlighter:
    """Handles syntax highlighting in tkinter Text widgets using Pygments."""
    
    # Color scheme for violation reports
    COLORS = {
        'rule_id': '#0066CC',      # Blue for rule IDs
        'file_path': '#008000',    # Green for file paths
        'line_number': '#666666',  # Gray for line numbers
        'violation': '#CC0000',    # Red for violation messages
        'keyword': '#0000FF',      # Blue for keywords
        'string': '#008000',       # Green for strings
        'comment': '#808080',      # Gray for comments
        'number': '#FF6600',       # Orange for numbers
        'heading': '#000080',      # Dark blue for headings
        'separator': '#CCCCCC',    # Light gray for separators
    }
    
    @staticmethod
    def configure_text_widget(text_widget: tk.Text):
        """
        Configure a Text widget with highlight tags.
        
        Args:
            text_widget: The Text widget to configure
        """
        # Configure tags for violation report elements
        text_widget.tag_config('rule_id', foreground=TextHighlighter.COLORS['rule_id'], font=('Consolas', 10, 'bold'))
        text_widget.tag_config('file_path', foreground=TextHighlighter.COLORS['file_path'], font=('Consolas', 9))
        text_widget.tag_config('line_number', foreground=TextHighlighter.COLORS['line_number'], font=('Consolas', 9))
        text_widget.tag_config('violation', foreground=TextHighlighter.COLORS['violation'], font=('Arial', 10))
        text_widget.tag_config('heading', foreground=TextHighlighter.COLORS['heading'], font=('Arial', 12, 'bold'))
        text_widget.tag_config('separator', foreground=TextHighlighter.COLORS['separator'])
        
        # Configure tags for Python syntax highlighting
        text_widget.tag_config('keyword', foreground=TextHighlighter.COLORS['keyword'], font=('Consolas', 9, 'bold'))
        text_widget.tag_config('string', foreground=TextHighlighter.COLORS['string'], font=('Consolas', 9))
        text_widget.tag_config('comment', foreground=TextHighlighter.COLORS['comment'], font=('Consolas', 9, 'italic'))
        text_widget.tag_config('number', foreground=TextHighlighter.COLORS['number'], font=('Consolas', 9))
    
    @staticmethod
    def highlight_violation_report(text_widget: tk.Text, text: str):
        """
        Highlight a violation report with syntax coloring.
        
        Args:
            text_widget: The Text widget to insert into
            text: The report text to highlight
        """
        text_widget.delete('1.0', tk.END)
        
        for line in text.split('\n'):
            # Detect and highlight different parts
            if line.startswith('[') and ']' in line:
                # Rule ID line: [TC001] path:line - message
                parts = line.split(']', 1)
                rule_id = parts[0] + ']'
                rest = parts[1] if len(parts) > 1 else ''
                
                text_widget.insert(tk.END, rule_id, 'rule_id')
                
                if ' - ' in rest:
                    location, message = rest.split(' - ', 1)
                    text_widget.insert(tk.END, location, 'file_path')
                    text_widget.insert(tk.END, ' - ')
                    text_widget.insert(tk.END, message, 'violation')
                else:
                    text_widget.insert(tk.END, rest)
                
                text_widget.insert(tk.END, '\n')
                
            elif line.strip().startswith('=') or line.strip().startswith('-'):
                # Separator lines
                text_widget.insert(tk.END, line + '\n', 'separator')
                
            elif line and not line.startswith(' '):
                # Heading lines
                text_widget.insert(tk.END, line + '\n', 'heading')
                
            else:
                # Regular text
                text_widget.insert(tk.END, line + '\n')
        
        text_widget.see('1.0')
