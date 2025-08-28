# VibeQA Generator - Schema Reference (rf-1.0)

## 📋 Overview

The VibeQA Generator enforces strict guidelines through a comprehensive Pydantic schema that validates all generated test metadata. This ensures **deterministic, consistent, and reliable** test artifacts.

## 🏗️ Schema Structure

### Top-Level Schema (`RainforestTest`)

```python
{
  "schema_version": "rf-1.0",           # REQUIRED: Exact version string
  "title": "string",                    # REQUIRED: 5-120 characters
  "description": "string",              # REQUIRED: 20-400 characters  
  "tags": ["string", ...],              # REQUIRED: ≥1 kebab-case tags
  "environment": { ... },               # REQUIRED: Environment config
  "variables": [ ... ],                 # OPTIONAL: Variable definitions
  "steps": [ ... ],                     # REQUIRED: 4-12 test steps
  "final_result": "string",             # REQUIRED: Overall outcome
  "design_decisions": "string"          # REQUIRED: ≤5 sentences
}
```

## 🔒 Strict Validation Rules

### 1. Schema Version
- **Pattern**: `^rf-1\.0$` (regex enforced)
- **Default**: `"rf-1.0"`
- **Purpose**: Ensures version compatibility

### 2. Title Constraints
```python
title: str = Field(..., min_length=5, max_length=120)
```
- **Minimum**: 5 characters
- **Maximum**: 120 characters
- **Required**: Cannot be empty or null

### 3. Description Constraints
```python
description: str = Field(..., min_length=20, max_length=400)
```
- **Minimum**: 20 characters (ensures meaningful descriptions)
- **Maximum**: 400 characters (prevents verbosity)
- **Required**: Must provide context

### 4. Tags Validation
```python
tags: List[str] = Field(..., min_items=1)

@validator('tags')
def validate_tags(cls, v):
    kebab_pattern = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
    for tag in v:
        if not kebab_pattern.match(tag):
            raise ValueError(f"Tag '{tag}' must be kebab-case")
```
- **Format**: `kebab-case` only (lowercase, hyphens)
- **Examples**: ✅ `"auth"`, `"email-validation"`, `"negative-test"`
- **Invalid**: ❌ `"Auth"`, `"email_validation"`, `"Email Validation"`
- **Minimum**: At least 1 tag required

### 5. Environment Schema
```python
class Environment(BaseModel):
    app_type: str = Field(default="web", pattern="^web$")
    base_url: str = Field(..., min_length=1)
```
- **app_type**: Must be exactly `"web"`
- **base_url**: Required, minimum 1 character

### 6. Steps Validation
```python
steps: List[TestStep] = Field(..., min_items=4, max_items=12)
```
- **Minimum**: 4 steps (ensures meaningful tests)
- **Maximum**: 12 steps (prevents overly complex tests)
- **Each step**: Must have `expected_result`

### 7. Design Decisions Constraint
```python
@validator('design_decisions')
def validate_design_decisions_length(cls, v):
    sentences = v.count('.') + v.count('!') + v.count('?')
    if sentences > 5:
        raise ValueError("design_decisions must be <= 5 sentences")
```
- **Maximum**: 5 sentences (counted by `.`, `!`, `?`)
- **Purpose**: Keeps explanations concise and focused

## 🎯 Step Schema (`TestStep`)

### Required Fields
```python
action: str                    # REQUIRED: Must be valid action
expected_result: str          # REQUIRED: What should happen
```

### Optional Fields (Action-Dependent)
```python
target: Optional[str]         # For navigation actions
selector_type: Optional[str]  # Must be "css" when selector present
selector: Optional[str]       # CSS selector string
value: Optional[str]          # Input values
timeout_seconds: Optional[int] # Wait timeouts
match: Optional[str]          # Text matching type
```

## 🔧 Action Validation

### Allowed Actions & Required Fields
```python
ALLOWED_ACTIONS = {
    'navigate': ['target', 'expected_result'],
    'wait_for_element': ['selector_type', 'selector', 'timeout_seconds', 'expected_result'],
    'type': ['selector_type', 'selector', 'value', 'expected_result'],
    'click': ['selector_type', 'selector', 'expected_result'],
    'assert_element_text': ['selector_type', 'selector', 'match', 'value', 'expected_result'],
    'assert_element_visible': ['selector_type', 'selector', 'expected_result'],
    'assert_no_navigation': ['expected_result'],
    'open_new_tab': ['target', 'expected_result'],
    'switch_to_new_tab': ['expected_result'],
}
```

### Selector Type Validation
```python
@validator('selector_type')
def validate_selector_type(cls, v, values):
    if 'selector' in values and values['selector'] is not None:
        if v != 'css':
            raise ValueError("selector_type must be 'css' when selector is present")
```
- **Rule**: When `selector` is present, `selector_type` MUST be `"css"`
- **Purpose**: Ensures consistent selector strategy

### Match Type Validation
```python
@validator('match')
def validate_match(cls, v, values):
    if values.get('action') == 'assert_element_text':
        if v not in ['equals', 'contains', 'regex']:
            raise ValueError("match must be 'equals', 'contains', or 'regex'")
```
- **Valid values**: `"equals"`, `"contains"`, `"regex"`
- **Only for**: `assert_element_text` actions

## 🔍 Variable Validation

### Variable Declaration
```python
class Variable(BaseModel):
    name: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)
```

### Variable Usage Validation
```python
def validate_variables_usage(self) -> List[str]:
    var_pattern = re.compile(r'\{\{(\w+)\}\}')
    # Find all {{variable}} references
    # Ensure all referenced variables are declared
```
- **Format**: `{{variable_name}}`
- **Rule**: All `{{var}}` references must be declared in `variables` array
- **Error**: "Variable 'name' used but not declared"

## 🚫 Strict Mode Validation

### Unknown Field Detection
```python
def _check_unknown_fields(self, data, result):
    known_top_level_fields = {
        'schema_version', 'title', 'description', 'tags', 'environment',
        'variables', 'steps', 'final_result', 'design_decisions'
    }
    unknown_fields = set(data.keys()) - known_top_level_fields
```
- **Purpose**: Prevents unexpected fields in strict mode
- **Enforcement**: CLI `--strict` flag

### Step Field Validation
```python
def _validate_step_actions(self, test, result):
    required_fields = set(ALLOWED_ACTIONS[action])
    present_fields = set(step_dict.keys())
    
    # Check missing required fields
    missing_fields = required_fields - present_fields
    
    # In strict mode, check unexpected fields
    unexpected_fields = present_fields - required_fields - {'action'}
```

## 📝 Validation Examples

### ✅ Valid Test Structure
```json
{
  "schema_version": "rf-1.0",
  "title": "Login Flow Validation",
  "description": "Test successful user authentication with valid credentials and dashboard verification.",
  "tags": ["auth", "positive", "login"],
  "environment": {
    "app_type": "web",
    "base_url": "https://example.com"
  },
  "steps": [
    {
      "action": "navigate",
      "target": "/login",
      "expected_result": "Login page loads"
    },
    {
      "action": "type",
      "selector_type": "css",
      "selector": "[data-test='email']",
      "value": "user@example.com",
      "expected_result": "Email entered"
    },
    {
      "action": "click", 
      "selector_type": "css",
      "selector": "[data-test='submit']",
      "expected_result": "Form submitted"
    },
    {
      "action": "assert_element_visible",
      "selector_type": "css", 
      "selector": "[data-test='dashboard']",
      "expected_result": "Dashboard visible"
    }
  ],
  "final_result": "User successfully logs in and sees dashboard",
  "design_decisions": "Used data-test selectors for reliability. Focused on happy path flow."
}
```

### ❌ Common Validation Errors

1. **Invalid Tag Format**:
   ```json
   "tags": ["Auth", "Email_Validation"]  // ❌ Not kebab-case
   ```

2. **Wrong Selector Type**:
   ```json
   {
     "action": "click",
     "selector_type": "xpath",  // ❌ Must be "css"
     "selector": "//button"
   }
   ```

3. **Missing Required Fields**:
   ```json
   {
     "action": "type",
     "selector": "[data-test='input']"
     // ❌ Missing selector_type, value, expected_result
   }
   ```

4. **Too Many Steps**:
   ```json
   "steps": [/* 15 steps */]  // ❌ Maximum 12 steps
   ```

5. **Design Decisions Too Long**:
   ```json
   "design_decisions": "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence. Sixth sentence."  // ❌ >5 sentences
   ```

## 🎯 Enforcement Points

1. **Generation Time**: Schema validates LLM output
2. **CLI Validation**: `--strict` mode enforces all rules
3. **Retry Logic**: Invalid output triggers correction prompt
4. **Unit Tests**: Comprehensive validation testing

This strict schema ensures that every generated test artifact is **consistent**, **valid**, and **production-ready** across all supported frameworks.
