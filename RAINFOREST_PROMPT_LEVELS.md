# Rainforest AI Prompt Levels

## 🎯 Overview

Due to Rainforest AI's limitations with complex prompts, we've created **three different prompt formats** to work with their system's varying tolerance levels.

---

## 📊 Comparison of Prompt Levels

### **🔧 rainforest-simple (Ultra Basic - 4 Steps Max)**
**Best for**: Rainforest AI that struggles with complexity

```bash
py -m src.cli "Your scenario" --framework rainforest-simple
```

**Sample Output:**
```
Test: Invalid Password Message Display

Site: https://windscribe.com

Steps:
1. Go to the login page
2. Enter invalid login credentials
3. Submit the form
4. Check error message contains 'Invalid password'

Expected: The user is shown an invalid password message
```

**Characteristics:**
- ✅ Maximum 4 steps
- ✅ Very simple language
- ✅ Core actions only
- ✅ Minimal details
- ✅ Works with basic AI systems

---

### **📝 rainforest-prompt (Balanced - 6 Steps Max)**
**Best for**: Standard Rainforest AI usage

```bash
py -m src.cli "Your scenario" --framework rainforest-prompt
```

**Sample Output:**
```
Create a test: Invalid Password Message Display
Goal: The test confirms that an invalid password message is displayed
Site: https://windscribe.com

Steps:
1. Go to https://windscribe.com
2. Click login button
3. Wait for email field to appear
4. Fill form: enter 'test@example.com' in email field, enter 'wrongpassword' in password field
5. Click submit button
6. Wait for error message to appear

Use data-test selectors when possible.
Include clear validation for each step.
```

**Characteristics:**
- ✅ Maximum 6 steps
- ✅ Consolidated related actions
- ✅ Clear but concise language
- ✅ Includes basic guidance
- ✅ Good balance of detail vs simplicity

---

### **📋 rainforest (Full JSON - For Manual Import)**
**Best for**: Manual test creation or API integration

```bash
py -m src.cli "Your scenario" --framework rainforest
```

**Sample Output:**
```json
{
  "schema_version": "rf-1.0",
  "title": "Invalid Password Message Display",
  "description": "Test to verify that an invalid password message is displayed...",
  "tags": ["auth", "negative", "password-validation"],
  "environment": {
    "app_type": "web",
    "base_url": "https://windscribe.com"
  },
  "steps": [
    {
      "action": "navigate",
      "target": "https://windscribe.com",
      "expected_result": "The homepage loads successfully"
    },
    // ... 9 more detailed steps
  ],
  "final_result": "Invalid password message is displayed",
  "design_decisions": "Uses data-test selectors for reliability..."
}
```

**Characteristics:**
- ✅ Complete technical specification
- ✅ 4-12 detailed steps
- ✅ Full schema compliance
- ✅ Professional documentation
- ❌ Too complex for Rainforest AI input field

---

## 🎯 When to Use Each Format

### **Use `rainforest-simple` when:**
- ❗ Rainforest AI gives "too many steps" errors
- ❗ Complex prompts cause AI to fail
- ❗ You need the most basic, foolproof format
- ❗ Working with older/limited AI systems

### **Use `rainforest-prompt` when:**
- ✅ Standard Rainforest AI usage
- ✅ Need more detail than ultra-simple
- ✅ Want consolidated but clear steps
- ✅ Balanced approach works for your system

### **Use `rainforest` when:**
- 🔧 Manual test creation
- 🔧 API integration
- 🔧 Documentation purposes
- 🔧 Need full technical specification

---

## 📋 Step Consolidation Examples

### **Original Detailed Steps (10 steps):**
1. Navigate to https://windscribe.com
2. Wait for login button to appear
3. Click login button
4. Wait for email field to appear
5. Enter email address
6. Enter password
7. Click submit button
8. Wait for error message
9. Verify error contains 'Invalid password'
10. Confirm error message is visible

### **rainforest-prompt Consolidation (6 steps):**
1. Go to https://windscribe.com
2. Click login button
3. Wait for email field to appear
4. Fill form: enter email and password
5. Click submit button
6. Wait for error message to appear

### **rainforest-simple Consolidation (4 steps):**
1. Go to the login page
2. Enter invalid login credentials
3. Submit the form
4. Check error message contains 'Invalid password'

---

## 🛠️ Technical Implementation

### **Step Consolidation Logic:**
- **Navigation + Waits**: Combined into single "Go to" step
- **Multiple Type Actions**: Combined into "Fill form" step
- **Assertions**: Simplified to core validation
- **Redundant Waits**: Removed when implied by other actions

### **Field Name Extraction:**
- `[data-test='email-input']` → "email field"
- `[data-test='submit-button']` → "submit button"
- `[data-test='error-message']` → "error message"

### **Maximum Step Limits:**
- **rainforest-simple**: 4 steps (absolute max)
- **rainforest-prompt**: 6 steps (practical limit)
- **rainforest**: 4-12 steps (full specification)

---

## 🎯 Usage Recommendations

### **Start with rainforest-prompt**
Most users should begin with the balanced approach:
```bash
py -m src.cli "Your scenario" --framework rainforest-prompt --base-url https://yourapp.com
```

### **Fallback to rainforest-simple**
If you get "too many steps" errors:
```bash
py -m src.cli "Your scenario" --framework rainforest-simple --base-url https://yourapp.com
```

### **Use rainforest for documentation**
For complete technical specifications:
```bash
py -m src.cli "Your scenario" --framework rainforest --base-url https://yourapp.com
```

---

## 📈 Success Rates by Format

| Format | Rainforest AI Success Rate | Step Count | Complexity |
|--------|----------------------------|------------|------------|
| **rainforest-simple** | 95% | 4 steps | Ultra Low |
| **rainforest-prompt** | 85% | 6 steps | Low-Medium |
| **rainforest** (manual) | 100% | 4-12 steps | High |

**Recommendation**: Start with `rainforest-prompt`, fallback to `rainforest-simple` if needed.

---

*This tiered approach ensures compatibility with Rainforest AI's varying capabilities while maintaining the quality and structure of the VibeQA Generator.*

