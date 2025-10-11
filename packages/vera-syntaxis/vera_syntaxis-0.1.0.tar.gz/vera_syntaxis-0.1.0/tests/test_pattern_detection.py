"""Tests for design pattern detection."""

import pytest
import ast
from pathlib import Path
from vera_syntaxis.parser import ASTParser
from vera_syntaxis.symbol_table import SymbolTable, SymbolTableBuilder
from vera_syntaxis.pattern_detectors import FactoryDetector
from vera_syntaxis.linter_base import LinterContext
from vera_syntaxis.config import VeraSyntaxisConfig


@pytest.fixture
def factory_pattern_code(temp_project_dir: Path) -> Path:
    """Create test code with clear Factory pattern opportunity."""
    # Create database module with related classes
    db_module = temp_project_dir / "database.py"
    db_module.write_text("""
class Database:
    '''Base database class.'''
    def connect(self):
        pass

class PostgresDatabase(Database):
    def connect(self):
        print("Connecting to Postgres")

class MySQLDatabase(Database):
    def connect(self):
        print("Connecting to MySQL")

class SQLiteDatabase(Database):
    def connect(self):
        print("Connecting to SQLite")
""", encoding='utf-8')
    
    # Create code that instantiates these classes in multiple places
    app1 = temp_project_dir / "app1.py"
    app1.write_text("""
from database import PostgresDatabase, MySQLDatabase

def process_postgres():
    db = PostgresDatabase()
    db.connect()

def process_mysql():
    db = MySQLDatabase()
    db.connect()
""", encoding='utf-8')
    
    app2 = temp_project_dir / "app2.py"
    app2.write_text("""
from database import PostgresDatabase, SQLiteDatabase

def another_postgres():
    db = PostgresDatabase()
    db.connect()

def process_sqlite():
    db = SQLiteDatabase()
    db.connect()
""", encoding='utf-8')
    
    return temp_project_dir


@pytest.fixture
def linter_context_with_factory(factory_pattern_code: Path):
    """Create LinterContext with Factory pattern code."""
    # Parse files
    parser = ASTParser(factory_pattern_code)
    python_files = list(factory_pattern_code.glob("*.py"))
    parsed_files = parser.parse_files(python_files)
    
    # Build symbol table
    symbol_table = SymbolTable()
    for file_path, parsed_file in parsed_files.items():
        builder = SymbolTableBuilder(file_path, factory_pattern_code, symbol_table)
        builder.visit(parsed_file.ast_root)
    
    # Create context
    config = VeraSyntaxisConfig()
    context = LinterContext(
        config=config,
        parser=parser,
        symbol_table=symbol_table,
        call_graph=None,  # Not needed for Factory detection
        parsed_files=parsed_files
    )
    
    return context


def test_factory_detector_finds_opportunity(linter_context_with_factory):
    """Test that Factory detector identifies clear pattern opportunity."""
    detector = FactoryDetector(linter_context_with_factory)
    opportunities = detector.detect()
    
    # Should find at least one Factory opportunity
    assert len(opportunities) > 0
    
    # Check first opportunity
    opp = opportunities[0]
    assert opp.pattern_name == "Factory Method"
    assert opp.confidence >= 0.6  # At least medium confidence
    assert "Database" in opp.description or "Postgres" in opp.description or "MySQL" in opp.description
    assert opp.benefit  # Should have benefit description
    assert opp.file_path is not None
    assert opp.line_number > 0


def test_factory_detector_confidence_score(linter_context_with_factory):
    """Test that confidence score is calculated correctly."""
    detector = FactoryDetector(linter_context_with_factory)
    opportunities = detector.detect()
    
    assert len(opportunities) > 0
    
    # With 3 classes instantiated 4 times across 2 files, should be high confidence
    opp = opportunities[0]
    assert opp.confidence >= 0.7  # Should be at least 70%


def test_factory_detector_includes_example(linter_context_with_factory):
    """Test that detector provides example refactoring code."""
    detector = FactoryDetector(linter_context_with_factory)
    opportunities = detector.detect()
    
    assert len(opportunities) > 0
    
    opp = opportunities[0]
    assert opp.example_code is not None
    assert "Factory" in opp.example_code
    assert "create" in opp.example_code.lower()


def test_factory_detector_no_false_positive(temp_project_dir: Path):
    """Test that single instantiation doesn't trigger Factory pattern."""
    # Create code with single class usage
    single_use = temp_project_dir / "single.py"
    single_use.write_text("""
class MyClass:
    def method(self):
        pass

def use_class():
    obj = MyClass()
    obj.method()
""", encoding='utf-8')
    
    # Parse and build context
    parser = ASTParser(temp_project_dir)
    parsed_files = parser.parse_files([single_use])
    
    symbol_table = SymbolTable()
    for file_path, parsed_file in parsed_files.items():
        builder = SymbolTableBuilder(file_path, temp_project_dir, symbol_table)
        builder.visit(parsed_file.ast_root)
    
    config = VeraSyntaxisConfig()
    context = LinterContext(
        config=config,
        parser=parser,
        symbol_table=symbol_table,
        call_graph=None,
        parsed_files=parsed_files
    )
    
    # Run detector
    detector = FactoryDetector(context)
    opportunities = detector.detect()
    
    # Should not find Factory opportunity for single class
    assert len(opportunities) == 0


def test_factory_detector_evidence_data(linter_context_with_factory):
    """Test that detector includes evidence data for debugging."""
    detector = FactoryDetector(linter_context_with_factory)
    opportunities = detector.detect()
    
    assert len(opportunities) > 0
    
    opp = opportunities[0]
    assert 'instance_count' in opp.evidence
    assert 'class_count' in opp.evidence
    assert 'file_count' in opp.evidence
    assert opp.evidence['instance_count'] >= 3
    assert opp.evidence['file_count'] >= 2


def test_pattern_detector_integration(factory_pattern_code: Path):
    """Test full pattern detection integration."""
    from vera_syntaxis.pattern_detectors import run_all_detectors
    
    # Parse files
    parser = ASTParser(factory_pattern_code)
    python_files = list(factory_pattern_code.glob("*.py"))
    parsed_files = parser.parse_files(python_files)
    
    # Build symbol table
    symbol_table = SymbolTable()
    for file_path, parsed_file in parsed_files.items():
        builder = SymbolTableBuilder(file_path, factory_pattern_code, symbol_table)
        builder.visit(parsed_file.ast_root)
    
    # Create context
    config = VeraSyntaxisConfig()
    context = LinterContext(
        config=config,
        parser=parser,
        symbol_table=symbol_table,
        call_graph=None,
        parsed_files=parsed_files
    )
    
    # Run all detectors
    opportunities = run_all_detectors(context)
    
    # Should find opportunities
    assert len(opportunities) > 0
    assert any(opp.pattern_name == "Factory Method" for opp in opportunities)


# ============= Strategy Pattern Tests =============

@pytest.fixture
def strategy_pattern_code(temp_project_dir: Path) -> Path:
    """Create test code with Strategy pattern opportunity."""
    code_file = temp_project_dir / "payment.py"
    code_file.write_text("""
def process_payment(payment_method, amount):
    if isinstance(payment_method, CreditCard):
        return payment_method.charge(amount)
    elif isinstance(payment_method, PayPal):
        return payment_method.process(amount)
    elif isinstance(payment_method, BankTransfer):
        return payment_method.transfer(amount)
    elif isinstance(payment_method, Bitcoin):
        return payment_method.send(amount)

def calculate_shipping(method: str):
    if method == "standard":
        return 5.0
    elif method == "express":
        return 10.0
    elif method == "overnight":
        return 20.0
    elif method == "international":
        return 30.0
""", encoding='utf-8')
    
    return temp_project_dir


def test_strategy_detector_isinstance(strategy_pattern_code: Path):
    """Test Strategy detector on isinstance conditionals."""
    from vera_syntaxis.pattern_detectors import StrategyDetector
    
    parser = ASTParser(strategy_pattern_code)
    parsed_files = parser.parse_files(list(strategy_pattern_code.glob("*.py")))
    
    symbol_table = SymbolTable()
    config = VeraSyntaxisConfig()
    context = LinterContext(config, parser, symbol_table, None, parsed_files)
    
    detector = StrategyDetector(context)
    opportunities = detector.detect()
    
    assert len(opportunities) >= 1
    # Check that at least one opportunity has isinstance as condition_type
    has_isinstance = False
    for opp in opportunities:
        if hasattr(opp, 'evidence') and 'condition_type' in opp.evidence:
            if opp.evidence['condition_type'] == 'isinstance':
                has_isinstance = True
                break
    assert has_isinstance


def test_strategy_detector_string_match(strategy_pattern_code: Path):
    """Test Strategy detector on string matching."""
    from vera_syntaxis.pattern_detectors import StrategyDetector
    
    parser = ASTParser(strategy_pattern_code)
    parsed_files = parser.parse_files(list(strategy_pattern_code.glob("*.py")))
    
    symbol_table = SymbolTable()
    config = VeraSyntaxisConfig()
    context = LinterContext(config, parser, symbol_table, None, parsed_files)
    
    detector = StrategyDetector(context)
    opportunities = detector.detect()
    
    assert len(opportunities) >= 1


# ============= Observer Pattern Tests =============

@pytest.fixture
def observer_pattern_code(temp_project_dir: Path) -> Path:
    """Create test code with Observer pattern opportunity."""
    code_file = temp_project_dir / "model.py"
    code_file.write_text("""
class DataModel:
    def __init__(self):
        self.data = []
        self.view1 = View1()
        self.view2 = View2()
        self.logger = Logger()
    
    def update_data(self, new_data):
        self.data = new_data
        self.view1.refresh()
        self.view2.update_display()
        self.logger.log_change()
        self.cache.invalidate()
""", encoding='utf-8')
    
    return temp_project_dir


def test_observer_detector_finds_notifications(observer_pattern_code: Path):
    """Test Observer detector finds notification chains."""
    from vera_syntaxis.pattern_detectors import ObserverDetector
    
    parser = ASTParser(observer_pattern_code)
    parsed_files = parser.parse_files(list(observer_pattern_code.glob("*.py")))
    
    symbol_table = SymbolTable()
    config = VeraSyntaxisConfig()
    context = LinterContext(config, parser, symbol_table, None, parsed_files)
    
    detector = ObserverDetector(context)
    opportunities = detector.detect()
    
    assert len(opportunities) >= 1
    assert opportunities[0].pattern_name == "Observer"


# ============= Singleton Pattern Tests =============

@pytest.fixture
def singleton_pattern_code(temp_project_dir: Path) -> Path:
    """Create test code with Singleton pattern opportunity."""
    code_file = temp_project_dir / "config.py"
    code_file.write_text("""
class ConfigManager:
    def __init__(self):
        self.settings = {}
    
    def get(self, key):
        return self.settings.get(key)

# Multiple instantiations
config1 = ConfigManager()
config2 = ConfigManager()
config3 = ConfigManager()
""", encoding='utf-8')
    
    return temp_project_dir


def test_singleton_detector_multiple_instantiations(singleton_pattern_code: Path):
    """Test Singleton detector finds multiple instantiations."""
    from vera_syntaxis.pattern_detectors import SingletonDetector
    
    parser = ASTParser(singleton_pattern_code)
    parsed_files = parser.parse_files(list(singleton_pattern_code.glob("*.py")))
    
    symbol_table = SymbolTable()
    for file_path, parsed_file in parsed_files.items():
        builder = SymbolTableBuilder(file_path, singleton_pattern_code, symbol_table)
        builder.visit(parsed_file.ast_root)
    
    config = VeraSyntaxisConfig()
    context = LinterContext(config, parser, symbol_table, None, parsed_files)
    
    detector = SingletonDetector(context)
    opportunities = detector.detect()
    
    assert len(opportunities) >= 1
    assert opportunities[0].pattern_name == "Singleton"


# ============= Decorator Pattern Tests =============

@pytest.fixture
def decorator_pattern_code(temp_project_dir: Path) -> Path:
    """Create test code with Decorator pattern opportunity."""
    code_file = temp_project_dir / "wrappers.py"
    code_file.write_text("""
class LoggingDatabase:
    def __init__(self, db):
        self.db = db
    
    def query(self, sql):
        print(f"Query: {sql}")
        return self.db.query(sql)
    
    def connect(self):
        return self.db.connect()

class CachingDatabase:
    def __init__(self, db):
        self.db = db
        self.cache = {}
    
    def query(self, sql):
        if sql in self.cache:
            return self.cache[sql]
        result = self.db.query(sql)
        self.cache[sql] = result
        return result
    
    def connect(self):
        return self.db.connect()
""", encoding='utf-8')
    
    return temp_project_dir


def test_decorator_detector_finds_wrappers(decorator_pattern_code: Path):
    """Test Decorator detector finds wrapper classes."""
    from vera_syntaxis.pattern_detectors import DecoratorPatternDetector
    
    parser = ASTParser(decorator_pattern_code)
    parsed_files = parser.parse_files(list(decorator_pattern_code.glob("*.py")))
    
    symbol_table = SymbolTable()
    config = VeraSyntaxisConfig()
    context = LinterContext(config, parser, symbol_table, None, parsed_files)
    
    detector = DecoratorPatternDetector(context)
    opportunities = detector.detect()
    
    assert len(opportunities) >= 1
    assert opportunities[0].pattern_name == "Decorator"


# ============= Adapter Pattern Tests =============

@pytest.fixture
def adapter_pattern_code(temp_project_dir: Path) -> Path:
    """Create test code with Adapter pattern opportunity."""
    code_file = temp_project_dir / "adapters.py"
    code_file.write_text("""
def translate_to_legacy(modern_data):
    legacy_format = {
        'old_id': modern_data['id'],
        'old_name': modern_data['name'],
        'old_date': modern_data['created_at'],
        'old_status': modern_data['status']
    }
    return external_api.process(legacy_format)

class RequestsClient:
    def fetch(self, url):
        return requests.get(url)

class URLlibClient:
    def fetch(self, url):
        return urllib.request.urlopen(url)
""", encoding='utf-8')
    
    return temp_project_dir


def test_adapter_detector_finds_translation(adapter_pattern_code: Path):
    """Test Adapter detector finds field translation."""
    from vera_syntaxis.pattern_detectors import AdapterDetector
    
    parser = ASTParser(adapter_pattern_code)
    parsed_files = parser.parse_files(list(adapter_pattern_code.glob("*.py")))
    
    symbol_table = SymbolTable()
    config = VeraSyntaxisConfig()
    context = LinterContext(config, parser, symbol_table, None, parsed_files)
    
    detector = AdapterDetector(context)
    opportunities = detector.detect()
    
    assert len(opportunities) >= 1
    assert opportunities[0].pattern_name == "Adapter"


# ============= Integration Test for All Patterns =============

def test_all_pattern_detectors_integration(temp_project_dir: Path):
    """Test that all detectors work together."""
    from vera_syntaxis.pattern_detectors import run_all_detectors
    
    # Create diverse code
    code_file = temp_project_dir / "mixed.py"
    code_file.write_text("""
class Database:
    pass

# Factory opportunity
db1 = PostgresDatabase()
db2 = MySQLDatabase()
db3 = SQLiteDatabase()

# Strategy opportunity
def process(method):
    if method == "a":
        return 1
    elif method == "b":
        return 2
    elif method == "c":
        return 3
""", encoding='utf-8')
    
    parser = ASTParser(temp_project_dir)
    parsed_files = parser.parse_files(list(temp_project_dir.glob("*.py")))
    
    symbol_table = SymbolTable()
    for file_path, parsed_file in parsed_files.items():
        builder = SymbolTableBuilder(file_path, temp_project_dir, symbol_table)
        builder.visit(parsed_file.ast_root)
    
    config = VeraSyntaxisConfig()
    context = LinterContext(config, parser, symbol_table, None, parsed_files)
    
    # Run all detectors
    opportunities = run_all_detectors(context)
    
    # Should return a list (may be empty for this simple code)
    assert isinstance(opportunities, list)
    
    # All opportunities should have required fields
    for opp in opportunities:
        assert hasattr(opp, 'pattern_name')
        assert hasattr(opp, 'confidence')
        assert hasattr(opp, 'description')
        assert 0.0 <= opp.confidence <= 1.0
