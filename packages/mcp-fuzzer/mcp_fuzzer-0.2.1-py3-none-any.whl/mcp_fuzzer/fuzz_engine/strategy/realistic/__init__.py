"""
Realistic Strategy Module

This module contains strategies for generating realistic, valid data for fuzzing.
The realistic phase tests server behavior with expected, well-formed inputs.
"""

from .tool_strategy import (
    base64_strings,
    uuid_strings,
    timestamp_strings,
    generate_realistic_text,
    fuzz_tool_arguments_realistic,
)

from .protocol_type_strategy import (
    json_rpc_id_values,
    method_names,
    protocol_version_strings,
    fuzz_initialize_request_realistic,
    fuzz_list_resources_request_realistic,
    fuzz_read_resource_request_realistic,
    fuzz_subscribe_request_realistic,
    fuzz_unsubscribe_request_realistic,
    fuzz_list_prompts_request_realistic,
    fuzz_get_prompt_request_realistic,
    fuzz_list_roots_request_realistic,
    fuzz_set_level_request_realistic,
    fuzz_complete_request_realistic,
)

__all__ = [
    # Tool strategies
    "base64_strings",
    "uuid_strings",
    "timestamp_strings",
    "generate_realistic_text",
    "fuzz_tool_arguments_realistic",
    # Protocol strategies
    "json_rpc_id_values",
    "method_names",
    "protocol_version_strings",
    "fuzz_initialize_request_realistic",
    "fuzz_list_resources_request_realistic",
    "fuzz_read_resource_request_realistic",
    "fuzz_subscribe_request_realistic",
    "fuzz_unsubscribe_request_realistic",
    "fuzz_list_prompts_request_realistic",
    "fuzz_get_prompt_request_realistic",
    "fuzz_list_roots_request_realistic",
    "fuzz_set_level_request_realistic",
    "fuzz_complete_request_realistic",
]
