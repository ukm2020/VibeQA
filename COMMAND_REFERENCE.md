# VibeQA Generator - Command Structure Reference

## 📋 Basic Command Structure

```bash
py -m src.cli "SCENARIO" --framework FRAMEWORK [OPTIONS]
```

## 🔧 Complete Command Breakdown

### Core Command
```bash
py -m src.cli
```
- **`py`**: Python launcher (Windows)
- **`-m src.cli`**: Run the CLI module from the src package
- **Alternative**: `python -m src.cli` (if python is in PATH)

### Required Arguments

#### 1. **SCENARIO** (Positional Argument)
```bash
py -m src.cli "Your test scenario description here"
```
- **Type**: String (quoted)
- **Purpose**: Plain English description of what you want to test
- **Examples**:
  ```bash
  "Login with valid credentials and verify dashboard loads"
  "Add item to shopping cart and proceed to checkout"
  "Reset password via email and verify new password works"
  ```

#### 2. **--framework** (Required)
```bash
--framework rainforest         # JSON format for Rainforest QA
--framework rainforest-prompt  # Human-readable prompt for Rainforest AI
--framework cypress            # JavaScript test file  
--framework gherkin            # BDD feature file
```
- **Short form**: `-f`
- **Options**: `rainforest`, `rainforest-prompt`, `cypress`, `gherkin`
- **Purpose**: Target framework for test generation
- **rainforest-prompt**: Generates human-readable text for Rainforest's "Generate test with AI" field

## 🎛️ Optional Parameters

### **--base-url** / **-u**
```bash
--base-url https://myapp.com
-u https://staging.example.com
```
- **Purpose**: Base URL for the application under test
- **Default**: Uses `https://example.com` if not specified
- **Usage**: Gets embedded in the generated test

### **--tags** / **-t**
```bash
--tags "auth,positive"
--tags "e2e,cart,checkout"
-t "negative,validation"
```
- **Format**: Comma-separated list (quoted)
- **Rules**: Must be kebab-case (lowercase, hyphens only)
- **Purpose**: Categorize and organize tests
- **Examples**: `auth`, `login`, `email-validation`, `negative-test`

### **--out** / **-o**
```bash
--out test.json
--out cypress/tests/login.cy.js
-o features/login.feature
```
- **Purpose**: Save output to file (also prints to stdout)
- **Behavior**: Creates directories if they don't exist
- **Without**: Only prints to stdout

### **--strict**
```bash
--strict
```
- **Type**: Flag (no value needed)
- **Purpose**: Enable strict validation mode
- **Effect**: Rejects unknown fields and enforces stricter rules

### **--model**
```bash
--model gpt-4o
--model gpt-4
--model gpt-3.5-turbo
```
- **Default**: `gpt-4o`
- **Purpose**: Choose which OpenAI model to use
- **Options**: Any valid OpenAI model name

### **--temperature**
```bash
--temperature 0.2
--temperature 0.0
--temperature 0.5
```
- **Default**: `0.2`
- **Range**: `0.0` (deterministic) to `1.0` (creative)
- **Purpose**: Control randomness in generation

## 📝 Command Examples

### **Basic Usage**
```bash
# Minimal command
py -m src.cli "Login test" --framework rainforest

# With base URL
py -m src.cli "User signup flow" --framework cypress --base-url https://myapp.com
```

### **Complete Examples**
```bash
# Rainforest with all options
py -m src.cli "Invalid email signup validation" \
  --framework rainforest \
  --base-url https://staging.myapp.com \
  --tags "auth,negative,email-validation" \
  --out tests/invalid_signup.json \
  --strict \
  --model gpt-4o \
  --temperature 0.1

# Cypress test generation
py -m src.cli "Add multiple items to cart and checkout" \
  --framework cypress \
  --base-url https://shop.example.com \
  --tags "e2e,cart,checkout" \
  --out cypress/e2e/cart_checkout.cy.js

# Gherkin feature file
py -m src.cli "Password reset via email verification" \
  --framework gherkin \
  --tags "auth,password,email" \
  --out features/password_reset.feature
```

### **Short Form Options**
```bash
# Using short flags
py -m src.cli "Login test" -f rainforest -u https://app.com -t "auth,positive" -o login.json
```

## 🔄 Command Flow

### 1. **Input Processing**
```
SCENARIO → Parse and validate
FRAMEWORK → Check if supported (rainforest/cypress/gherkin)
OPTIONS → Parse tags, URLs, file paths
```

### 2. **Generation Process**
```
API Key Check → LLM Generation → Schema Validation → Framework Conversion → Output
```

### 3. **Output Behavior**
```
ALWAYS: Print to stdout (terminal)
WITH --out: Also save to specified file
WITH --strict: Apply stricter validation rules
```

## ⚠️ Error Handling

### **Missing API Key**
```bash
Error: OPENAI_API_KEY environment variable is required
```
**Solution**: Set `$env:OPENAI_API_KEY = "your-key"`

### **Invalid Framework**
```bash
Error: Unsupported framework 'invalid'. Available: cypress, gherkin, rainforest
```
**Solution**: Use one of the supported frameworks

### **Validation Failure**
```bash
Error: Validation failed: Missing required fields for 'click': selector_type, selector
```
**Solution**: The LLM output didn't meet schema requirements (automatic retry attempted)

### **Invalid Tags**
```bash
Error: Tag 'Invalid_Tag' must be kebab-case (lowercase, hyphens only)
```
**Solution**: Use kebab-case: `invalid-tag`

## 🎯 Real-World Usage Patterns

### **Development Workflow**
```bash
# 1. Generate initial test
py -m src.cli "User login flow" -f rainforest -u https://dev.myapp.com -t "auth,positive"

# 2. Save to file for review
py -m src.cli "User login flow" -f rainforest -u https://dev.myapp.com -t "auth,positive" -o tests/login.json

# 3. Generate for multiple frameworks
py -m src.cli "User login flow" -f cypress -u https://dev.myapp.com -t "auth,positive" -o cypress/login.cy.js
py -m src.cli "User login flow" -f gherkin -t "auth,positive" -o features/login.feature
```

### **CI/CD Integration**
```bash
# Strict mode for production
py -m src.cli "Critical payment flow" -f rainforest --strict -u https://prod.myapp.com -t "payment,critical"

# Deterministic output for consistency
py -m src.cli "API validation test" -f cypress --temperature 0.0 -t "api,validation"
```

## 🚀 Pro Tips

### **Scenario Writing**
- ✅ **Good**: "Login with valid credentials and verify dashboard loads"
- ❌ **Bad**: "Login test"
- **Tip**: Be specific about expected outcomes

### **Tag Strategy**
- **Categories**: `auth`, `payment`, `admin`
- **Types**: `positive`, `negative`, `edge`
- **Scope**: `unit`, `integration`, `e2e`
- **Priority**: `critical`, `high`, `medium`, `low`

### **File Organization**
```bash
# Organized output structure
--out tests/rainforest/auth/login.json
--out cypress/e2e/auth/login.cy.js  
--out features/auth/login.feature
```

### **Model Selection**
- **Production**: `gpt-4o` (best balance)
- **Development**: `gpt-3.5-turbo` (faster/cheaper)
- **Critical Tests**: `gpt-4` (highest quality)

This command structure gives you complete control over test generation while maintaining simplicity for basic use cases!
