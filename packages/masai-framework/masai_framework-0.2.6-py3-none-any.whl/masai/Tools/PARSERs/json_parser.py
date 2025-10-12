import json
import re
import logging

# Setup logger for JSON parser
logger = logging.getLogger(__name__)

def repair_json_string(json_str: str) -> str:
    """
    Attempt to repair common JSON string issues:
    1. Invalid escape sequences (\' which is not valid JSON)
    2. Unescaped control characters (actual newlines, tabs, etc.)
    3. Missing closing brackets/braces

    Uses a stack-based approach to determine the correct order of closing characters.

    Args:
        json_str: Potentially malformed JSON string

    Returns:
        Repaired JSON string
    """
    # Remove leading/trailing whitespace
    json_str = json_str.strip()

    repairs_made = []

    # Fix 0: Escape unescaped control characters inside JSON strings
    # JSON spec requires control characters (0x00-0x1F) to be escaped
    # Common issue: LLM generates actual newlines instead of \n
    #
    # IMPORTANT: We need to be very careful here because:
    # 1. The JSON might contain Python code with nested quotes
    # 2. We don't want to break the JSON structure
    # 3. We only want to escape ACTUAL control characters (not \n sequences)
    #
    # Strategy: Use a character-by-character approach with proper state tracking
    def escape_control_chars_safe(json_str):
        """Safely escape actual control characters in JSON string"""
        result = []
        in_string = False
        escape_next = False

        for i, char in enumerate(json_str):
            if escape_next:
                # Previous char was backslash, keep this char as-is
                result.append(char)
                escape_next = False
                continue

            if char == '\\':
                # Start of escape sequence
                result.append(char)
                escape_next = True
                continue

            if char == '"':
                # Toggle string state
                in_string = not in_string
                result.append(char)
                continue

            # If we're inside a string and encounter a control character, escape it
            if in_string and ord(char) < 0x20:
                if char == '\n':
                    result.append('\\n')
                elif char == '\r':
                    result.append('\\r')
                elif char == '\t':
                    result.append('\\t')
                elif char == '\b':
                    result.append('\\b')
                elif char == '\f':
                    result.append('\\f')
                else:
                    # Other control characters - escape as unicode
                    result.append(f'\\u{ord(char):04x}')
            else:
                result.append(char)

        return ''.join(result)

    # Try to escape control characters safely
    try:
        # ALWAYS run the escape function if there are ANY control characters
        # The function is smart enough to only escape actual control chars, not escape sequences
        has_control_chars = any(ord(c) < 0x20 for c in json_str)

        if has_control_chars:
            json_str = escape_control_chars_safe(json_str)
            repairs_made.append("escaped control characters")
    except Exception as e:
        logger.warning(f"Failed to escape control characters: {e}")

    # Fix 1: Handle invalid escape sequences carefully
    # \' is not a valid JSON escape sequence (only \" \\ \/ \b \f \n \r \t \uXXXX are valid)
    #
    # The LLM sometimes generates: {"code": "db[\'tasks\']"}
    # This is INVALID JSON because \' is not a valid escape sequence
    # It should be: {"code": "db['tasks']"} (no escape needed for single quotes in JSON)
    #
    # Strategy: Remove the backslash before single quotes ONLY when inside JSON string values
    def fix_invalid_escapes(json_str):
        """Remove invalid escape sequences like \' from JSON strings"""
        result = []
        in_string = False
        escape_next = False
        i = 0

        while i < len(json_str):
            char = json_str[i]

            if escape_next:
                # Previous char was backslash
                if char == "'":
                    # \' is invalid in JSON - just keep the quote, drop the backslash
                    result.append("'")
                else:
                    # Valid escape sequence - keep both backslash and char
                    result.append(char)
                escape_next = False
                i += 1
                continue

            if char == '\\' and in_string:
                # Check if next char is a single quote
                if i + 1 < len(json_str) and json_str[i + 1] == "'":
                    # Don't add the backslash yet, mark for next iteration
                    escape_next = True
                    i += 1
                    continue
                else:
                    # Valid escape sequence
                    result.append(char)
            elif char == '"':
                # Toggle string state
                in_string = not in_string
                result.append(char)
            else:
                result.append(char)

            i += 1

        return ''.join(result)

    # Try to fix invalid escape sequences
    try:
        if "\\'" in json_str:
            json_str = fix_invalid_escapes(json_str)
            repairs_made.append("fixed invalid escape sequences")
    except Exception as e:
        logger.warning(f"Failed to fix invalid escape sequences: {e}")

    # Fix 2: Use a stack to track opening brackets/braces and determine what's missing
    stack = []
    for char in json_str:
        if char in ('{', '['):
            stack.append(char)
        elif char == '}':
            if stack and stack[-1] == '{':
                stack.pop()
        elif char == ']':
            if stack and stack[-1] == '[':
                stack.pop()

    # If stack is not empty, we have unclosed brackets/braces
    if stack:
        # Add closing characters in reverse order
        closing_chars = []
        for open_char in reversed(stack):
            if open_char == '{':
                closing_chars.append('}')
            elif open_char == '[':
                closing_chars.append(']')

        json_str = json_str + ''.join(closing_chars)
        repairs_made.append(f"added {len(closing_chars)} closing character(s): {''.join(closing_chars)}")

    if repairs_made:
        logger.warning(f"Repaired JSON string: {'; '.join(repairs_made)}")

    return json_str


def clean_input(text):
    """
    Cleans the input text to make it more JSON-compliant.
    - Replaces single quotes with double quotes.
    - Handles boolean values (True/False) and None.
    """
    # Replace single quotes with double quotes
    text = text.replace("'", '"')

    # Replace Python-style booleans and None with JSON-compatible values
    text = re.sub(r'\bTrue\b', 'true', text)
    text = re.sub(r'\bFalse\b', 'false', text)
    text = re.sub(r'\bNone\b', 'null', text)

    return text

def extract_delimited_content(text, start_delimiter, end_delimiter):
    """
    Extract content between delimiters.

    Args:
        text: Input text containing delimited content
        start_delimiter: Opening delimiter (e.g., '<PYTHON>')
        end_delimiter: Closing delimiter (e.g., '</PYTHON>')

    Returns:
        Extracted content (without delimiters), or None if not found

    Example:
        text = 'code: <PYTHON>print("hello")</PYTHON>'
        extract_delimited_content(text, '<PYTHON>', '</PYTHON>')
        # Returns: 'print("hello")'
    """
    # Escape special regex characters in delimiters
    start_pattern = re.escape(start_delimiter)
    end_pattern = re.escape(end_delimiter)

    # Create pattern to match content between delimiters
    # re.DOTALL makes . match newlines too
    pattern = rf'{start_pattern}(.*?){end_pattern}'

    match = re.search(pattern, text, re.DOTALL)
    if match:
        content = match.group(1)
        # Strip leading/trailing whitespace (but preserve internal formatting)
        return content.strip()

    return None


def parse_json_with_delimiters(text):
    """
    Parse JSON that may contain delimited content (e.g., <PYTHON>code</PYTHON>).

    This function:
    1. Extracts delimited content (e.g., code between <PYTHON></PYTHON>)
    2. Replaces it with a placeholder in the JSON
    3. Parses the JSON
    4. Restores the delimited content

    Supported delimiters:
    - <PYTHON>...</PYTHON> for Python code
    - <SQL>...</SQL> for SQL queries
    - <CODE>...</CODE> for generic code

    Handles both formats:
    - Without quotes: {"code": <PYTHON>...</PYTHON>}
    - With quotes: {"code": "<PYTHON>...</PYTHON>"}

    Args:
        text: Input text containing JSON with possible delimited content

    Returns:
        Parsed dictionary with delimited content restored

    Example:
        Input: '{"code": <PYTHON>print("hello")</PYTHON>, "query": "test"}'
        Output: {"code": 'print("hello")', "query": "test"}
    """
    # Define supported delimiters
    delimiters = [
        ('<PYTHON>', '</PYTHON>'),
        ('<SQL>', '</SQL>'),
        ('<CODE>', '</CODE>'),
    ]

    # Store extracted content
    extracted_content = {}
    modified_text = text

    # Extract all delimited content and replace with placeholders
    for start_delim, end_delim in delimiters:
        delimiter_type = start_delim.strip('<>')
        counter = 0

        while True:
            content = extract_delimited_content(modified_text, start_delim, end_delim)
            if content is None:
                break

            # Create unique placeholder
            placeholder = f'__DELIMITED_{delimiter_type}_{counter}__'
            extracted_content[placeholder] = content

            # Replace delimited content with placeholder
            # Handle both quoted and unquoted delimiters:
            # 1. "<PYTHON>...</PYTHON>" (with quotes)
            # 2. <PYTHON>...</PYTHON> (without quotes)
            pattern = re.escape(start_delim) + r'.*?' + re.escape(end_delim)

            # Check if delimiter is inside quotes
            # Pattern: "delimiter...content...delimiter"
            quoted_pattern = r'"' + pattern + r'"'
            if re.search(quoted_pattern, modified_text, re.DOTALL):
                # Replace quoted delimiter with placeholder (keep quotes)
                modified_text = re.sub(quoted_pattern, f'"{placeholder}"', modified_text, count=1, flags=re.DOTALL)
            else:
                # Replace unquoted delimiter with placeholder (add quotes)
                modified_text = re.sub(pattern, f'"{placeholder}"', modified_text, count=1, flags=re.DOTALL)

            counter += 1

    # Now parse the modified JSON (with placeholders)
    try:
        parsed = json.loads(modified_text)
    except json.JSONDecodeError as e:
        # Try to repair and parse
        logger.warning(f"Initial JSON parsing failed: {e}. Attempting repair...")
        try:
            repaired = repair_json_string(modified_text)
            parsed = json.loads(repaired)
            logger.info(f"Successfully parsed repaired JSON string")
        except json.JSONDecodeError as repair_error:
            raise ValueError(f"Failed to parse JSON. Original error: {e}. Repair attempt also failed: {repair_error}")

    # Restore delimited content
    def restore_content(obj):
        """Recursively restore delimited content in parsed object"""
        if isinstance(obj, dict):
            return {k: restore_content(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [restore_content(item) for item in obj]
        elif isinstance(obj, str):
            # Check if this is a placeholder
            if obj in extracted_content:
                content = extracted_content[obj]

                # CRITICAL FIX: The content was extracted BEFORE JSON parsing,
                # but json.loads() decodes escape sequences in the placeholder.
                #
                # Example flow:
                # 1. LLM generates: {"code": "<PYTHON>f'''text\\n\\n{var}'''</PYTHON>"}
                # 2. We extract: f'''text\\n\\n{var}''' (with \\n)
                # 3. We replace with placeholder: {"code": "__DELIMITED_PYTHON_0__"}
                # 4. json.loads() parses this - placeholder is fine
                # 5. We restore content: f'''text\\n\\n{var}''' (still with \\n)
                #
                # BUT if LLM generates actual newlines:
                # 1. LLM generates: {"code": "<PYTHON>f'''text\n\n{var}'''</PYTHON>"} (actual newlines)
                # 2. repair_json_string() escapes them: {"code": "<PYTHON>f'''text\\n\\n{var}'''</PYTHON>"}
                # 3. We extract: f'''text\\n\\n{var}''' (with \\n - looks good!)
                # 4. We replace with placeholder: {"code": "__DELIMITED_PYTHON_0__"}
                # 5. json.loads() parses - placeholder is fine
                # 6. We restore content: f'''text\\n\\n{var}''' (with \\n - still good!)
                #
                # So actually, the content should be correct as-is!
                # The issue must be elsewhere...

                return content
            return obj
        else:
            return obj

    return restore_content(parsed)


def parse_json(text):
    """
    Attempts to parse the cleaned text as JSON with automatic repair for malformed JSON.

    This function now supports:
    1. Standard JSON parsing
    2. JSON with delimited content (e.g., <PYTHON>code</PYTHON>)
    3. Automatic repair for common JSON issues

    Returns a dictionary if successful, otherwise raises an error.
    """
    # First, check if text contains delimiters
    has_delimiters = any(delim in text for delim in ['<PYTHON>', '<SQL>', '<CODE>'])

    if has_delimiters:
        # Use delimiter-aware parsing
        try:
            return parse_json_with_delimiters(text)
        except Exception as e:
            logger.warning(f"Delimiter-based parsing failed: {e}. Falling back to standard parsing...")

    # Standard JSON parsing (with repair)
    try:
        # First attempt: direct parsing
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Second attempt: try to repair and parse
        logger.warning(f"Initial JSON parsing failed: {e}. Attempting repair...")
        try:
            repaired = repair_json_string(text)
            result = json.loads(repaired)
            logger.info(f"Successfully parsed repaired JSON string")
            return result
        except json.JSONDecodeError as repair_error:
            raise ValueError(f"Failed to parse JSON. Original error: {e}. Repair attempt also failed: {repair_error}")

def parse_task_string(task_str: str) -> list[str]:
    """
    Parses a comma-separated string of quoted tasks into individual tasks.
    Handles commas within task descriptions and varying quotation marks.
    
    Args:
        task_str: Input string containing tasks (e.g. '"task 1", "task 2, with comma"')
        
    Returns:
        List of cleaned task strings
    """
    # Remove surrounding brackets if present
    cleaned = task_str.strip('[]')
    
    # Split on commas followed by optional whitespace and a quote
    task_split = re.split(r',(?=\s*["\'])', cleaned)
    
    # Clean whitespace and quotes from each task
    return [task.strip(' "\'') for task in task_split]


def handle_tool_input(parsed_dict):
    """
    Ensures that 'tool_input' in the parsed dictionary is always a valid dictionary.
    If 'tool_input' is not a dictionary, attempts to parse it into one with automatic repair.
    """
    if "tool_input" in parsed_dict:
        if isinstance(parsed_dict["tool_input"], str):
            try:
                # First attempt: direct parsing
                parsed_dict["tool_input"] = json.loads(parsed_dict["tool_input"])
            except json.JSONDecodeError as e:
                # Second attempt: try to repair and parse
                logger.warning(f"tool_input JSON parsing failed: {e}. Attempting repair...")
                try:
                    repaired = repair_json_string(parsed_dict["tool_input"])
                    parsed_dict["tool_input"] = json.loads(repaired)
                    logger.info(f"Successfully parsed repaired tool_input JSON string")
                except json.JSONDecodeError as repair_error:
                    raise ValueError(
                        f"Invalid tool_input format: {parsed_dict['tool_input']}. "
                        f"Original error: {e}. Repair attempt also failed: {repair_error}"
                    )
        elif not isinstance(parsed_dict["tool_input"], dict):
            raise ValueError(f"tool_input must be a dictionary or valid JSON string, got: {type(parsed_dict['tool_input'])}")

    return parsed_dict

def parser(stream):
    # Step 1: Clean the input
    cleaned_text = clean_input(stream)

    # Step 2: Parse the cleaned text into a dictionary
    parsed_dict = parse_json(cleaned_text)

    # Step 3: Handle tool_input field specifically
    parsed_dict = handle_tool_input(parsed_dict)

    return parsed_dict

def parse_tool_input(tool_input:dict, fields):
    """
    Parses `tool_input` according to the provided fields, handling various formats and edge cases.

    Parameters:
    tool_input (str or dict): The input to parse. It can be a dictionary, a JSON-like string, or a raw string.
    fields (list): List of field names to extract.

    Returns:
    dict: A dictionary containing the parsed data for the specified fields.

    Flow:
    1. If tool_input is already a dict → Direct field extraction (fast path)
    2. If tool_input is a string → Try to parse as JSON first, then fall back to regex
    """

    def clean_text(text):
        """Cleans and normalizes the input text."""
        return text.strip().replace("\\'", "'").replace('\\"', '"')

    def parse_json_like(text):
        """
        Attempts to parse a JSON-like string. Handles various quote styles and ensures nested quotes are replaced.
        """
        def replace_quotes(s):
            state = {'in_string': False, 'quote_char': None}
            result = []
            i = 0
            while i < len(s):
                if s[i] in ['"', "'"]:
                    if not state['in_string']:
                        state['in_string'] = True
                        state['quote_char'] = s[i]
                        result.append('"')
                    elif state['quote_char'] == s[i]:
                        state['in_string'] = False
                        result.append('"')
                    else:
                        result.append(s[i])
                elif s[i] == '\\' and i + 1 < len(s):
                    result.append(s[i:i+2])
                    i += 1
                else:
                    result.append(s[i])
                i += 1
            return ''.join(result)

        try:
            # Replace quotes and safely parse the modified string
            processed_text = replace_quotes(text)
            return json.loads(processed_text)
        except json.JSONDecodeError:
            return None


    def extract_field_value(data, field):
        """
        Extracts the value for a single field from the input data.
        Handles quoted values, JSON-like structures, unquoted key-value pairs, and boolean values.

        CRITICAL: This function must preserve the ENTIRE value without truncation.
        Common issue: Multi-line strings with escape sequences (\\n, \\t, etc.) getting truncated.
        """
        # If data is already a dict, extract field directly
        if isinstance(data, dict):
            if field in data:
                value = data[field]
                # If value is a JSON string, try to parse it with repair
                if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        # Try to repair and parse
                        try:
                            repaired = repair_json_string(value)
                            return json.loads(repaired)
                        except json.JSONDecodeError:
                            # Return as string if repair fails
                            return value
                return value
            return None

        # If `data` is not a string at this point, return an error
        if not isinstance(data, str):
            return None

        # SPECIAL CASE: Handle malformed JSON with mixed quotes (common in LLM-generated code)
        # Example: {"code": "x = db['clients'].find({'key': 'value'})", "other": "value"}
        # Standard JSON parsing fails because single quotes inside double quotes aren't escaped
        # Strategy: Find the field, then extract everything until we find the next field or closing brace
        if '"' + field + '"' in data or "'" + field + "'" in data:
            # Try to find the field and extract its value manually
            # Pattern: "field": "value" or "field": 'value'
            # We need to find the opening quote after the colon, then find the matching closing quote
            # accounting for escaped quotes

            # Find the field position
            field_pattern = rf'["\']?{re.escape(field)}["\']?\s*:\s*'
            field_match = re.search(field_pattern, data)
            if field_match:
                start_pos = field_match.end()
                # Check what comes after the colon
                if start_pos < len(data):
                    first_char = data[start_pos]

                    if first_char in ['"', "'"]:
                        # It's a quoted string - find the matching closing quote
                        # We need to handle escaped quotes and mixed quotes
                        quote_char = first_char
                        value_start = start_pos + 1
                        i = value_start
                        value_chars = []

                        # Track if we're in an escape sequence
                        escape_next = False

                        while i < len(data):
                            current_char = data[i]

                            if escape_next:
                                # Previous character was a backslash, so this character is escaped
                                # Include it as-is (already have the backslash in value_chars)
                                value_chars.append(current_char)
                                escape_next = False
                                i += 1
                            elif current_char == '\\':
                                # Start of an escape sequence
                                value_chars.append(current_char)
                                escape_next = True
                                i += 1
                            elif current_char == quote_char:
                                # Found an unescaped quote that matches our opening quote
                                # Check if this is the closing quote by looking ahead
                                # The closing quote should be followed by:
                                # - End of string
                                # - Comma, brace, bracket (JSON delimiters)
                                # - Whitespace followed by comma/brace/bracket
                                if i + 1 >= len(data):
                                    # End of string - this is the closing quote
                                    value = ''.join(value_chars)
                                    logger.debug(f"Extracted field '{field}' value (length: {len(value)})")
                                    return value

                                next_char = data[i + 1]
                                # Check if followed by JSON delimiter
                                if next_char in [',', '}', ']']:
                                    # This is the closing quote
                                    value = ''.join(value_chars)
                                    logger.debug(f"Extracted field '{field}' value (length: {len(value)})")
                                    return value
                                # Check if followed by whitespace then delimiter
                                elif next_char in [' ', '\n', '\t', '\r']:
                                    # Look ahead to see if there's a delimiter after whitespace
                                    j = i + 1
                                    while j < len(data) and data[j] in [' ', '\n', '\t', '\r']:
                                        j += 1
                                    if j >= len(data) or data[j] in [',', '}', ']']:
                                        # This is the closing quote
                                        value = ''.join(value_chars)
                                        logger.debug(f"Extracted field '{field}' value (length: {len(value)})")
                                        return value
                                    else:
                                        # Not the closing quote, include it in the value
                                        value_chars.append(current_char)
                                        i += 1
                                else:
                                    # Not followed by delimiter, so this quote is part of the value
                                    value_chars.append(current_char)
                                    i += 1
                            else:
                                # Regular character, include it
                                value_chars.append(current_char)
                                i += 1

                        # If we got here, we didn't find a closing quote
                        # Return what we have
                        value = ''.join(value_chars)
                        logger.warning(f"No closing quote found for field '{field}', returning partial value (length: {len(value)})")
                        return value

        # Define patterns to match different value formats
        # Note: These patterns are fallback for when JSON parsing fails
        # The optimized flow tries JSON parsing first (which handles all cases correctly)
        # IMPORTANT: These patterns must NOT truncate the value
        patterns = [
            # Python-style key=value patterns (for LLM-generated tool inputs)
            rf'{field}\s*=\s*"""(.*?)"""',              # Triple double-quoted value (Python docstring style)
            rf"{field}\s*=\s*'''(.*?)'''",              # Triple single-quoted value (Python docstring style)
            rf'{field}\s*=\s*"((?:[^"\\]|\\.)*)"',      # Double-quoted value (Python style)
            rf"{field}\s*=\s*'((?:[^'\\]|\\.)*)'",      # Single-quoted value (Python style)

            # JSON-style key:value patterns (standard)
            # CRITICAL: These patterns must capture the ENTIRE value including escape sequences
            # The pattern ((?:[^"\\]|\\.)*)  means: match any char that's not " or \, OR match \ followed by any char
            # This correctly handles escape sequences like \n, \t, \", \\, etc.
            rf'"{field}"\s*:\s*"((?:[^"\\]|\\.)*)"',    # Double-quoted value (handles ALL escaped chars)
            rf"'{field}'\s*:\s*'((?:[^'\\]|\\.)*)'",    # Single-quoted value (handles ALL escaped chars)
            rf'"{field}"\s*:\s*(\{{[^}}]*\}})',         # JSON-like dictionary (simple, no nesting)
            rf'"{field}"\s*:\s*(\[[^\]]*\])',           # JSON-like list (simple, no nesting)
            rf'"{field}"\s*:\s*(true|false)',           # Boolean values (JSON-style)
            rf'"{field}"\s*:\s*(null)',                 # Null values (JSON-style)
            rf'"{field}"\s*:\s*(\d+\.?\d*)',            # Numbers (int or float)
            rf'"{field}"\s*:\s*([^\s,\}}]+)'            # Unquoted value (general case, stops at comma or brace)
        ]

        # Apply patterns to extract the value
        for pattern in patterns:
            match = re.search(pattern, data, re.DOTALL)
            if match:
                value = next((g for g in match.groups() if g is not None), None)
                if value:
                    # Convert JSON values to Python equivalents (EXACT match only, not substring)
                    if value.lower() == 'true':
                        return True
                    if value.lower() == 'false':
                        return False
                    if value.lower() == 'null':
                        return None
                    if (value.startswith('{') and value.endswith('}')) or (value.startswith('[') and value.endswith(']')):
                        try:
                            return json.loads(value)
                        except json.JSONDecodeError:
                            # Try to repair and parse
                            try:
                                repaired = repair_json_string(value)
                                return json.loads(repaired)
                            except json.JSONDecodeError:
                                pass
                    # Handle incomplete JSON objects/arrays (missing closing braces/brackets)
                    elif value.startswith('{') or value.startswith('['):
                        try:
                            repaired = repair_json_string(value)
                            return json.loads(repaired)
                        except json.JSONDecodeError:
                            pass

                    # Return the value as-is (don't strip quotes - they're already removed by regex)
                    logger.debug(f"Extracted field '{field}' using pattern match (length: {len(value)})")
                    return value


        return None

    def extract_fields(data, fields):
        """
        Extracts values for the specified fields from the input data.
        Handles cases where `tool_input` is a serialized JSON string or a dictionary.
        """
        result={field: extract_field_value(data, field) for field in fields}
        # print(result)
        for field in fields:
            if field not in result.keys():
                # print(field)
                result[field] = None
        return result

    # OPTIMIZATION: If tool_input is a string, try to parse it as JSON first
    # This converts it to a dict, which uses the fast path in extract_field_value
    if isinstance(tool_input, str):
        try:
            # Try direct JSON parsing
            tool_input = json.loads(tool_input)
            logger.info("Successfully parsed tool_input string as JSON")
        except json.JSONDecodeError as e:
            logger.warning(f"Initial JSON parsing failed: {e}")

            # Try with repair
            try:
                repaired = repair_json_string(tool_input)
                tool_input = json.loads(repaired)
                logger.info("Successfully parsed repaired tool_input string as JSON")
            except json.JSONDecodeError as repair_error:
                # Try one more time with aggressive cleaning
                try:
                    # Remove any leading/trailing whitespace and quotes
                    cleaned = tool_input.strip().strip('"').strip("'")
                    # Try parsing the cleaned version
                    tool_input = json.loads(cleaned)
                    logger.info("Successfully parsed cleaned tool_input string as JSON")
                except json.JSONDecodeError:
                    # Try fixing mixed quotes (single quotes inside double-quoted strings)
                    try:
                        # This is a common issue when LLM generates code with single quotes
                        # inside double-quoted JSON strings
                        # Strategy: Don't use json.loads at all, go straight to field extraction
                        # which handles this case better
                        logger.warning(f"Failed to parse tool_input as JSON after all attempts. Original error: {e}, Repair error: {repair_error}. Using direct field extraction")
                        logger.warning(f"tool_input preview (first 200 chars): {tool_input[:200]}")
                        # Don't pass - let it fall through to extract_fields which will handle the string
                    except Exception:
                        pass

    try:
        parsed_tool_input = extract_fields(tool_input, fields)

        # Log the parsed values for debugging
        for field in fields:
            if field in parsed_tool_input and parsed_tool_input[field] is not None:
                value = parsed_tool_input[field]
                if isinstance(value, str):
                    logger.debug(f"Parsed field '{field}': length={len(value)}, preview={value[:100]}...")
                else:
                    logger.debug(f"Parsed field '{field}': type={type(value).__name__}")

        return parsed_tool_input
    except Exception as e:
        logger.error(f"Error parsing tool input: {e}", exc_info=True)
        return None