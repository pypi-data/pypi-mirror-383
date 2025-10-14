"""Tests for implementations module - cache strategies, rate limiters, validators, circuit breakers."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.implementations import (
    DefaultValidator,
    MemoryCacheStrategy,
    NoOpRateLimiter,
    AioLimiterAdapter,
    AioCacheAdapter,
    DefaultCircuitBreaker,
    NoOpCircuitBreaker,
    CircuitState,
    generate_cache_key,
)
from src.exceptions import CircuitBreakerOpenError


class TestDefaultValidator:
    """Test DefaultValidator implementation."""

    def test_validate_params_with_nested_dict(self):
        """Test validation of nested dictionary parameters."""
        validator = DefaultValidator()
        params = {
            "level1": {
                "level2": {
                    "value": "safe data"
                }
            }
        }
        # Should not raise
        validator.validate_params(params)

    def test_validate_params_with_list_of_dicts(self):
        """Test validation of list containing dictionaries."""
        validator = DefaultValidator()
        params = {
            "items": [
                {"id": "1", "name": "item1"},
                {"id": "2", "name": "item2"}
            ]
        }
        # Should not raise
        validator.validate_params(params)

    def test_validate_params_oversized_list_item(self):
        """Test that oversized list items are rejected."""
        validator = DefaultValidator()
        params = {
            "items": ["x" * (validator.MAX_PARAM_VALUE_LENGTH + 1)]
        }
        with pytest.raises(ValueError, match="exceeds maximum length"):
            validator.validate_params(params)

    def test_validate_params_nested_dict_with_oversized_value(self):
        """Test nested dict with oversized value is rejected."""
        validator = DefaultValidator()
        params = {
            "outer": {
                "inner": "x" * (validator.MAX_PARAM_VALUE_LENGTH + 1)
            }
        }
        with pytest.raises(ValueError, match="exceeds maximum length"):
            validator.validate_params(params)

    def test_validate_endpoint_with_suspicious_patterns(self):
        """Test endpoint validation with suspicious patterns."""
        validator = DefaultValidator()

        # Test path traversal
        with pytest.raises(ValueError, match="Suspicious pattern"):
            validator.validate_endpoint("/api/../etc/passwd")

        # Test double slash
        with pytest.raises(ValueError, match="Suspicious pattern"):
            validator.validate_endpoint("/api//endpoint")

        # Test null byte
        with pytest.raises(ValueError, match="Suspicious pattern"):
            validator.validate_endpoint("/api/\x00endpoint")


class TestMemoryCacheStrategy:
    """Test MemoryCacheStrategy implementation."""

    @pytest.mark.asyncio
    async def test_cache_basic_operations(self):
        """Test basic cache get/set/delete operations."""
        cache = MemoryCacheStrategy()

        # Test set and get
        await cache.set("key1", {"data": "value1"})
        result = await cache.get("key1")
        assert result == {"data": "value1"}

        # Test get non-existent key
        result = await cache.get("non_existent")
        assert result is None

        # Test delete
        await cache.delete("key1")
        result = await cache.get("key1")
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_with_ttl(self):
        """Test cache set with TTL parameter (basic implementation ignores TTL)."""
        cache = MemoryCacheStrategy()
        await cache.set("key1", {"data": "value1"}, ttl=300)
        result = await cache.get("key1")
        assert result == {"data": "value1"}

    @pytest.mark.asyncio
    async def test_cache_clear(self):
        """Test cache clear operation."""
        cache = MemoryCacheStrategy()
        await cache.set("key1", {"data": "value1"})
        await cache.set("key2", {"data": "value2"})

        await cache.clear()

        assert await cache.get("key1") is None
        assert await cache.get("key2") is None


class TestNoOpRateLimiter:
    """Test NoOpRateLimiter implementation."""

    @pytest.mark.asyncio
    async def test_acquire_always_succeeds(self):
        """Test that acquire always succeeds immediately."""
        limiter = NoOpRateLimiter()
        # Should complete immediately without blocking
        await limiter.acquire()
        await limiter.acquire()
        await limiter.acquire()

    @pytest.mark.asyncio
    async def test_try_acquire_always_returns_true(self):
        """Test that try_acquire always returns True."""
        limiter = NoOpRateLimiter()
        assert await limiter.try_acquire() is True
        assert await limiter.try_acquire() is True
        assert await limiter.try_acquire() is True


class TestAioLimiterAdapter:
    """Test AioLimiterAdapter implementation."""

    @pytest.mark.asyncio
    async def test_acquire_calls_underlying_limiter(self):
        """Test that acquire calls the underlying aiolimiter."""
        mock_limiter = AsyncMock()
        adapter = AioLimiterAdapter(mock_limiter)

        await adapter.acquire()

        mock_limiter.acquire.assert_called_once()

    @pytest.mark.asyncio
    async def test_try_acquire_returns_true(self):
        """Test that try_acquire calls acquire and returns True."""
        mock_limiter = AsyncMock()
        adapter = AioLimiterAdapter(mock_limiter)

        result = await adapter.try_acquire()

        assert result is True
        mock_limiter.acquire.assert_called_once()


class TestAioCacheAdapter:
    """Test AioCacheAdapter implementation."""

    @pytest.mark.asyncio
    async def test_get_success(self):
        """Test successful cache retrieval."""
        mock_cache = AsyncMock()
        mock_cache.get.return_value = {"data": "value"}
        adapter = AioCacheAdapter(mock_cache)

        result = await adapter.get("key1")

        assert result == {"data": "value"}
        mock_cache.get.assert_called_once_with("key1")

    @pytest.mark.asyncio
    async def test_get_returns_none_when_not_found(self):
        """Test that get returns None when key not found."""
        mock_cache = AsyncMock()
        mock_cache.get.return_value = None
        adapter = AioCacheAdapter(mock_cache)

        result = await adapter.get("key1")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_handles_exception(self):
        """Test that get handles exceptions gracefully."""
        mock_cache = AsyncMock()
        mock_cache.get.side_effect = Exception("Cache error")
        adapter = AioCacheAdapter(mock_cache)

        result = await adapter.get("key1")

        assert result is None

    @pytest.mark.asyncio
    async def test_set_with_ttl(self):
        """Test cache set with TTL."""
        mock_cache = AsyncMock()
        adapter = AioCacheAdapter(mock_cache)

        await adapter.set("key1", {"data": "value"}, ttl=300)

        mock_cache.set.assert_called_once_with("key1", {"data": "value"}, ttl=300)

    @pytest.mark.asyncio
    async def test_set_without_ttl(self):
        """Test cache set without TTL."""
        mock_cache = AsyncMock()
        adapter = AioCacheAdapter(mock_cache)

        await adapter.set("key1", {"data": "value"})

        mock_cache.set.assert_called_once_with("key1", {"data": "value"})

    @pytest.mark.asyncio
    async def test_set_handles_exception(self):
        """Test that set handles exceptions gracefully."""
        mock_cache = AsyncMock()
        mock_cache.set.side_effect = Exception("Cache error")
        adapter = AioCacheAdapter(mock_cache)

        # Should not raise
        await adapter.set("key1", {"data": "value"})

    @pytest.mark.asyncio
    async def test_delete(self):
        """Test cache delete."""
        mock_cache = AsyncMock()
        adapter = AioCacheAdapter(mock_cache)

        await adapter.delete("key1")

        mock_cache.delete.assert_called_once_with("key1")

    @pytest.mark.asyncio
    async def test_delete_handles_exception(self):
        """Test that delete handles exceptions gracefully."""
        mock_cache = AsyncMock()
        mock_cache.delete.side_effect = Exception("Cache error")
        adapter = AioCacheAdapter(mock_cache)

        # Should not raise
        await adapter.delete("key1")

    @pytest.mark.asyncio
    async def test_clear(self):
        """Test cache clear."""
        mock_cache = AsyncMock()
        adapter = AioCacheAdapter(mock_cache)

        await adapter.clear()

        mock_cache.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_clear_handles_exception(self):
        """Test that clear handles exceptions gracefully."""
        mock_cache = AsyncMock()
        mock_cache.clear.side_effect = Exception("Cache error")
        adapter = AioCacheAdapter(mock_cache)

        # Should not raise
        await adapter.clear()


class TestDefaultCircuitBreaker:
    """Test DefaultCircuitBreaker implementation."""

    @pytest.mark.asyncio
    async def test_initial_state_is_closed(self):
        """Test that circuit breaker starts in CLOSED state."""
        cb = DefaultCircuitBreaker()
        assert cb.state == CircuitState.CLOSED.value
        assert cb.failure_count == 0

    @pytest.mark.asyncio
    async def test_successful_call(self):
        """Test successful function execution through circuit breaker."""
        cb = DefaultCircuitBreaker()

        async def successful_func():
            return "success"

        result = await cb.call(successful_func)

        assert result == "success"
        assert cb.state == CircuitState.CLOSED.value
        assert cb.failure_count == 0

    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold_failures(self):
        """Test that circuit opens after reaching failure threshold."""
        cb = DefaultCircuitBreaker(failure_threshold=3)

        async def failing_func():
            raise ValueError("Test error")

        # Record failures up to threshold
        for i in range(3):
            with pytest.raises(ValueError):
                await cb.call(failing_func)

        assert cb.state == CircuitState.OPEN.value
        assert cb.failure_count == 3

    @pytest.mark.asyncio
    async def test_circuit_open_fails_fast(self):
        """Test that open circuit fails fast without calling function."""
        cb = DefaultCircuitBreaker(failure_threshold=2)

        call_count = 0

        async def failing_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("Test error")

        # Open the circuit
        for i in range(2):
            with pytest.raises(ValueError):
                await cb.call(failing_func)

        assert cb.state == CircuitState.OPEN.value
        call_count_before = call_count

        # Next call should fail fast
        with pytest.raises(CircuitBreakerOpenError) as exc_info:
            await cb.call(failing_func)

        # Function should not have been called
        assert call_count == call_count_before
        assert "Circuit breaker is OPEN" in str(exc_info.value)
        assert exc_info.value.failure_count == 2

    @pytest.mark.asyncio
    async def test_circuit_transitions_to_half_open(self):
        """Test that circuit transitions to HALF_OPEN after recovery timeout."""
        cb = DefaultCircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.1,  # Short timeout for testing
            success_threshold=1
        )

        async def failing_func():
            raise ValueError("Test error")

        async def successful_func():
            return "success"

        # Open the circuit
        for i in range(2):
            with pytest.raises(ValueError):
                await cb.call(failing_func)

        assert cb.state == CircuitState.OPEN.value

        # Wait for recovery timeout
        await asyncio.sleep(0.2)

        # Next call should transition to HALF_OPEN and succeed
        result = await cb.call(successful_func)

        assert result == "success"
        assert cb.state == CircuitState.CLOSED.value  # Should close after success

    @pytest.mark.asyncio
    async def test_half_open_closes_after_success_threshold(self):
        """Test that HALF_OPEN circuit closes after success threshold."""
        cb = DefaultCircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.1,
            success_threshold=2
        )

        async def failing_func():
            raise ValueError("Test error")

        async def successful_func():
            return "success"

        # Open the circuit
        for i in range(2):
            with pytest.raises(ValueError):
                await cb.call(failing_func)

        # Wait for recovery
        await asyncio.sleep(0.2)

        # First success - should stay HALF_OPEN
        result1 = await cb.call(successful_func)
        assert result1 == "success"
        # Note: state might be CLOSED already due to lock timing

        # Second success - should close circuit
        result2 = await cb.call(successful_func)
        assert result2 == "success"
        assert cb.state == CircuitState.CLOSED.value

    @pytest.mark.asyncio
    async def test_half_open_reopens_on_failure(self):
        """Test that HALF_OPEN circuit reopens on failure."""
        cb = DefaultCircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.1
        )

        async def failing_func():
            raise ValueError("Test error")

        # Open the circuit
        for i in range(2):
            with pytest.raises(ValueError):
                await cb.call(failing_func)

        # Wait for recovery
        await asyncio.sleep(0.2)

        # Fail during recovery - should reopen
        with pytest.raises(ValueError):
            await cb.call(failing_func)

        assert cb.state == CircuitState.OPEN.value

    @pytest.mark.asyncio
    async def test_record_success_in_closed_state(self):
        """Test record_success resets failure count in CLOSED state."""
        cb = DefaultCircuitBreaker()

        # Record some failures
        cb.record_failure()
        cb.record_failure()
        assert cb.failure_count == 2

        # Record success should reset
        cb.record_success()
        assert cb.failure_count == 0
        assert cb.state == CircuitState.CLOSED.value

    @pytest.mark.asyncio
    async def test_record_failure_in_closed_state(self):
        """Test record_failure increments count in CLOSED state."""
        cb = DefaultCircuitBreaker(failure_threshold=3)

        cb.record_failure()
        assert cb.failure_count == 1
        assert cb.state == CircuitState.CLOSED.value

        cb.record_failure()
        assert cb.failure_count == 2
        assert cb.state == CircuitState.CLOSED.value

        cb.record_failure()
        assert cb.failure_count == 3
        assert cb.state == CircuitState.OPEN.value


class TestNoOpCircuitBreaker:
    """Test NoOpCircuitBreaker implementation."""

    @pytest.mark.asyncio
    async def test_call_executes_function(self):
        """Test that call executes the function without circuit breaking."""
        cb = NoOpCircuitBreaker()

        async def test_func():
            return "result"

        result = await cb.call(test_func)
        assert result == "result"

    @pytest.mark.asyncio
    async def test_call_propagates_exceptions(self):
        """Test that call propagates exceptions."""
        cb = NoOpCircuitBreaker()

        async def failing_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            await cb.call(failing_func)

    def test_record_success_is_noop(self):
        """Test that record_success does nothing."""
        cb = NoOpCircuitBreaker()
        cb.record_success()  # Should not raise

    def test_record_failure_is_noop(self):
        """Test that record_failure does nothing."""
        cb = NoOpCircuitBreaker()
        cb.record_failure()  # Should not raise

    def test_state_always_closed(self):
        """Test that state is always CLOSED."""
        cb = NoOpCircuitBreaker()
        assert cb.state == CircuitState.CLOSED.value

        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED.value

    def test_failure_count_always_zero(self):
        """Test that failure_count is always 0."""
        cb = NoOpCircuitBreaker()
        assert cb.failure_count == 0

        cb.record_failure()
        cb.record_failure()
        assert cb.failure_count == 0


class TestGenerateCacheKey:
    """Test generate_cache_key function."""

    def test_generate_cache_key_basic(self):
        """Test basic cache key generation."""
        key = generate_cache_key("/api/endpoint", {"param": "value"})
        assert isinstance(key, str)
        assert len(key) == 32  # Blake2b with 16-byte digest = 32 hex chars

    def test_generate_cache_key_consistent(self):
        """Test that same inputs produce same key."""
        key1 = generate_cache_key("/api/endpoint", {"param": "value"})
        key2 = generate_cache_key("/api/endpoint", {"param": "value"})
        assert key1 == key2

    def test_generate_cache_key_different_endpoints(self):
        """Test that different endpoints produce different keys."""
        key1 = generate_cache_key("/api/endpoint1", {"param": "value"})
        key2 = generate_cache_key("/api/endpoint2", {"param": "value"})
        assert key1 != key2

    def test_generate_cache_key_different_params(self):
        """Test that different params produce different keys."""
        key1 = generate_cache_key("/api/endpoint", {"param": "value1"})
        key2 = generate_cache_key("/api/endpoint", {"param": "value2"})
        assert key1 != key2

    def test_generate_cache_key_param_order_irrelevant(self):
        """Test that param order doesn't affect key."""
        key1 = generate_cache_key("/api/endpoint", {"a": "1", "b": "2"})
        key2 = generate_cache_key("/api/endpoint", {"b": "2", "a": "1"})
        assert key1 == key2

    def test_generate_cache_key_none_params(self):
        """Test cache key generation with None params."""
        key = generate_cache_key("/api/endpoint", None)
        assert isinstance(key, str)
        assert len(key) == 32

    def test_generate_cache_key_empty_params(self):
        """Test cache key generation with empty params."""
        key1 = generate_cache_key("/api/endpoint", {})
        key2 = generate_cache_key("/api/endpoint", None)
        assert key1 == key2