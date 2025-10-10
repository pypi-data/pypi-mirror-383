# Code Quality & Indentation Guide for Freshrelease MCP

## 🎯 Purpose
This guide ensures consistent, error-free code development for the Freshrelease MCP project, specifically focusing on preventing indentation errors and maintaining high code quality.

## 📐 Indentation Standards

### **Python Indentation Rules**
- **USE 4 SPACES** - Never use tabs
- **Consistent throughout** - All code blocks must use exactly 4 spaces
- **No mixed indentation** - Never mix spaces and tabs
- **Function/Class bodies** - Always indent by 4 spaces from the def/class line

### **Common Indentation Patterns in This Project**

#### ✅ **Correct MCP Tool Function Structure**
```python
@mcp.tool()
@performance_monitor("function_name")
async def function_name(
    param1: Type,
    param2: Optional[Type] = None
) -> Dict[str, Any]:
    """Docstring with proper indentation.
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        Description
    """
    try:
        # Function body - 4 spaces from def line
        if condition:
            # Nested block - 8 spaces from def line
            result = await some_function()
            return result
        else:
            # Same level as if - 8 spaces from def line
            return error_response
            
    except Exception as e:
        # Exception handling - 4 spaces from def line
        return create_error_response(f"Error: {str(e)}")
```

#### ✅ **Correct Dictionary/List Structures**
```python
# Multi-line dictionary
result = {
    "key1": value1,
    "key2": {
        "nested_key": nested_value,
        "another_key": another_value
    },
    "key3": [
        item1,
        item2,
        item3
    ]
}

# Function call with multiple parameters
response = await make_api_request(
    method="GET",
    url=url,
    headers=headers,
    params={
        "param1": value1,
        "param2": value2
    }
)
```

#### ✅ **Correct If/Else/Try/Except Structures**
```python
# Proper if-else indentation
if condition1:
    # 4 spaces from if
    action1()
    if nested_condition:
        # 8 spaces from original if
        nested_action()
elif condition2:
    # Same level as if
    action2()
else:
    # Same level as if
    default_action()

# Proper try-except indentation
try:
    # 4 spaces from try
    risky_operation()
    if success:
        # 8 spaces from try
        handle_success()
except SpecificError as e:
    # Same level as try
    handle_error(e)
except Exception as e:
    # Same level as try
    handle_generic_error(e)
finally:
    # Same level as try
    cleanup()
```

#### ✅ **Correct Loop Structures**
```python
# For loop indentation
for item in items:
    # 4 spaces from for
    processed_item = process(item)
    if processed_item:
        # 8 spaces from for
        results.append(processed_item)
        if detailed_logging:
            # 12 spaces from for
            logging.info(f"Processed: {processed_item}")

# While loop indentation
while condition:
    # 4 spaces from while
    result = get_next_item()
    if result:
        # 8 spaces from while
        process_result(result)
```

## ❌ Common Indentation Mistakes to Avoid

### **Mistake 1: Inconsistent Spacing**
```python
# WRONG - Mixed indentation levels
def bad_function():
    if condition:
        action1()  # 4 spaces
          action2()  # 6 spaces - WRONG!
      action3()    # 2 spaces - WRONG!
```

### **Mistake 2: Hanging Indents After Colons**
```python
# WRONG - Incorrect indentation after if/else
if condition:
        # 8 spaces instead of 4 - WRONG!
    action()

# WRONG - Incorrect else indentation
if condition:
    action1()
        else:  # Should align with if - WRONG!
    action2()
```

### **Mistake 3: Function/Method Indentation Errors**
```python
# WRONG - Class method indentation
class MyClass:
    def method1(self):
        pass
        
        def method2(self):  # Should be at class level - WRONG!
        pass
```

### **Mistake 4: Dictionary/List Indentation Errors**
```python
# WRONG - Inconsistent dictionary indentation
result = {
    "key1": value1,
        "key2": value2,  # Extra indentation - WRONG!
"key3": value3           # Missing indentation - WRONG!
}
```

## 🛠️ Project-Specific Patterns

### **MCP Tool Function Template**
```python
@mcp.tool()
@performance_monitor("tool_name")
async def tool_name(
    required_param: str,
    optional_param: Optional[str] = None,
    project_identifier: Optional[Union[int, str]] = None
) -> Dict[str, Any]:
    """Tool description.
    
    Args:
        required_param: Description
        optional_param: Description  
        project_identifier: Project ID or key (optional, uses FRESHRELEASE_PROJECT_KEY if not provided)
        
    Returns:
        Dictionary containing results or error response
        
    Examples:
        # Example usage
        tool_name("value")
    """
    try:
        # Environment validation
        env_data = validate_environment()
        project_id = get_project_identifier(project_identifier)
        
        # Main logic
        if condition:
            result = await process_data()
            return {
                "success": True,
                "data": result
            }
        else:
            return create_error_response("Condition not met")
            
    except Exception as e:
        return create_error_response(f"Failed to execute tool: {str(e)}")
```

### **API Request Pattern**
```python
# Standard API request structure
async def make_request():
    try:
        url = f"{base_url}/{endpoint}"
        params = {
            "param1": value1,
            "param2": value2
        }
        
        result = await make_api_request(
            method="GET",
            url=url,
            headers=headers,
            params=params
        )
        
        if "error" not in result:
            return process_success(result)
        else:
            return handle_error(result)
            
    except httpx.HTTPStatusError as e:
        return create_error_response(f"HTTP error: {str(e)}")
    except Exception as e:
        return create_error_response(f"Request failed: {str(e)}")
```

### **AI Analysis Function Pattern**
```python
def _generate_insights(data: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate AI insights from data.
    
    Args:
        data: List of data objects to analyze
        context: Additional context for analysis
        
    Returns:
        Dictionary containing insights, recommendations, and metrics
    """
    if not data:
        return {
            "summary": "No data available for analysis.",
            "insights": [],
            "recommendations": [],
            "metrics": {}
        }
    
    # Initialize counters
    metrics = {}
    insights = []
    recommendations = []
    
    # Analyze data
    for item in data:
        # Process each item
        if item.get("status"):
            status = item["status"]
            metrics[status] = metrics.get(status, 0) + 1
    
    # Generate insights based on analysis
    if metrics:
        total_items = len(data)
        for status, count in metrics.items():
            percentage = (count / total_items) * 100
            insights.append(f"{status}: {count} items ({percentage:.1f}%)")
    
    return {
        "summary": f"Analyzed {len(data)} items",
        "insights": insights,
        "recommendations": recommendations,
        "metrics": metrics
    }
```

## 🔧 Code Optimization Guidelines

### **Performance Optimization**
1. **Use async/await properly**
   ```python
   # Good - Parallel API calls
   tasks = [
       make_api_call(url1),
       make_api_call(url2),
       make_api_call(url3)
   ]
   results = await asyncio.gather(*tasks)
   
   # Avoid - Sequential API calls
   result1 = await make_api_call(url1)
   result2 = await make_api_call(url2)
   result3 = await make_api_call(url3)
   ```

2. **Efficient data processing**
   ```python
   # Good - List comprehension
   processed_items = [
       process_item(item) 
       for item in items 
       if item.get("active")
   ]
   
   # Good - Generator for large datasets
   def process_large_dataset(items):
       for item in items:
           if should_process(item):
               yield process_item(item)
   ```

3. **Memory optimization**
   ```python
   # Good - Process in chunks for large datasets
   def process_in_chunks(items, chunk_size=100):
       for i in range(0, len(items), chunk_size):
           chunk = items[i:i + chunk_size]
           yield process_chunk(chunk)
   ```

### **Error Handling Optimization**
```python
# Comprehensive error handling pattern
async def robust_api_call(url: str, retries: int = 3) -> Dict[str, Any]:
    """Make API call with proper error handling and retries."""
    for attempt in range(retries):
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
            
        except httpx.TimeoutException:
            if attempt == retries - 1:
                return create_error_response("Request timed out after retries")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return create_error_response("Resource not found")
            elif e.response.status_code >= 500:
                if attempt == retries - 1:
                    return create_error_response(f"Server error: {e.response.status_code}")
                await asyncio.sleep(2 ** attempt)
            else:
                return create_error_response(f"HTTP error: {e.response.status_code}")
                
        except Exception as e:
            return create_error_response(f"Unexpected error: {str(e)}")
    
    return create_error_response("All retry attempts failed")
```

### **Code Reusability Optimization**
```python
# Create reusable helper functions
def _add_ai_summary_to_result(result: Dict[str, Any], data_key: str, summary_func: Callable) -> Dict[str, Any]:
    """Generic helper to add AI summary to any result."""
    if "error" in result:
        return result
        
    data = result.get(data_key, [])
    ai_summary = summary_func(data)
    
    return {
        data_key: data,
        "ai_summary": ai_summary,
        "original_response": result
    }

# Use helper function in multiple places
def process_tasks_with_summary(result):
    return _add_ai_summary_to_result(result, "tasks", _generate_task_insights)

def process_testcases_with_summary(result):
    return _add_ai_summary_to_result(result, "test_cases", _generate_testcase_insights)
```

### **❌ Avoiding Redundant Code and Duplicate Methods**

**Rule:** Always check if functionality already exists before creating new methods. Enhance existing methods rather than duplicating functionality.

#### **❌ Bad Example: Creating Duplicate Methods**
```python
# EXISTING METHOD (already handles field resolution)
async def _resolve_testcase_field_value(condition, value, project_id, client, base_url, headers):
    """Existing method that resolves testcase field values."""
    if condition == "creator_id":
        return await _resolve_user_name_to_id(value, project_id, client, base_url, headers)
    elif condition == "section_id":
        return await _resolve_name_to_id_generic(value, project_id, client, base_url, headers, "sections")
    # ... existing logic

# BAD - Creating a duplicate method with similar functionality
async def resolve_testcase_field_explicit(condition, value):
    """REDUNDANT - Duplicates existing functionality!"""
    if condition == "creator_id":
        return await resolve_creator_to_id(value)  # Same logic, different wrapper
    elif condition == "severity_id":
        return severity_options.get(value.lower())  # Only new part
    # ... duplicate logic
```

#### **✅ Good Example: Enhancing Existing Methods**
```python
# ENHANCED - Add optional parameters to existing method
async def _resolve_testcase_field_value(
    condition: str, 
    value: Any, 
    project_id: Union[int, str],
    client: httpx.AsyncClient,
    base_url: str,
    headers: Dict[str, str],
    severity_options: Optional[Dict[str, int]] = None,  # ← NEW
    section_options: Optional[Dict[str, int]] = None    # ← NEW
) -> Any:
    """Enhanced existing method with new functionality."""
    
    # NEW functionality: Use form field mappings when available
    if condition == "severity_id" and severity_options and value.lower() in severity_options:
        return severity_options[value.lower()]
    
    # EXISTING functionality: Maintained and enhanced
    elif condition == "creator_id":
        return await _resolve_user_name_to_id(value, project_id, client, base_url, headers)
    # ... rest of existing logic
```

#### **🔍 Before Creating New Methods - Ask These Questions:**

1. **Does similar functionality already exist?**
   ```bash
   # Search for existing methods
   grep -n "def.*resolve.*field" src/freshrelease_mcp/server.py
   grep -n "async def.*resolve" src/freshrelease_mcp/server.py
   ```

2. **Can I enhance the existing method instead?**
   - Add optional parameters for new functionality
   - Maintain backward compatibility
   - Use progressive enhancement patterns

3. **Am I duplicating logic?**
   - If you're copying code patterns, refactor instead
   - Create shared helper functions for common logic
   - Use composition over duplication

#### **✅ Code Review Checklist for Redundancy**

Before committing new methods:

- [ ] **Search existing codebase** for similar functionality
- [ ] **Check method signatures** - do they overlap with existing methods?
- [ ] **Analyze logic patterns** - am I copying existing conditional structures?
- [ ] **Consider enhancement** - can I add optional parameters to existing methods?
- [ ] **Test backward compatibility** - do existing calls still work?

#### **🚨 Warning Signs of Redundant Code**

- **Similar method names**: `resolve_field()` vs `resolve_field_explicit()`
- **Duplicate conditional logic**: Same if/elif patterns in multiple methods
- **Wrapper functions**: Methods that just call other methods with minor changes
- **Copy-paste patterns**: Large blocks of similar code with minor variations

#### **✅ Refactoring Strategy When You Find Redundancy**

1. **Identify the core method** that should be enhanced
2. **Add optional parameters** for new functionality  
3. **Update all call sites** to use enhanced method
4. **Remove duplicate methods** completely
5. **Test thoroughly** to ensure no regressions
6. **Update documentation** to reflect changes

**Remember: One well-designed method is better than multiple similar methods!**

## 🔍 Pre-Commit Checklist

### **Before Adding New Code:**
1. ✅ **Check indentation consistency**
   - All function bodies use 4 spaces
   - All nested blocks properly aligned

2. ✅ **Check for redundant code**
   - Search for existing similar functionality
   - Consider enhancing existing methods instead of creating new ones
   - Verify no duplicate conditional logic patterns

3. ✅ **Verify function structure**
   - Proper MCP tool decorators
   - Consistent parameter naming
   - Complete docstrings with Args/Returns

4. ✅ **Test error scenarios**
   - Handle all expected exceptions
   - Provide meaningful error messages
   - Include fallback behaviors

5. ✅ **Optimize performance**
   - Use async/await appropriately
   - Consider parallel processing
   - Implement caching where beneficial

6. ✅ **Code reusability**
   - Extract common patterns into helpers
   - Follow DRY principle
   - Create reusable components

## 🚨 Emergency Indentation Fix

If you encounter indentation errors:

1. **Use your editor's "show whitespace" feature**
2. **Select all code and auto-format** (most editors have this)
3. **Manually check these common areas:**
   - After `if`, `elif`, `else` statements
   - After `try`, `except`, `finally` blocks
   - After `for`, `while` loops
   - After function/class definitions
   - Inside dictionaries and lists

4. **Verify using Python's built-in checker:**
   ```bash
   python -m py_compile filename.py
   ```

## 📋 IDE Configuration Recommendations

### **VS Code Settings**
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "editor.tabSize": 4,
    "editor.insertSpaces": true,
    "editor.detectIndentation": false,
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
}
```

### **PyCharm Settings**
- File → Settings → Editor → Code Style → Python
- Set "Tab size" and "Indent" to 4
- Check "Use tab character" should be UNCHECKED
- Enable "Optimize imports on the fly"

## 🎯 Quality Assurance Commands

```bash
# Check for indentation issues
python -m py_compile src/freshrelease_mcp/server.py

# Format code (if black is installed)
black src/freshrelease_mcp/server.py

# Check linting
flake8 src/freshrelease_mcp/server.py

# Build and test
uv build
```

## 📝 Final Notes

- **Always test your code** before committing
- **Use consistent naming conventions** throughout the project
- **Write comprehensive docstrings** for all public functions
- **Handle edge cases** and provide meaningful error messages
- **Optimize for readability** - code is read more often than written
- **Follow the established patterns** in the existing codebase

## 8. Indentation and Syntax Consistency

### Critical Rule: Maintain Proper Python Indentation

Python's indentation-sensitive syntax requires absolute consistency. Improper indentation causes `IndentationError` crashes that prevent the package from loading.

### ❌ **Bad Examples (Causes Runtime Crashes):**

```python
# Problem 1: Misaligned else statement
if parent_section_id is None:
    url = f"{base_url}/{project_identifier}/sections"
                else:  # WRONG: Extra indentation
    url = f"{base_url}/{project_identifier}/sections/{parent_section_id}/sections"

# Problem 2: Inconsistent indentation within if block  
if section_name and str(section_name).strip().lower() == target_lower:
        section_id = section.get("id")  # WRONG: Over-indented
    return section_id if isinstance(section_id, int) else None  # WRONG: Under-indented

# Problem 3: Misaligned for loop
logging.info("Processing filter rules")
        for i, rule in enumerate(filter_rules):  # WRONG: Over-indented
                if isinstance(rule, dict):  # WRONG: Double over-indented
                    process_rule(rule)
```

### ✅ **Good Examples:**

```python
# Correct: Properly aligned if-else
if parent_section_id is None:
    url = f"{base_url}/{project_identifier}/sections"
else:  # CORRECT: Aligned with if
    url = f"{base_url}/{project_identifier}/sections/{parent_section_id}/sections"

# Correct: Consistent indentation within if block
if section_name and str(section_name).strip().lower() == target_lower:
    section_id = section.get("id")  # CORRECT: 4 spaces
    return section_id if isinstance(section_id, int) else None  # CORRECT: Same level

# Correct: Properly aligned for loop
logging.info("Processing filter rules")
for i, rule in enumerate(filter_rules):  # CORRECT: No extra indentation
    if isinstance(rule, dict):  # CORRECT: 4 spaces from for
        process_rule(rule)  # CORRECT: 8 spaces from for
```

### 🔧 **Prevention Strategies:**

1. **Use a consistent editor setup:**
   ```
   - Set tab size to 4 spaces
   - Show whitespace characters
   - Enable indentation guides
   - Use "spaces only" (no tabs)
   ```

2. **Run linter regularly:**
   ```bash
   # Check for indentation issues before committing
   python -m py_compile src/freshrelease_mcp/server.py
   ```

3. **Common indentation patterns:**
   ```python
   # Function definition (0 spaces)
   def my_function():
       # Function body (4 spaces)
       if condition:
           # If body (8 spaces)
           for item in items:
               # Loop body (12 spaces)
               process(item)
   ```

### 🚨 **Warning Signs:**

- **IndentationError** during package import
- **Unexpected indentation** linter warnings  
- **Mixed tabs and spaces** warnings
- Code that looks correct but fails to run

### 📋 **Indentation Checklist:**

Before committing any Python code:

- [ ] All if/else statements properly aligned
- [ ] Loop bodies consistently indented (4 spaces per level)
- [ ] Function/method bodies indented uniformly
- [ ] No mixing of tabs and spaces
- [ ] Nested blocks follow 4-space increments
- [ ] Test that Python can compile the file: `python -m py_compile filename.py`

### 🎯 **Quick Fix Commands:**

```bash
# Check syntax without running
python -m py_compile src/freshrelease_mcp/server.py

# Auto-format with consistent indentation
python -m black src/freshrelease_mcp/server.py --line-length 120
```

**Remember**: Indentation errors cause complete package failure - they're not just style issues but critical bugs that prevent the MCP server from starting.

## 9. Preventing Duplicate Method Calls and Responses

### Critical Issue: Duplicate API Calls Can Cause Performance Problems

Duplicate method calls, especially for expensive operations like `fr_get_epic_insights`, can cause unnecessary API load, increased latency, and confusing user experiences.

### 🚨 **Common Causes of Duplicate Calls:**

1. **Duplicate Assistant Responses:**
   ```
   First response: "I'll get the epic insights for FS-223786 for you..."
   Second response: "I'll get the epic insights for FS-223786 for you..." (identical)
   ```

2. **Race Conditions in Async Operations:**
   ```python
   # BAD: Multiple concurrent calls to same resource
   async def process_epic():
       task1 = fr_get_epic_insights("FS-223786")
       task2 = fr_get_epic_insights("FS-223786")  # DUPLICATE!
       await asyncio.gather(task1, task2)
   ```

3. **Retry Logic Without Deduplication:**
   ```python
   # BAD: Retries without checking if already in progress
   for attempt in range(3):
       try:
           result = await fr_get_epic_insights(epic_key)
           break
       except:
           continue  # May cause duplicates if first call is still processing
   ```

### ✅ **Prevention Strategies:**

1. **Response Deduplication in Assistant Logic:**
   ```python
   # GOOD: Check if response already provided
   if not hasattr(context, 'processed_requests'):
       context.processed_requests = set()
   
   request_key = f"epic_insights_{epic_key}"
   if request_key in context.processed_requests:
       return "Epic insights already being processed or provided."
   
   context.processed_requests.add(request_key)
   ```

2. **Caching for Expensive Operations:**
   ```python
   # GOOD: Simple in-memory cache for recent requests
   _epic_insights_cache = {}
   cache_expiry = 300  # 5 minutes

   async def fr_get_epic_insights(epic_key: Union[int, str], ...):
       cache_key = f"epic_{epic_key}_{project_id}"
       
       # Check cache first
       if cache_key in _epic_insights_cache:
           cached_result, timestamp = _epic_insights_cache[cache_key]
           if time.time() - timestamp < cache_expiry:
               logging.info(f"Returning cached epic insights for {epic_key}")
               return cached_result
       
       # Fetch new data
       result = await _fetch_epic_insights_internal(epic_key, ...)
       _epic_insights_cache[cache_key] = (result, time.time())
       return result
   ```

3. **Request Deduplication with Locks:**
   ```python
   # GOOD: Prevent concurrent calls to same resource
   _active_requests = {}

   async def fr_get_epic_insights(epic_key: Union[int, str], ...):
       request_key = f"epic_{epic_key}_{project_id}"
       
       # Check if already processing
       if request_key in _active_requests:
           logging.info(f"Epic insights for {epic_key} already in progress, waiting...")
           return await _active_requests[request_key]
       
       # Create new request
       async def _fetch():
           try:
               return await _fetch_epic_insights_internal(epic_key, ...)
           finally:
               _active_requests.pop(request_key, None)
       
       _active_requests[request_key] = asyncio.create_task(_fetch())
       return await _active_requests[request_key]
   ```

### 🔧 **Implementation Guidelines:**

1. **Add Request Tracking:**
   ```python
   @performance_monitor
   async def fr_get_epic_insights(epic_key: Union[int, str], ...):
       # Log unique request identifier
       request_id = f"epic_{epic_key}_{int(time.time())}"
       logging.info(f"Starting epic insights request: {request_id}")
       
       try:
           result = await _process_epic_insights(epic_key, ...)
           logging.info(f"Completed epic insights request: {request_id}")
           return result
       except Exception as e:
           logging.error(f"Failed epic insights request: {request_id} - {e}")
           raise
   ```

2. **Response Format Consistency:**
   ```python
   # GOOD: Always include metadata to identify duplicates
   return {
       "epic_details": epic_data,
       "ai_insights": insights,
       "request_metadata": {
           "epic_key": epic_key,
           "timestamp": datetime.utcnow().isoformat(),
           "request_id": request_id,
           "cached": False
       }
   }
   ```

### 📋 **Duplicate Prevention Checklist:**

Before implementing expensive operations:

- [ ] **Add request deduplication** for identical parameters
- [ ] **Implement caching** for frequently requested data
- [ ] **Add unique request IDs** for tracking
- [ ] **Log request start/completion** to identify duplicates
- [ ] **Use async locks** to prevent concurrent identical calls
- [ ] **Include metadata** in responses to identify cached vs fresh data
- [ ] **Test with rapid successive calls** to same resource

### 🎯 **Detection Commands:**

```bash
# Check for duplicate log entries
grep "Starting epic insights" logs/server.log | sort | uniq -c | sort -nr

# Monitor active requests
grep "already in progress" logs/server.log
```

### ⚠️ **Impact of Duplicates:**

- **Performance**: 2x API calls = 2x latency and resource usage
- **Rate Limits**: May hit API rate limits faster
- **User Experience**: Confusing duplicate responses
- **Cost**: Unnecessary compute and API costs for expensive operations like AI insights

**Remember**: For expensive operations like `fr_get_epic_insights`, always implement deduplication to prevent unnecessary API calls and improve user experience.

## 10. AI Insights Data Contamination Prevention

### Critical Issue: AI Insights Must Process Only API Data, Never Chat Content

AI insight generation functions like `_generate_epic_insights` and `_generate_testrun_insights` must process ONLY structured API data from Freshrelease, never chat content, conversation history, or user messages.

### 🚨 **Problem Scenario:**

```python
# BAD: Function receives contaminated data
def _generate_epic_insights(epic_details, child_tasks):
    # If child_tasks contains chat/conversation data instead of task objects,
    # the AI insights will summarize chat content instead of epic progress
    for task in child_tasks:  # This might contain chat messages!
        # Process what should be task data but is actually conversation content
```

**Result**: User gets "chat content summarized in cursor for epic insights" instead of actual task analysis.

### ✅ **Prevention Strategies:**

1. **Data Validation Before Processing:**
   ```python
   # GOOD: Validate input data structure
   def _generate_epic_insights(epic_details: Dict[str, Any], child_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
       """Generate AI insights for epic and tasks.
       
       CRITICAL: This function processes ONLY epic and task data from Freshrelease API.
       It should NEVER process chat content, conversation history, or user messages.
       """
       # Validate data type
       if not isinstance(child_tasks, list):
           logging.warning("Invalid data type received")
           return {"error": "Invalid task data format"}
       
       # Filter out non-task data
       valid_tasks = []
       for task in child_tasks:
           if isinstance(task, dict):
               task_data = task.get("issue", {}) if "issue" in task else task
               # Validate this looks like a Freshrelease task object
               if any(key in task_data for key in ["id", "title", "key", "display_id", "status"]):
                   valid_tasks.append(task)
               else:
                   logging.warning(f"Filtered out non-task data: {list(task_data.keys())[:3]}...")
   ```

2. **Explicit Data Source Confirmation:**
   ```python
   # GOOD: Add data source tracking
   return {
       "summary": summary,
       "insights": insights,
       "recommendations": recommendations,
       "data_source": "freshrelease_task_data_only"  # Confirms no chat content
   }
   ```

3. **Field-Specific Extraction:**
   ```python
   # GOOD: Extract only known Freshrelease API fields
   for task in valid_tasks:
       task_data = task.get("issue", {}) if "issue" in task else task
       
       # Only extract known Freshrelease task fields
       status = task_data.get("status", {})  # Freshrelease status object
       owner = task_data.get("owner", {})    # Freshrelease owner object
       priority = task_data.get("priority", {})  # Freshrelease priority object
       
       # Never process unstructured text that could be chat content
   ```

### 🔧 **Implementation Guidelines:**

1. **Always validate input data structure:**
   ```python
   # Check that we're receiving expected API response format
   if not all(isinstance(item, dict) for item in child_tasks):
       return {"error": "Invalid task data structure"}
   ```

2. **Use explicit field extraction:**
   ```python
   # BAD: Processing unknown/unstructured data
   for item in data:
       content = str(item)  # Could be chat content!
   
   # GOOD: Only extract known API fields
   for task in validated_tasks:
       task_data = task.get("issue", {})
       title = task_data.get("title", "")  # Known field
       status = task_data.get("status", {}).get("name", "")  # Known field
   ```

3. **Add protective logging:**
   ```python
   logging.info(f"Processing {len(valid_tasks)} valid tasks (filtered from {len(input_tasks)} items)")
   ```

### 📋 **AI Insights Quality Checklist:**

Before releasing AI insight functions:

- [ ] **Validate input data types** (Dict/List as expected)
- [ ] **Filter out non-API data** (chat, conversation, unstructured text)
- [ ] **Extract only known API fields** (status, owner, priority, etc.)
- [ ] **Add data source tracking** ("freshrelease_task_data_only")
- [ ] **Include protective logging** to identify data contamination
- [ ] **Test with edge cases** (empty data, malformed responses)
- [ ] **Document data expectations** clearly in docstrings

### 🎯 **Detection Commands:**

```bash
# Check for data contamination in logs
grep "Filtered out non-task data" logs/server.log

# Verify AI insights are processing task data only
grep "freshrelease_task_data_only" logs/server.log
```

### ⚠️ **Warning Signs:**

- AI insights mention chat/conversation content
- Insights reference user messages or commands
- Summary includes non-task related information
- Recommendations are about conversation flow instead of project progress

**Remember**: AI insights should analyze project data (tasks, epics, test runs) ONLY. Any mention of chat content, user messages, or conversation history indicates data contamination that must be fixed immediately.

## 11. Minimal AI Insights Principle

### Critical Rule: AI Insights Must Be Concise and Essential Only

AI insight functions should provide only the most essential information in a minimal format to reduce response size, improve performance, and focus on actionable insights.

### ✅ **Minimal Insights Structure:**

```python
# GOOD: Minimal epic insights
{
    "summary": "5/10 tasks completed.",
    "insight": "Needs attention.",
    "recommendation": "Prioritize task execution.",
    "data_source": "freshrelease_task_data_only"
}

# GOOD: Minimal test run insights  
{
    "summary": "23/25 tests executed. 2 failed.",
    "recommendation": "Fix failing tests.",
    "data_source": "freshrelease_testrun_data_only"
}

# GOOD: Minimal test case insights
{
    "summary": "Found 150 test cases.",
    "insight": "Partially automated.", 
    "recommendation": "Consider increasing automation.",
    "total_count": 150,
    "page_count": 50,
    "data_source": "freshrelease_testcase_data_only"
}
```

### ❌ **Avoid Verbose Insights:**

```python
# BAD: Too much detail and complexity
{
    "summary": "Epic 'User Authentication' contains 15 tasks with 60% completion rate across 3 different sections involving 4 team members with varying priority levels and git development status indicating active development...",
    "insights": [
        "Epic is progressing well (60% done).",
        "Development is active with recent commits.",
        "Team distribution shows good collaboration.",
        "High number of open PRs indicates ongoing work.",
        "Priority distribution requires attention."
    ],
    "recommendations": [
        "Monitor blockers and maintain momentum.",
        "Review open PRs for merge readiness.", 
        "Balance priority assignments across team.",
        "Consider additional testing resources."
    ],
    "risk_factors": ["Complex dependency chain", "Resource allocation concerns"],
    "metrics": {
        "completion_rate": "60%",
        "team_size": 4,
        "git_development": {"open_prs": 3, "recent_commits": 12}
    }
}
```

### 🎯 **Implementation Guidelines:**

1. **Single Summary Statement**: One clear, concise summary of current state
2. **Single Insight**: One key observation about the data
3. **Single Recommendation**: One actionable next step
4. **Essential Metadata**: Only critical counts and data source confirmation
5. **No Complex Metrics**: Avoid detailed breakdowns and nested analysis

### 📋 **Minimal Insights Checklist:**

For each AI insight function:

- [ ] **Summary is one sentence** (under 100 characters if possible)
- [ ] **Single insight statement** (not a list of insights)  
- [ ] **Single recommendation** (not multiple recommendations)
- [ ] **Essential data only** (total count, basic status)
- [ ] **No verbose metrics** (avoid detailed breakdowns)
- [ ] **Data source confirmation** included
- [ ] **Fast response time** (minimal processing overhead)

### ⚡ **Performance Benefits:**

- **Faster API responses** (less data processing)
- **Reduced memory usage** (smaller response payloads)
- **Better user experience** (quick, actionable insights)
- **Lower computational cost** (minimal analysis complexity)

**Remember**: Users need quick, actionable insights, not comprehensive reports. Keep AI insights minimal, focused, and immediately actionable.

---

*This guide should be updated whenever new patterns or conventions are established in the project.*
