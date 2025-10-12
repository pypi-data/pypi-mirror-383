"""Core utilities: Helpers for requesting JSON from LLM.
"""
from __future__ import annotations
import json
import re
import requests
import sys
import warnings
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, Type, Optional, List, Union

from pydantic import BaseModel, Field

from .drivers import get_driver, get_driver_for_model
from .driver import Driver
from .tools import create_field_schema, convert_value, log_debug, clean_json_text, LogLevel, get_field_default
from .field_definitions import get_registry_snapshot


def normalize_field_value(value: Any, field_type: Type, field_def: Dict[str, Any]) -> Any:
    """Normalize invalid values for fields based on their type and nullable status.
    
    This function handles post-processing of extracted values BEFORE Pydantic validation,
    converting invalid values (like empty strings for booleans) to proper defaults.
    
    Args:
        value: The extracted value from the LLM
        field_type: The expected Python type for this field
        field_def: The field definition dict containing nullable, default, etc.
    
    Returns:
        A normalized value suitable for the field type
    """
    nullable = field_def.get("nullable", True)
    default_value = field_def.get("default")
    
    # Special handling for boolean fields
    if field_type is bool or (hasattr(field_type, '__origin__') and field_type.__origin__ is bool):
        # If value is already a boolean, return it as-is
        if isinstance(value, bool):
            return value
        
        # For non-nullable booleans
        if not nullable:
            # Any non-empty string should be True, empty/None should be default
            if isinstance(value, str):
                return bool(value.strip()) if value.strip() else (default_value if default_value is not None else False)
            if value in (None, [], {}):
                return default_value if default_value is not None else False
            # Try to coerce other types
            return bool(value) if value else (default_value if default_value is not None else False)
        else:
            # For nullable booleans, preserve None
            if value is None:
                return None
            if isinstance(value, str):
                return bool(value.strip()) if value.strip() else None
            return bool(value) if value else None
    
    # If the field is nullable and value is None, that's acceptable
    if nullable and value is None:
        return value
    
    # For non-nullable fields with invalid values, use the default
    if not nullable:
        # Check for invalid values that should be replaced
        invalid_values = (None, "", [], {})
        
        if value in invalid_values or (isinstance(value, str) and not value.strip()):
            # Use the default value if provided, otherwise use type-appropriate default
            if default_value is not None:
                return default_value
            
            # Type-specific defaults for non-nullable fields
            if field_type is int or (hasattr(field_type, '__origin__') and field_type.__origin__ is int):
                return 0
            elif field_type is float or (hasattr(field_type, '__origin__') and field_type.__origin__ is float):
                return 0.0
            elif field_type is str or (hasattr(field_type, '__origin__') and field_type.__origin__ is str):
                return ""
            elif field_type is list or (hasattr(field_type, '__origin__') and field_type.__origin__ is list):
                return []
            elif field_type is dict or (hasattr(field_type, '__origin__') and field_type.__origin__ is dict):
                return {}
    
    return value


def clean_json_text_with_ai(driver: Driver, text: str, model_name: str = "", options: Dict[str, Any] = {}) -> str:
    """Use LLM to fix malformed JSON strings.

    Generates a specialized prompt instructing the LLM to correct the
    provided text into valid JSON.

    Args:
        driver: Active LLM driver used to send the correction request.
        text: Malformed JSON string to be corrected.
        options: Additional options passed to the driver.

    Returns:
        A cleaned string that should contain valid JSON.
    """
    # Check if JSON is already valid - if so, return unchanged
    try:
        json.loads(text)
        return text  # Already valid, no need for LLM correction
    except json.JSONDecodeError:
        pass  # Invalid, proceed with LLM correction
    
    prompt = (
        "The following text is supposed to be a single JSON object, but it is malformed. "
        "Please correct it and return only the valid JSON object. Do not add any explanations or markdown. "
        f"The text to correct is:\n\n{text}"
    )
    resp = driver.generate(prompt, options)
    raw = resp.get("text", "")
    cleaned = clean_json_text(raw)
    return cleaned

def ask_for_json(
    driver: Driver,
    content_prompt: str,
    json_schema: Dict[str, Any],
    ai_cleanup: bool = True,
    model_name: str = "",
    options: Dict[str, Any] = {},
) -> Dict[str, Any]:
    """Sends a prompt to the driver and returns both JSON output and usage metadata.

    This function enforces a schema-first approach by requiring a json_schema parameter
    and automatically generating instructions for the LLM to return valid JSON matching the schema.

    Args:
        driver: Adapter that implements generate(prompt, options).
        content_prompt: Main prompt content (may include examples).
        json_schema: Required JSON schema dictionary defining the expected structure.
        ai_cleanup: Whether to attempt AI-based cleanup if JSON parsing fails.
        options: Additional options to pass to the driver.
        verbose_level: Logging level for debug output (LogLevel.OFF by default).

    Returns:
        A dictionary containing:
        - json_string: the JSON string output.
        - json_object: the parsed JSON object.
        - usage: token usage and cost information from the driver's meta object.

    Raises:
        json.JSONDecodeError: If the response cannot be parsed as JSON and ai_cleanup is False.
    """

    schema_string = json.dumps(json_schema, indent=2)
    instruct = (
        "Return only a single JSON object (no markdown, no extra text) that validates against this JSON schema:\n"
        f"{schema_string}\n\n"
        "If a value is unknown use null. Use double quotes for keys and strings."
    )
    full_prompt = f"{content_prompt}\n\n{instruct}"
    resp = driver.generate(full_prompt, options)
    raw = resp.get("text", "")
    cleaned = clean_json_text(raw)

    try:
        json_obj = json.loads(cleaned)
        usage = {
            **resp.get("meta", {}),
            "raw_response": resp,
            "total_tokens": resp.get("meta", {}).get("total_tokens", 0),
            "prompt_tokens": resp.get("meta", {}).get("prompt_tokens", 0),
            "completion_tokens": resp.get("meta", {}).get("completion_tokens", 0),
            "cost": resp.get("meta", {}).get("cost", 0.0),
            "model_name": model_name or getattr(driver, "model", "")
        }
        return {
            "json_string": cleaned,
            "json_object": json_obj,
            "usage": usage
        }
    except json.JSONDecodeError as e:
        if ai_cleanup:
            cleaned_fixed = clean_json_text_with_ai(driver, cleaned, model_name, options)
            try:
                json_obj = json.loads(cleaned_fixed)
                return {
                    "json_string": cleaned_fixed,
                    "json_object": json_obj,
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0,
                        "cost": 0.0,
                        "model_name": options.get("model", getattr(driver, "model", "")),
                        "raw_response": {}
                    },
                }
            except json.JSONDecodeError:
                # Re-raise the original JSONDecodeError
                raise e
        else:
            # Explicitly re-raise the original JSONDecodeError
            raise e

def extract_and_jsonify(
    text: Union[str, Driver],  # Can be either text or driver for backward compatibility
    json_schema: Dict[str, Any],
    *,  # Force keyword arguments for remaining params
    model_name: Union[str, Dict[str, Any]] = "",  # Can be schema (old) or model name (new)
    instruction_template: str = "Extract information from the following text:",
    ai_cleanup: bool = True,
    options: Dict[str, Any] = {},
) -> Dict[str, Any]:
    """Extracts structured information using automatic driver selection based on model name.
    
    Args:
        text: The raw text to extract information from.
        json_schema: JSON schema dictionary defining the expected structure.
        model_name: Model identifier in format "provider/model" (e.g., "openai/gpt-4-turbo-preview").
        instruction_template: Instructional text to prepend to the content.
        ai_cleanup: Whether to attempt AI-based cleanup if JSON parsing fails.
        options: Additional options to pass to the driver.
    
    Returns:
        A dictionary containing:
        - json_string: the JSON string output.
        - json_object: the parsed JSON object.
        - usage: token usage and cost information from the driver's meta object.
    
    Raises:
        ValueError: If text is empty or None, or if model_name format is invalid.
        json.JSONDecodeError: If the response cannot be parsed as JSON and ai_cleanup is False.
        pytest.skip: If a ConnectionError occurs during testing (when pytest is running).
    """
    # Handle legacy format where first argument is driver
    # Validate text input first
    if isinstance(text, Driver):
        driver = text
        actual_text = json_schema
        actual_schema = model_name
        actual_model = options.pop("model", "") or getattr(driver, "model", "")
        options.pop("model_name", None)
    else:
        # New format
        if not isinstance(text, str):
            raise ValueError("Text input must be a string")
        if not text or not text.strip():
            raise ValueError("Text input cannot be empty")
        actual_text = text
        actual_schema = json_schema
        actual_template = instruction_template
        actual_model = model_name or options.get("model", "")
        driver = options.pop("driver", None)

    # Get driver if not provided
    if driver is None:
        if not actual_model:
            raise ValueError("Model name cannot be empty")
            
        # First validate model format
        if "/" not in actual_model:
            raise ValueError("Invalid model string format. Expected format: 'provider/model'")
            
        try:
            driver = get_driver_for_model(actual_model)
        except ValueError as e:
            if "Unsupported provider" in str(e):
                raise ValueError(f"Unsupported provider in model name: {actual_model}")
            raise  # Re-raise any other ValueError
    
    # Extract model parts for other validation
    try:
        provider, model_id = actual_model.split("/", 1)
        if not provider:
            raise ValueError("Provider cannot be empty in model name")
    except ValueError:
        # If no "/" in model string, use entire string as both provider and model_id
        provider = model_id = actual_model
        
    opts = {**options, "model": model_id}
    
    content_prompt = f"{actual_template} {actual_text}"
    
    try:
        return ask_for_json(driver, content_prompt, actual_schema, ai_cleanup, model_id, opts)
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        if "pytest" in sys.modules:
            import pytest
            pytest.skip(f"Connection error occurred: {e}")
        raise ConnectionError(f"Connection error occurred: {e}")

def manual_extract_and_jsonify(
    driver: Driver,
    text: str,
    json_schema: Dict[str, Any],
    model_name: str = "",
    instruction_template: str = "Extract information from the following text:",
    ai_cleanup: bool = True,
    options: Dict[str, Any] = {},
    verbose_level: LogLevel | int = LogLevel.OFF,
) -> Dict[str, Any]:
    """Extracts structured information using an explicitly provided driver.

    This variant is useful when you want to directly control which driver
    is used (e.g., OpenAI, Azure, Ollama, LocalHTTP) and optionally override
    the model per call.

    Args:
        driver: The LLM driver instance to use.
        text: The raw text to extract information from.
        json_schema: JSON schema dictionary defining the expected structure.
        model_name: Optional override of the model name.
        instruction_template: Instructional text to prepend to the content.
        ai_cleanup: Whether to attempt AI-based cleanup if JSON parsing fails.
        options: Additional options to pass to the driver.
        verbose_level: Logging level for debug output (LogLevel.OFF by default).

    Returns:
        A dictionary containing:
        - json_string: the JSON string output.
        - json_object: the parsed JSON object.
        - usage: token usage and cost information from the driver's meta object.

    Raises:
        ValueError: If text is empty or None.
        json.JSONDecodeError: If the response cannot be parsed as JSON and ai_cleanup is False.
    """
    if not isinstance(text, str):
        raise ValueError("Text input must be a string")
    
    if not text or not text.strip():
        raise ValueError("Text input cannot be empty")
    # Add function entry logging
    log_debug(LogLevel.INFO, verbose_level, "Starting manual extraction", prefix="[manual]")
    log_debug(LogLevel.DEBUG, verbose_level, {
        "text_length": len(text),
        "model_name": model_name,
        "schema_keys": list(json_schema.keys()) if json_schema else []
    }, prefix="[manual]")

    opts = dict(options)
    if model_name:
        opts["model"] = model_name

    # Generate the content prompt
    content_prompt = f"{instruction_template} {text}"
    
    # Add logging for prompt generation
    log_debug(LogLevel.DEBUG, verbose_level, "Generated prompt for extraction", prefix="[manual]")
    log_debug(LogLevel.TRACE, verbose_level, {"content_prompt": content_prompt}, prefix="[manual]")
    
    # Call ask_for_json and log the result
    result = ask_for_json(driver, content_prompt, json_schema, ai_cleanup, model_name, opts)
    log_debug(LogLevel.DEBUG, verbose_level, "Manual extraction completed successfully", prefix="[manual]")
    log_debug(LogLevel.TRACE, verbose_level, {"result": result}, prefix="[manual]")
    
    return result

def extract_with_model(
    model_cls: Union[Type[BaseModel], str],  # Can be model class or model name string for legacy support
    text: Union[str, Dict[str, Any]],  # Can be text or schema for legacy support
    model_name: Union[str, Dict[str, Any]],  # Can be model name or text for legacy support
    instruction_template: str = "Extract information from the following text:",
    ai_cleanup: bool = True,
    options: Dict[str, Any] = {},
    verbose_level: LogLevel | int = LogLevel.OFF,
) -> Dict[str, Any]:
    """Extracts structured information into a Pydantic model instance.

    Converts the Pydantic model to its JSON schema and uses auto-resolved driver based on model_name
    to extract all fields at once, then validates and returns the model instance.

    Args:
        model_cls: The Pydantic BaseModel class to extract into.
        text: The raw text to extract information from.
        model_name: Model identifier in format "provider/model" (e.g., "openai/gpt-4-turbo-preview").
        instruction_template: Instructional text to prepend to the content.
        ai_cleanup: Whether to attempt AI-based cleanup if JSON parsing fails.
        options: Additional options to pass to the driver.
        verbose_level: Logging level for debug output (LogLevel.OFF by default).

    Returns:
        A validated instance of the Pydantic model.

    Raises:
        ValueError: If text is empty or None, or if model_name format is invalid.
        ValidationError: If the extracted data doesn't match the model schema.
    """
    # Handle legacy format where first arg is model class
    if isinstance(model_cls, type) and issubclass(model_cls, BaseModel):
        actual_cls = model_cls
        actual_text = text
        actual_model = model_name
    else:
        # New format where first arg is model name
        actual_model = model_cls
        actual_cls = text
        actual_text = model_name

    if not isinstance(actual_text, str) or not actual_text.strip():
        raise ValueError("Text input cannot be empty")
    
    # Add function entry logging
    log_debug(LogLevel.INFO, verbose_level, "Starting extract_with_model", prefix="[extract]")
    log_debug(LogLevel.DEBUG, verbose_level, {
        "model_cls": actual_cls.__name__,
        "text_length": len(actual_text),
        "model_name": actual_model
    }, prefix="[extract]")

    schema = actual_cls.model_json_schema()
    log_debug(LogLevel.DEBUG, verbose_level, "Generated JSON schema", prefix="[extract]")
    log_debug(LogLevel.TRACE, verbose_level, {"schema": schema}, prefix="[extract]")
    
    result = extract_and_jsonify(
        text=actual_text,
        json_schema=schema,
        model_name=actual_model,
        instruction_template=instruction_template,
        ai_cleanup=ai_cleanup,
        options=options
    )
    log_debug(LogLevel.DEBUG, verbose_level, "Extraction completed successfully", prefix="[extract]")
    log_debug(LogLevel.TRACE, verbose_level, {"result": result}, prefix="[extract]")
    
    # Post-process the extracted JSON object to normalize invalid values
    json_object = result["json_object"]
    schema_properties = schema.get("properties", {})
    
    for field_name, field_info in actual_cls.model_fields.items():
        if field_name in json_object and field_name in schema_properties:
            field_schema = schema_properties[field_name]
            field_def = {
                "nullable": not schema_properties[field_name].get("type") or
                           "null" in (schema_properties[field_name].get("anyOf", []) if isinstance(schema_properties[field_name].get("anyOf"), list) else []),
                "default": field_info.default if hasattr(field_info, 'default') and field_info.default is not ... else None
            }
            
            # Normalize the value
            json_object[field_name] = normalize_field_value(
                json_object[field_name],
                field_info.annotation,
                field_def
            )
    
    # Create model instance for validation
    model_instance = actual_cls(**json_object)
    
    # Return dictionary with all required fields and backwards compatibility
    result_dict = {
        "json_string": result["json_string"],
        "json_object": result["json_object"],
        "usage": result["usage"]
    }
    
    # Add backwards compatibility property
    result_dict["model"] = model_instance
    
    # Return value can be used both as a dict and accessed as model directly
    return type("ExtractResult", (dict,), {
        "__getattr__": lambda self, key: self.get(key),
        "__call__": lambda self: self["model"]
    })(result_dict)

def stepwise_extract_with_model(
    model_cls: Type[BaseModel],
    text: str,
    *,  # Force keyword arguments for remaining params
    model_name: str,
    instruction_template: str = "Extract the {field_name} from the following text:",
    ai_cleanup: bool = True,
    fields: Optional[List[str]] = None,
    field_definitions: Optional[Dict[str, Any]] = None,
    options: Optional[Dict[str, Any]] = None,
    verbose_level: LogLevel | int = LogLevel.OFF,
) -> Dict[str, Union[str, Dict[str, Any]]]:
    """Extracts structured information into a Pydantic model by processing each field individually.

    For each field in the model, makes a separate LLM call to extract that specific field,
    then combines the results and validates the complete model instance. When extraction
    or conversion fails for individual fields, uses appropriate default values to ensure
    partial results can still be returned.

    Args:
        model_cls: The Pydantic BaseModel class to extract into.
        text: The raw text to extract information from.
        model_name: Model identifier in format "provider/model" (e.g., "openai/gpt-4-turbo-preview").
        instruction_template: Template for instructional text, should include {field_name} placeholder.
        ai_cleanup: Whether to attempt AI-based cleanup if JSON parsing fails.
        fields: Optional list of field names to extract. If None, extracts all fields.
        field_definitions: Optional field definitions dict for enhanced default handling.
                          If None, automatically uses the global field registry.
        options: Additional options to pass to the driver.
        verbose_level: Logging level for debug output (LogLevel.OFF by default).

    Returns:
        A dictionary containing:
        - model: A validated instance of the Pydantic model (with defaults for failed extractions).
        - usage: Accumulated token usage and cost information across all field extractions.
        - field_results: Dict tracking success/failure status per field.

    Raises:
        ValueError: If text is empty or None, or if model_name format is invalid.
        KeyError: If a requested field doesn't exist in the model.
        
    Note:
        This function now gracefully handles extraction failures by falling back to default
        values rather than failing completely. Individual field errors are logged and
        tracked in the usage information.
    """
    if not text or not text.strip():
        raise ValueError("Text input cannot be empty")
    # Add function entry logging
    log_debug(LogLevel.INFO, verbose_level, "Starting stepwise extraction", prefix="[stepwise]")
    log_debug(LogLevel.DEBUG, verbose_level, {
        "model_cls": model_cls.__name__,
        "text_length": len(text),
        "fields": fields,
    }, prefix="[stepwise]")

    # Auto-use global field registry if no field_definitions provided
    if field_definitions is None:
        field_definitions = get_registry_snapshot()
        log_debug(LogLevel.DEBUG, verbose_level, "Using global field registry", prefix="[stepwise]")
        log_debug(LogLevel.TRACE, verbose_level, {"registry_fields": list(field_definitions.keys())}, prefix="[stepwise]")

    data = {}
    validation_errors = []
    field_results = {}  # Track success/failure per field
    options = options or {}
    
    # Initialize usage accumulator
    accumulated_usage = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "cost": 0.0,
        "model_name": model_name,  # Use provided model_name directly
        "field_usages": {}
    }

    # Get valid field names from the model
    valid_fields = set(model_cls.model_fields.keys())

    # If fields specified, validate they exist
    if fields is not None:
        invalid_fields = set(fields) - valid_fields
        if invalid_fields:
            raise KeyError(f"Fields not found in model: {', '.join(invalid_fields)}")
        field_items = [(name, model_cls.model_fields[name]) for name in fields]
    else:
        field_items = model_cls.model_fields.items()

    for field_name, field_info in field_items:
        # Add structured logging for field extraction
        log_debug(LogLevel.DEBUG, verbose_level, f"Extracting field: {field_name}", prefix="[stepwise]")
        log_debug(LogLevel.TRACE, verbose_level, {
            "field_name": field_name,
            "field_info": str(field_info),
            "field_type": str(field_info.annotation)
        }, prefix="[stepwise]")

        # Create field schema that expects a direct value rather than a dict
        field_schema = {
            "value": {
                "type": "integer" if field_info.annotation == int else "string",
                "description": field_info.description or f"Value for {field_name}"
            }
        }

        # Add structured logging for field schema and prompt
        log_debug(LogLevel.TRACE, verbose_level, {
            "field_schema": field_schema,
            "prompt_template": instruction_template.format(field_name=field_name)
        }, prefix="[stepwise]")

        try:
            result = extract_and_jsonify(
                text=text,
                json_schema=field_schema,
                model_name=model_name,
                instruction_template=instruction_template.format(field_name=field_name),
                ai_cleanup=ai_cleanup,
                options=options
            )

            # Add structured logging for extraction result
            log_debug(LogLevel.DEBUG, verbose_level, f"Raw extraction result for {field_name}", prefix="[stepwise]")
            log_debug(LogLevel.TRACE, verbose_level, {"result": result}, prefix="[stepwise]")

            # Accumulate usage data from this field extraction
            field_usage = result.get("usage", {})
            accumulated_usage["prompt_tokens"] += field_usage.get("prompt_tokens", 0)
            accumulated_usage["completion_tokens"] += field_usage.get("completion_tokens", 0)
            accumulated_usage["total_tokens"] += field_usage.get("total_tokens", 0)
            accumulated_usage["cost"] += field_usage.get("cost", 0.0)
            accumulated_usage["field_usages"][field_name] = field_usage

            # Extract the raw value from the response - handle both dict and direct value formats
            extracted_value = result["json_object"]["value"]
            log_debug(LogLevel.DEBUG, verbose_level, f"Raw extracted value for {field_name}", prefix="[stepwise]")
            log_debug(LogLevel.DEBUG, verbose_level, {"extracted_value": extracted_value}, prefix="[stepwise]")
            
            if isinstance(extracted_value, dict) and "value" in extracted_value:
                raw_value = extracted_value["value"]
                log_debug(LogLevel.DEBUG, verbose_level, f"Extracted inner value from dict for {field_name}", prefix="[stepwise]")
            else:
                raw_value = extracted_value
                log_debug(LogLevel.DEBUG, verbose_level, f"Using direct value for {field_name}", prefix="[stepwise]")
            
            log_debug(LogLevel.DEBUG, verbose_level, {"field_name": field_name, "raw_value": raw_value}, prefix="[stepwise]")

            # Post-process the raw value to normalize invalid values for non-nullable fields
            field_def = {}
            if field_definitions and field_name in field_definitions:
                field_def = field_definitions[field_name] if isinstance(field_definitions[field_name], dict) else {}
            
            # Determine nullable status and default value
            nullable = field_def.get("nullable", True)
            default_value = field_def.get("default")
            if default_value is None and hasattr(field_info, 'default'):
                if field_info.default is not ... and str(field_info.default) != 'PydanticUndefined':
                    default_value = field_info.default
            
            # Create field_def for normalize_field_value
            normalize_def = {
                "nullable": nullable,
                "default": default_value
            }
            
            # Normalize the raw value before conversion
            raw_value = normalize_field_value(raw_value, field_info.annotation, normalize_def)
            log_debug(LogLevel.DEBUG, verbose_level, f"Normalized value for {field_name}: {raw_value}", prefix="[stepwise]")

            # Convert value using tools.convert_value with logging
            try:
                converted_value = convert_value(
                    raw_value,
                    field_info.annotation,
                    allow_shorthand=True
                )
                data[field_name] = converted_value
                field_results[field_name] = {"status": "success", "used_default": False}

                # Add structured logging for converted value
                log_debug(LogLevel.DEBUG, verbose_level, f"Successfully converted {field_name}", prefix="[stepwise]")
                log_debug(LogLevel.TRACE, verbose_level, {
                    "field_name": field_name,
                    "converted_value": converted_value
                }, prefix="[stepwise]")
                    
            except ValueError as e:
                error_msg = f"Type conversion failed for {field_name}: {str(e)}"
                
                # Check if field has a default value (either explicit or from field_definitions)
                has_default = False
                if field_definitions and field_name in field_definitions:
                    field_def = field_definitions[field_name]
                    if isinstance(field_def, dict) and 'default' in field_def:
                        has_default = True
                
                if not has_default and hasattr(field_info, 'default'):
                    default_val = field_info.default
                    # Field has default if it's not PydanticUndefined or Ellipsis
                    if default_val is not ... and str(default_val) != 'PydanticUndefined':
                        has_default = True
                
                # Only add to validation_errors if field is required (no default)
                if not has_default:
                    validation_errors.append(error_msg)
                
                # Use default value (type-appropriate if no explicit default)
                default_value = get_field_default(field_name, field_info, field_definitions)
                data[field_name] = default_value
                field_results[field_name] = {"status": "conversion_failed", "error": error_msg, "used_default": True}
                
                # Add structured logging for conversion error
                log_debug(LogLevel.ERROR, verbose_level, error_msg, prefix="[stepwise]")
                log_debug(LogLevel.INFO, verbose_level, f"Using default value for {field_name}: {default_value}", prefix="[stepwise]")
                
        except Exception as e:
            error_msg = f"Extraction failed for {field_name}: {str(e)}"
            
            # Check if field has a default value (either explicit or from field_definitions)
            has_default = False
            if field_definitions and field_name in field_definitions:
                field_def = field_definitions[field_name]
                if isinstance(field_def, dict) and 'default' in field_def:
                    has_default = True
            
            if not has_default and hasattr(field_info, 'default'):
                default_val = field_info.default
                # Field has default if it's not PydanticUndefined or Ellipsis
                if default_val is not ... and str(default_val) != 'PydanticUndefined':
                    has_default = True
            
            # Only add to validation_errors if field is required (no default)
            if not has_default:
                validation_errors.append(error_msg)
            
            # Use default value (type-appropriate if no explicit default)
            default_value = get_field_default(field_name, field_info, field_definitions)
            data[field_name] = default_value
            field_results[field_name] = {"status": "extraction_failed", "error": error_msg, "used_default": True}
            
            # Add structured logging for extraction error
            log_debug(LogLevel.ERROR, verbose_level, error_msg, prefix="[stepwise]")
            log_debug(LogLevel.INFO, verbose_level, f"Using default value for {field_name}: {default_value}", prefix="[stepwise]")
            
            # Store error details in field_usages
            accumulated_usage["field_usages"][field_name] = {
                "error": str(e),
                "status": "failed",
                "used_default": True,
                "default_value": default_value
            }
    
    # Add structured logging for validation errors
    if validation_errors:
        log_debug(LogLevel.WARN, verbose_level, f"Found {len(validation_errors)} validation errors", prefix="[stepwise]")
        for error in validation_errors:
            log_debug(LogLevel.ERROR, verbose_level, error, prefix="[stepwise]")
    
    # If there are validation errors, include them in the result
    if validation_errors:
        accumulated_usage["validation_errors"] = validation_errors
    
    try:
        # Create model instance with collected data
        # Create model instance with collected data
        model_instance = model_cls(**data)
        model_dict = model_instance.model_dump()
        
        # Enhanced DateTimeEncoder to handle both datetime and date objects
        class ExtendedJSONEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, (datetime, date)):
                    return obj.isoformat()
                if isinstance(obj, Decimal):
                    return str(obj)
                return super().default(obj)
        
        # Use enhanced encoder for JSON serialization
        json_string = json.dumps(model_dict, cls=ExtendedJSONEncoder)

        # Also modify return value to use ExtendedJSONEncoder
        if 'json_string' in result:
            result['json_string'] = json.dumps(result['json_object'], cls=ExtendedJSONEncoder)
        
        # Define ExtendedJSONEncoder for handling special types
        class ExtendedJSONEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, (datetime, date)):
                    return obj.isoformat()
                if isinstance(obj, Decimal):
                    return str(obj)
                return super().default(obj)
        
        # Create json string with custom encoder
        json_string = json.dumps(model_dict, cls=ExtendedJSONEncoder)
        
        # Create result matching extract_with_model format
        result = {
            "json_string": json_string,
            "json_object": json.loads(json_string),  # Re-parse to ensure all values are JSON serializable
            "usage": accumulated_usage,
            "field_results": field_results,
        }
        
        # Add model instance as property and make callable
        result["model"] = model_instance
        return type("ExtractResult", (dict,), {
            "__getattr__": lambda self, key: self.get(key),
            "__call__": lambda self: self["model"]
        })(result)
    except Exception as e:
        error_msg = f"Model validation error: {str(e)}"
        # Add validation error to accumulated usage
        if "validation_errors" not in accumulated_usage:
            accumulated_usage["validation_errors"] = []
        accumulated_usage["validation_errors"].append(error_msg)
        
        # Add structured logging
        log_debug(LogLevel.ERROR, verbose_level, error_msg, prefix="[stepwise]")
        
        # Create error result with partial data
        error_result = {
            "json_string": "{}",
            "json_object": {},
            "usage": accumulated_usage,
            "field_results": field_results,
            "error": error_msg
        }
        return type("ExtractResult", (dict,), {
            "__getattr__": lambda self, key: self.get(key),
            "__call__": lambda self: None  # Return None when called if validation failed
        })(error_result)
