# SPDX-FileCopyrightText: 2025-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import inspect
from typing import Any

import pytest

from deepset_mcp.tokonomics import InMemoryBackend, ObjectStore, RichExplorer
from deepset_mcp.tokonomics.decorators import (
    _add_str_to_type,
    _enhance_docstring_for_explorable,
    _enhance_docstring_for_references,
    _is_reference,
    _type_allows_str,
    explorable,
    explorable_and_referenceable,
    referenceable,
)


class TestHelperFunctions:
    """Test helper functions used by decorators."""

    def test_is_reference_valid(self) -> None:
        """Test _is_reference with valid references."""
        valid_refs = [
            "@obj_001",
            "@obj_123.path",
            "@test_obj",
            "@a",
        ]

        for ref in valid_refs:
            assert _is_reference(ref) is True

    def test_is_reference_invalid(self) -> None:
        """Test _is_reference with invalid references."""
        invalid_refs = [
            "obj_001",  # No @
            "@",  # Just @
            "",  # Empty string
            123,  # Not string
            None,  # None
        ]

        for ref in invalid_refs:
            assert _is_reference(ref) is False

    def test_type_allows_str_primitive(self) -> None:
        """Test _type_allows_str with primitive str type."""
        assert _type_allows_str(str) is True

    def test_type_allows_str_pipe_union(self) -> None:
        """Test _type_allows_str with | union syntax."""
        assert _type_allows_str(str | int) is True
        assert _type_allows_str(int | str) is True
        assert _type_allows_str(int | float) is False

    def test_type_allows_str_other_types(self) -> None:
        """Test _type_allows_str with other types."""
        assert _type_allows_str(int) is False
        assert _type_allows_str(list) is False
        assert _type_allows_str(dict) is False

    def test_add_str_to_type_empty(self) -> None:
        """Test _add_str_to_type with empty annotation."""
        result = _add_str_to_type(inspect.Parameter.empty)
        assert result is str

    def test_add_str_to_type_already_str(self) -> None:
        """Test _add_str_to_type with str type."""
        result = _add_str_to_type(str)
        assert result is str

    def test_add_str_to_type_union_with_str(self) -> None:
        """Test _add_str_to_type with Union already containing str."""
        original = str | int
        result = _add_str_to_type(original)
        assert result == original

    def test_add_str_to_type_other_type(self) -> None:
        """Test _add_str_to_type with other types."""
        result = _add_str_to_type(int)
        assert result == (int | str)

    def test_enhance_docstring_for_references(self) -> None:
        """Test docstring enhancement for referenceable functions."""
        original = "Original docstring."

        result = _enhance_docstring_for_references(original, "test_func")

        assert "Original docstring." in result
        assert "All parameters accept object references" in result
        assert "test_func(data='@obj_123'" in result
        # Should not contain the old reference support formatting
        assert "**Reference Support**" not in result
        assert "dict → dict | str" not in result

    def test_enhance_docstring_for_references_empty_original(self) -> None:
        """Test docstring enhancement with empty original docstring."""
        result = _enhance_docstring_for_references("", "test_func")

        assert "test_func function." in result
        assert "All parameters accept object references" in result
        # Should not contain the old reference support formatting
        assert "**Reference Support**" not in result

    def test_enhance_docstring_for_explorable(self) -> None:
        """Test docstring enhancement for explorable functions."""
        original = "Original docstring."

        result = _enhance_docstring_for_explorable(original, "test_func")

        assert "Original docstring." in result
        assert "automatically stored and can be referenced" in result
        assert "object ID (e.g., ``@obj_123``)" in result
        # Should not contain the old output storage formatting
        assert "**Output Storage**" not in result

    def test_enhance_docstring_for_explorable_empty_original(self) -> None:
        """Test docstring enhancement with empty original docstring."""
        result = _enhance_docstring_for_explorable("", "test_func")

        assert "test_func function." in result
        assert "automatically stored and can be referenced" in result
        # Should not contain the old output storage formatting
        assert "**Output Storage**" not in result

    def test_enhance_docstring_for_references_preserves_original(self) -> None:
        """Test that _enhance_docstring_for_references preserves all original content."""
        original = """Process data and return results.

        This function processes the input data and returns processed results.
        It may raise exceptions if the data is invalid.

        :param data: Input data to process
        :param options: Processing options
        :return: Processed results
        :raises ValueError: If data is invalid
        :raises RuntimeError: If processing fails
        """

        result = _enhance_docstring_for_references(original, "test_func")

        # Check that all original content is preserved exactly
        assert "Process data and return results." in result
        assert "This function processes the input data" in result
        assert ":param data: Input data to process" in result
        assert ":param options: Processing options" in result
        assert ":return: Processed results" in result
        assert ":raises ValueError: If data is invalid" in result
        assert ":raises RuntimeError: If processing fails" in result

        # Check that enhancement is added
        assert "All parameters accept object references" in result
        assert "test_func(data='@obj_123'" in result

    def test_enhance_docstring_for_explorable_preserves_original(self) -> None:
        """Test that _enhance_docstring_for_explorable preserves all original content."""
        original = """Calculate statistics from data.

        :param values: List of numbers
        :return: Statistical summary dict
        :raises ValueError: If values is empty
        """

        result = _enhance_docstring_for_explorable(original, "calc_stats")

        # Check that all original content is preserved exactly
        assert "Calculate statistics from data." in result
        assert ":param values: List of numbers" in result
        assert ":return: Statistical summary dict" in result
        assert ":raises ValueError: If values is empty" in result

        # Check that enhancement is added
        assert "automatically stored and can be referenced" in result
        assert "object ID (e.g., ``@obj_123``)" in result


class TestExplorableDecorator:
    """Test @explorable decorator."""

    @pytest.fixture
    def store(self) -> ObjectStore:
        """Create an ObjectStore for testing."""
        return ObjectStore(backend=InMemoryBackend(), ttl=0)

    @pytest.fixture
    def explorer(self, store: ObjectStore) -> RichExplorer:
        """Create a RichExplorer for testing."""
        return RichExplorer(store)

    def test_explorable_sync_function(self, store: ObjectStore, explorer: RichExplorer) -> None:
        """Test @explorable decorator on sync function."""

        @explorable(object_store=store, explorer=explorer)
        def test_func() -> dict:
            return {"result": "success"}

        result = test_func()

        assert isinstance(result, str)
        assert "@obj_001" in result
        assert "success" in result

        # Check that object is stored
        stored_obj = store.get("obj_001")
        assert stored_obj == {"result": "success"}

    def test_explorable_async_function(self, store: ObjectStore, explorer: RichExplorer) -> None:
        """Test @explorable decorator on async function."""

        @explorable(object_store=store, explorer=explorer)
        async def test_func() -> dict:
            return {"result": "success"}

        async def run_test() -> None:
            result = await test_func()

            assert isinstance(result, str)
            assert "@obj_001" in result
            assert "success" in result

            # Check that object is stored
            stored_obj = store.get("obj_001")
            assert stored_obj == {"result": "success"}

        asyncio.run(run_test())

    def test_explorable_preserves_signature(self, store: ObjectStore, explorer: RichExplorer) -> None:
        """Test that @explorable preserves function signature."""

        @explorable(object_store=store, explorer=explorer)
        def test_func(param1: str, param2: int = 42) -> dict:
            """Original docstring."""
            return {"param1": param1, "param2": param2}

        sig = inspect.signature(test_func)
        params = list(sig.parameters.keys())

        assert params == ["param1", "param2"]
        assert sig.parameters["param1"].annotation is str
        assert sig.parameters["param2"].annotation is int
        assert sig.parameters["param2"].default == 42

    def test_explorable_enhances_docstring(self, store: ObjectStore, explorer: RichExplorer) -> None:
        """Test that @explorable enhances docstring."""

        @explorable(object_store=store, explorer=explorer)
        def test_func() -> dict:
            """Original docstring."""
            return {}

        assert "Original docstring." in test_func.__doc__
        assert "automatically stored" in test_func.__doc__
        # Should not contain the old output storage formatting
        assert "**Output Storage**" not in test_func.__doc__

    def test_explorable_with_args(self, store: ObjectStore, explorer: RichExplorer) -> None:
        """Test @explorable decorated function with arguments."""

        @explorable(object_store=store, explorer=explorer)
        def test_func(data: dict, multiplier: int = 2) -> dict:
            return {key: value * multiplier for key, value in data.items()}

        result = test_func({"a": 1, "b": 2}, multiplier=3)

        assert isinstance(result, str)
        assert "a" in result

    def test_explorable_sync_return_type_annotation_changed_to_str(
        self, store: ObjectStore, explorer: RichExplorer
    ) -> None:
        """Test that @explorable decorator changes sync function return type annotation to str."""

        @explorable(object_store=store, explorer=explorer)
        def sync_test_func() -> dict:
            return {"test": "data"}

        # Verify the return type annotation was changed to str
        assert sync_test_func.__annotations__["return"] is str

    def test_explorable_async_return_type_annotation_changed_to_str(
        self, store: ObjectStore, explorer: RichExplorer
    ) -> None:
        """Test that @explorable decorator changes async function return type annotation to str."""

        @explorable(object_store=store, explorer=explorer)
        async def async_test_func() -> list:
            return [1, 2, 3]

        # Verify the return type annotation was changed to str
        assert async_test_func.__annotations__["return"] is str


class TestReferenceableDecorator:
    """Test @referenceable decorator."""

    @pytest.fixture
    def store(self) -> ObjectStore:
        """Create an ObjectStore for testing."""
        return ObjectStore(backend=InMemoryBackend(), ttl=0)

    @pytest.fixture
    def explorer(self, store: ObjectStore) -> RichExplorer:
        """Create a RichExplorer for testing."""
        return RichExplorer(store)

    def test_referenceable_direct_values(self, store: ObjectStore, explorer: RichExplorer) -> None:
        """Test @referenceable decorator with direct values."""

        @referenceable(object_store=store, explorer=explorer)
        def test_func(data: dict, threshold: int) -> str:
            return f"Processed {len(data)} items with threshold {threshold}"

        result = test_func({"a": 1, "b": 2}, 10)

        assert result == "Processed 2 items with threshold 10"

    def test_referenceable_with_references(self, store: ObjectStore, explorer: RichExplorer) -> None:
        """Test @referenceable decorator with object references."""
        # Store test objects
        data_obj = {"key1": "value1", "key2": "value2"}
        config_obj = {"threshold": 15, "mode": "test"}

        data_id = store.put(data_obj)
        config_id = store.put(config_obj)

        @referenceable(object_store=store, explorer=explorer)
        def test_func(data: dict, threshold: int) -> str:
            return f"Processed {len(data)} items with threshold {threshold}"

        # Use references
        result = test_func(f"@{data_id}", f"@{config_id}.threshold")

        assert result == "Processed 2 items with threshold 15"

    def test_referenceable_mixed_args(self, store: ObjectStore, explorer: RichExplorer) -> None:
        """Test @referenceable decorator with mixed direct values and references."""
        data_obj = {"items": [1, 2, 3, 4, 5]}
        data_id = store.put(data_obj)

        @referenceable(object_store=store, explorer=explorer)
        def test_func(data: dict, multiplier: int) -> int:
            return len(data["items"]) * multiplier

        result = test_func(f"@{data_id}", 3)

        assert result == 15

    def test_referenceable_async_function(self, store: ObjectStore, explorer: RichExplorer) -> None:
        """Test @referenceable decorator on async function."""
        data_obj = {"count": 42}
        data_id = store.put(data_obj)

        @referenceable(object_store=store, explorer=explorer)
        async def test_func(data: dict) -> int:
            return data["count"]

        async def run_test() -> None:
            result = await test_func(f"@{data_id}")
            assert result == 42

        asyncio.run(run_test())

    def test_referenceable_invalid_reference(self, store: ObjectStore, explorer: RichExplorer) -> None:
        """Test @referenceable decorator with invalid reference."""

        @referenceable(object_store=store, explorer=explorer)
        def test_func(data: dict) -> str:
            return "success"

        with pytest.raises(TypeError, match="Parameter 'data' expects"):
            test_func("invalid_reference")

    def test_referenceable_nonexistent_object(self, store: ObjectStore, explorer: RichExplorer) -> None:
        """Test @referenceable decorator with non-existent object reference."""

        @referenceable(object_store=store, explorer=explorer)
        def test_func(data: dict) -> str:
            return "success"

        with pytest.raises(ValueError, match="Object @obj_999 not found or expired"):
            test_func("@obj_999")

    def test_referenceable_invalid_path(self, store: ObjectStore, explorer: RichExplorer) -> None:
        """Test @referenceable decorator with invalid path in reference."""
        data_obj = {"key": "value"}
        data_id = store.put(data_obj)

        @referenceable(object_store=store, explorer=explorer)
        def test_func(data: Any) -> str:
            return str(data)

        with pytest.raises(ValueError, match="Navigation error"):
            test_func(f"@{data_id}.nonexistent.path")

    def test_referenceable_type_checking(self, store: ObjectStore, explorer: RichExplorer) -> None:
        """Test @referenceable decorator type checking for non-string parameters."""

        @referenceable(object_store=store, explorer=explorer)
        def test_func(number: int) -> int:
            return number * 2

        # Should work with valid reference
        num_obj = 42
        num_id = store.put(num_obj)
        result = test_func(f"@{num_id}")
        assert result == 84

        # Should fail with invalid string (not a reference)
        with pytest.raises(TypeError, match="Parameter 'number' expects"):
            test_func("not_a_reference")

    def test_referenceable_preserves_signature(self, store: ObjectStore, explorer: RichExplorer) -> None:
        """Test that @referenceable preserves and modifies function signature."""

        @referenceable(object_store=store, explorer=explorer)
        def test_func(data: dict, threshold: int, text: str = "default") -> str:
            """Original docstring."""
            return f"{len(data)} items"

        sig = inspect.signature(test_func)
        params = list(sig.parameters.keys())

        assert params == ["data", "threshold", "text"]
        # Types should be modified to include str
        assert sig.parameters["data"].annotation == (dict | str)
        assert sig.parameters["threshold"].annotation == (int | str)
        assert sig.parameters["text"].annotation is str  # Already allows str

    def test_referenceable_enhances_docstring(self, store: ObjectStore, explorer: RichExplorer) -> None:
        """Test that @referenceable enhances docstring."""

        @referenceable(object_store=store, explorer=explorer)
        def test_func(data: dict) -> str:
            """Original docstring."""
            return "result"

        assert "Original docstring." in test_func.__doc__
        assert "All parameters accept object references" in test_func.__doc__
        # Should not contain the old reference support formatting
        assert "**Reference Support**" not in test_func.__doc__


class TestExplorableAndReferenceableDecorator:
    """Test @explorable_and_referenceable decorator."""

    @pytest.fixture
    def store(self) -> ObjectStore:
        """Create an ObjectStore for testing."""
        return ObjectStore(backend=InMemoryBackend(), ttl=0)

    @pytest.fixture
    def explorer(self, store: ObjectStore) -> RichExplorer:
        """Create a RichExplorer for testing."""
        return RichExplorer(store)

    def test_combined_decorator_functionality(self, store: ObjectStore, explorer: RichExplorer) -> None:
        """Test combined @explorable_and_referenceable decorator."""
        # First, create some data to reference
        input_data = {"values": [1, 2, 3, 4, 5]}
        input_id = store.put(input_data)

        @explorable_and_referenceable(object_store=store, explorer=explorer)
        def process_data(data: dict, multiplier: int) -> dict:
            """Process data by multiplying values."""
            return {"processed": [x * multiplier for x in data["values"]]}

        # Call with reference and direct value
        result = process_data(f"@{input_id}", 2)

        # Should return string (from @explorable)
        assert isinstance(result, str)

        # Should store the result (from @explorable)
        # We need to get the latest stored object to verify it was stored
        stored_result = store.get("obj_002")
        assert stored_result == {"processed": [2, 4, 6, 8, 10]}

    def test_combined_decorator_chaining(self, store: ObjectStore, explorer: RichExplorer) -> None:
        """Test chaining functions with combined decorator."""

        @explorable_and_referenceable(object_store=store, explorer=explorer)
        def step1(data: list) -> dict:
            return {"sum": sum(data), "count": len(data)}

        @explorable_and_referenceable(object_store=store, explorer=explorer)
        def step2(stats: dict) -> dict:
            return {"average": stats["sum"] / stats["count"]}

        # Step 1: Process initial data
        initial_data = [10, 20, 30, 40, 50]
        _ = step1(initial_data)

        # Step 2: Use result from step 1 by reference (obj_001)
        result2 = step2("@obj_001")

        assert isinstance(result2, str)

        processed = store.get("obj_002")

        assert processed == {"average": 30.0}

    def test_combined_decorator_docstring(self, store: ObjectStore, explorer: RichExplorer) -> None:
        """Test that combined decorator enhances docstring properly."""

        @explorable_and_referenceable(object_store=store, explorer=explorer)
        def test_func(data: dict) -> dict:
            """Original docstring."""
            return data

        docstring = test_func.__doc__

        # Should contain both reference and explorable documentation
        assert "Original docstring." in docstring
        assert "All parameters accept object references" in docstring
        assert "automatically stored" in docstring
        # Should not contain the old section formatting
        assert "**Reference Support**" not in docstring
        assert "**Output Storage**" not in docstring

    def test_combined_decorator_signature(self, store: ObjectStore, explorer: RichExplorer) -> None:
        """Test that combined decorator modifies signature correctly."""

        @explorable_and_referenceable(object_store=store, explorer=explorer)
        def test_func(data: dict, threshold: int) -> dict:
            return {"data": data, "threshold": threshold}

        sig = inspect.signature(test_func)

        # Should have modified parameter types (from @referenceable)
        assert sig.parameters["data"].annotation == (dict | str)
        assert sig.parameters["threshold"].annotation == (int | str)
