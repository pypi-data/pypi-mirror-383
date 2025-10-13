# Schema-Lite: Package Requirements Document

## Project Overview

**Package Name:** `schema-lite`  
**Purpose:** Transform verbose Pydantic JSON schemas into lightweight, LLM-friendly formats with support for JSON and YAML output, focusing on token efficiency and improved LLM performance.

**Core Problem:** Standard Pydantic `model_json_schema()` generates overly verbose schemas (815+ tokens) that waste tokens and confuse LLMs. This package reduces schemas by 67-83% while preserving essential type and validation information.

## Technical Requirements

### 1. Core Dependencies
- **Python**: 3.8+
- **Required Dependencies**:
  - `pydantic>=2.0.0` - Core model schema extraction
  - `PyYAML>=6.0` - YAML output support
  - `json-repair>=0.7.0` - Malformed JSON repair
  - `typing-extensions>=4.0.0` - Enhanced type hints for older Python versions

### 2. Package Structure
```
schema-lite/
├── schema_lite/
│   ├── __init__.py          # Main exports
│   ├── core.py              # Core simplification logic
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── json_processor.py    # JSON schema processing
│   │   ├── yaml_processor.py    # YAML format conversion
│   │   └── comment_processor.py # Comment/metadata handling
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── repair.py        # Output repair utilities
│   │   ├── metrics.py       # Token counting and analysis
│   │   └── validators.py    # Schema validation helpers
│   └── exceptions.py        # Custom exceptions
├── tests/
│   ├── test_core.py
│   ├── test_processors.py
│   ├── test_utils.py
│   └── fixtures/
│       └── example_models.py
├── examples/
│   ├── basic_usage.py
│   ├── dspy_integration.py
│   └── performance_comparison.py
├── docs/
│   ├── README.md
│   ├── api_reference.md
│   └── performance_benchmarks.md
├── pyproject.toml
├── README.md
├── LICENSE
└── .github/
    └── workflows/
        └── ci.yml
```

### 3. Core API Design

#### Main Interface
```python
from schema_lite import simplify_schema, SchemaLite

# Primary function
def simplify_schema(
    model: Type[BaseModel], 
    include_metadata: bool = True,
    format_style: Literal["json", "yaml", "hybrid"] = "json",
    comment_style: Literal["//", "#"] = "//",
    optimize_for: Literal["tokens", "readability"] = "tokens"
) -> SchemaLite:
    """
    Convert Pydantic model to simplified schema.
    
    Args:
        model: Pydantic BaseModel class
        include_metadata: Include validation rules as comments
        format_style: Output format preference
        comment_style: Comment syntax style
        optimize_for: Optimization target
        
    Returns:
        SchemaLite object with conversion methods
    """

# SchemaLite class interface
class SchemaLite:
    def to_dict(self) -> Dict[str, Any]: ...
    def to_json(self, indent: int = 2) -> str: ...
    def to_yaml(self, default_flow_style: bool = False) -> str: ...
    def to_string(self) -> str: ...
    def token_count(self) -> int: ...
    def compare_tokens(self, original_schema: Dict) -> Dict[str, int]: ...
```

#### Utility Functions
```python
# Repair utilities
def repair_json_output(text: str) -> Dict[str, Any]: ...
def validate_against_schema(data: Dict, schema: SchemaLite) -> bool: ...

# Metrics and analysis
def analyze_token_efficiency(
    original: Dict, 
    simplified: SchemaLite
) -> Dict[str, Union[int, float]]: ...

def benchmark_schema_performance(
    schemas: List[Type[BaseModel]], 
    test_prompts: List[str]
) -> Dict[str, Any]: ...
```

### 4. Feature Requirements

#### Phase 1 (MVP - v0.1.0)
- [x] **Core Schema Simplification**
  - Transform Pydantic JSON schema to simplified format
  - Support nested objects and arrays
  - Handle primitive types (string, int, float, bool)
  - Preserve enum definitions
  
- [x] **Output Formats**
  - JSON output with inline comments
  - Basic YAML conversion
  - String representation for LLM prompts
  
- [x] **Metadata Handling**
  - Optional inclusion of validation rules as comments
  - Field descriptions preservation
  - Type constraints (min, max, pattern) as comments

#### Phase 2 (v0.2.0)
- [ ] **Enhanced Format Support**
  - BAML-style TypeScript-like syntax option
  - Hybrid JSON+YAML format
  - Customizable comment styles (// vs #)
  
- [ ] **Advanced Processing**
  - Circular reference detection and handling
  - Union type optimization
  - Generic type parameter simplification
  
- [ ] **Performance Optimization**
  - Token counting with different tokenizer libraries
  - Caching for repeated schema processing
  - Batch processing capabilities

#### Phase 3 (v0.3.0+)
- [ ] **Integration Features**
  - DSPy adapter integration
  - FastAPI integration helpers
  - LangChain schema compatibility
  
- [ ] **Advanced Utilities**
  - Schema diff and merge capabilities
  - Custom field processors/plugins
  - LLM response validation against simplified schema
  
- [ ] **CLI Tool**
  - Command-line schema conversion utility
  - Batch file processing
  - Performance benchmarking tool

### 5. Quality Requirements

#### Testing
- **Unit Tests**: 95%+ code coverage
- **Integration Tests**: Test with real Pydantic models
- **Performance Tests**: Token reduction benchmarks
- **Compatibility Tests**: Python 3.8-3.12, Pydantic v1 & v2

#### Documentation
- **README**: Clear installation, quickstart, and examples
- **API Documentation**: Comprehensive docstrings
- **Performance Benchmarks**: Before/after token comparisons
- **Integration Guides**: DSPy, FastAPI, LangChain examples

#### Code Quality
- **Type Hints**: Full type annotation coverage
- **Linting**: Black, isort, flake8 compliance
- **Security**: Bandit security analysis
- **Performance**: Profile memory usage and processing speed

### 6. Development Setup Requirements

#### Development Dependencies
```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
pytest-cov = "^4.0.0"
black = "^23.0.0"
isort = "^5.12.0"
flake8 = "^6.0.0"
mypy = "^1.0.0"
bandit = "^1.7.0"
pre-commit = "^3.0.0"
```

#### CI/CD Pipeline
- **GitHub Actions**: Automated testing on push/PR
- **Multi-Python Testing**: 3.8, 3.9, 3.10, 3.11, 3.12
- **PyPI Publishing**: Automated releases on version tags
- **Documentation**: Auto-generated docs deployment

### 7. Performance Targets

#### Token Efficiency
- **Target Reduction**: 60-85% fewer tokens than original JSON schema
- **Processing Speed**: <100ms for complex nested models
- **Memory Usage**: <50MB for typical usage patterns

#### Benchmark Test Cases
```python
# Example complex model for benchmarking
class ComplexOrder(BaseModel):
    order_id: int
    user: UserProfile
    items: List[OrderItem]
    shipping: Optional[ShippingAddress]
    metadata: Dict[str, Union[str, int, float]]
    created_at: datetime
    status: OrderStatus  # Enum
    tags: Set[str]
    
# Target: 800+ token schema → <200 tokens
```

### 8. Integration Specifications

#### DSPy Adapter
```python
class SchemaLiteAdapter(JSONAdapter):
    def format_field_structure(self, field_info, indent=0):
        # Use schema-lite for field formatting
        return super().format_field_structure(field_info, indent)
```

#### FastAPI Integration
```python
# Helper for FastAPI response models
def create_llm_schema_route(
    model: Type[BaseModel], 
    app: FastAPI,
    endpoint: str = "/schema"
): ...
```

### 9. Error Handling Requirements

#### Exception Hierarchy
```python
class SchemaLiteError(Exception): ...
class UnsupportedModelError(SchemaLiteError): ...
class ConversionError(SchemaLiteError): ...
class ValidationError(SchemaLiteError): ...
```

#### Graceful Degradation
- Fallback to original schema on conversion errors
- Warning logs for unsupported field types
- Partial schema generation for complex edge cases

### 10. Documentation Examples

#### Basic Usage
```python
from pydantic import BaseModel
from schema_lite import simplify_schema

class User(BaseModel):
    name: str
    age: int
    email: str

# Convert to LLM-friendly format
schema = simplify_schema(User)
print(schema.to_json())
# Output: {"name": "string", "age": "integer", "email": "string"}

# With metadata
schema_with_meta = simplify_schema(User, include_metadata=True)
print(schema_with_meta.to_yaml())
```

#### Performance Comparison
```python
original_tokens = len(User.model_json_schema().__str__().split())
simplified_tokens = schema.token_count()
print(f"Token reduction: {original_tokens} → {simplified_tokens}")
# Expected: Token reduction: 156 → 42
```

## Success Criteria

1. **Token Reduction**: Achieve 60-85% token reduction across diverse Pydantic models
2. **Compatibility**: Support Pydantic v1.10+ and v2.0+
3. **Performance**: Process complex schemas in <100ms
4. **Adoption**: Gain 100+ GitHub stars and 1000+ PyPI downloads within 6 months
5. **Integration**: Successful integration examples with DSPy, FastAPI, and LangChain

## Future Roadmap

- **v0.4.0**: Plugin architecture for custom processors
- **v0.5.0**: Visual schema editor/inspector
- **v1.0.0**: Stable API, enterprise features, comprehensive documentation