"""Raw JSON wrapper for GraphQL resolvers to bypass serialization."""

import asyncio
from typing import Callable, Dict, Optional

from fraiseql.types.coercion import wrap_resolver_with_input_coercion


def create_raw_json_resolver(
    fn: Callable, field_name: str, arg_name_mapping: Optional[Dict[str, str]] = None
) -> Callable:
    """Create a raw JSON resolver that bypasses GraphQL serialization.

    This wrapper enables true JSON passthrough for production mode,
    where database JSON is directly returned to the client without
    Python object instantiation or GraphQL serialization.

    Args:
        fn: The original resolver function
        field_name: The GraphQL field name for response wrapping
        arg_name_mapping: Optional mapping from GraphQL args to Python params

    Returns:
        A wrapper resolver that handles raw JSON passthrough
    """
    # First wrap with input coercion
    coerced_fn = wrap_resolver_with_input_coercion(fn)

    if asyncio.iscoroutinefunction(coerced_fn):

        async def async_raw_json_resolver(root, info, **kwargs):
            # Debug logging to confirm raw JSON wrapper is being used
            import logging

            logger = logging.getLogger(__name__)
            logger.info(f"Raw JSON wrapper called for field: {field_name}")

            # Store GraphQL info and field name in context for repository
            if hasattr(info, "context"):
                info.context["graphql_info"] = info
                info.context["graphql_field_name"] = field_name

                # Also update the repository's context if it exists
                if "db" in info.context and hasattr(info.context["db"], "context"):
                    info.context["db"].context["graphql_info"] = info
                    info.context["db"].context["graphql_field_name"] = field_name

            # Map GraphQL argument names to Python parameter names
            if arg_name_mapping:
                mapped_kwargs = {}
                for gql_name, value in kwargs.items():
                    python_name = arg_name_mapping.get(gql_name, gql_name)
                    mapped_kwargs[python_name] = value
                kwargs = mapped_kwargs

            # Check if we should use passthrough BEFORE calling resolver
            context = getattr(info, "context", {})
            mode = context.get("mode")

            # Check configuration first, then other indicators
            # Only enable passthrough if explicitly configured or via query hints
            enable_passthrough = (
                context.get("json_passthrough", False)
                or context.get("execution_mode") == "passthrough"
                or (
                    mode in ("production", "staging")
                    and context.get("json_passthrough_in_production", False)
                )
            )

            # Set passthrough hint in context for the resolver to use
            if enable_passthrough and hasattr(info, "context"):
                info.context["_passthrough_field"] = field_name
                info.context["_passthrough_enabled"] = True

            # Call the coerced resolver
            result = await coerced_fn(root, info, **kwargs)

            # Re-check passthrough mode (already set above but double-check)
            enable_passthrough = context.get("_passthrough_enabled", enable_passthrough)

            # Debug logging
            logger.info(
                f"Raw JSON wrapper: mode={mode}, enable_passthrough={enable_passthrough}, "
                f"result_type={type(result).__name__}, result_is_dict={isinstance(result, dict)}"
            )
            if isinstance(result, dict):
                sample_keys = list(result.keys())[:5]  # Show first 5 keys
                logger.info(f"Dict keys sample: {sample_keys}")
            elif isinstance(result, list) and result:
                logger.info(
                    f"List result: length={len(result)}, first_item_type={type(result[0]).__name__}"
                )
                if isinstance(result[0], dict):
                    logger.info(f"First item keys: {list(result[0].keys())[:5]}")

            # Check if result is already a RawJSONResult (from raw JSON methods)
            from fraiseql.core.raw_json_executor import RawJSONResult

            if isinstance(result, RawJSONResult):
                logger.info("Returning RawJSONResult directly")
                return result

            # IMPORTANT: Do NOT convert dict/list results to RawJSONResult here!
            # RawJSONResult should only be used when the SQL query already returns
            # the properly structured JSON with field selection applied.
            #
            # If we convert here, it bypasses GraphQL's field resolution, which means:
            # - Nested objects/arrays aren't properly resolved
            # - Field selection from the query is ignored
            # - Custom resolvers don't run
            #
            # Instead, let GraphQL handle the result normally. The JSONPassthrough
            # wrapper (returned by the repository) already provides the performance
            # benefits without breaking field resolution.

            # Always return the result - let GraphQL handle field resolution
            return result

        return async_raw_json_resolver

    def sync_raw_json_resolver(root, info, **kwargs):
        # Store GraphQL info and field name in context for repository
        if hasattr(info, "context"):
            info.context["graphql_info"] = info
            info.context["graphql_field_name"] = field_name

            # Also update the repository's context if it exists
            if "db" in info.context and hasattr(info.context["db"], "context"):
                info.context["db"].context["graphql_info"] = info
                info.context["db"].context["graphql_field_name"] = field_name

        # Map GraphQL argument names to Python parameter names
        if arg_name_mapping:
            mapped_kwargs = {}
            for gql_name, value in kwargs.items():
                python_name = arg_name_mapping.get(gql_name, gql_name)
                mapped_kwargs[python_name] = value
            kwargs = mapped_kwargs

        # Call the coerced resolver
        result = coerced_fn(root, info, **kwargs)

        # Check if result is already a RawJSONResult (from raw JSON methods)
        from fraiseql.core.raw_json_executor import RawJSONResult

        if isinstance(result, RawJSONResult):
            # This is the key: RawJSONResult should bypass GraphQL entirely
            # and be returned directly as HTTP JSON response
            return result

        # IMPORTANT: Do NOT convert dict/list results to RawJSONResult here!
        # See explanation in async version above. The same principle applies
        # to synchronous resolvers - let GraphQL handle field resolution.

        # Always return the result - let GraphQL handle field resolution
        return result

    return sync_raw_json_resolver
