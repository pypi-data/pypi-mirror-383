"""Model layer for Vera Syntaxis GUI."""

from vera_syntaxis.gui.model.analysis_model import AnalysisModel, AnalysisStatus, AnalysisResult
from vera_syntaxis.gui.model.report_generator import ReportGenerator
from vera_syntaxis.gui.model.preferences import PreferencesManager

__all__ = [
    'AnalysisModel',
    'AnalysisStatus', 
    'AnalysisResult',
    'ReportGenerator',
    'PreferencesManager'
]
