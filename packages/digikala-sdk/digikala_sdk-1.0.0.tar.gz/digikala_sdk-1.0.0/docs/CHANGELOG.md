# Changelog

All notable changes to the Digikala SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-14

### Added

#### Core Features
- 🚀 Initial release of Digikala SDK
- ✅ Fully asynchronous Python SDK built on `httpx` and `pydantic`
- 📦 Complete type-safe models with Pydantic v2
- 🔄 Automatic retry logic with exponential backoff
- 🛡️ Comprehensive exception hierarchy for error handling

#### API Services
- **Products Service**
  - `get_product()` - Get detailed product information by ID
  - `search()` - Search products with pagination support
  - Support for active and inactive products with discriminated unions

- **Sellers Service**
  - `get_seller_products()` - Get seller products with pagination
  - `get_seller_info()` - Get seller information (convenience method)

- **Brands Service**
  - `get_brand_products()` - Get brand products with pagination
  - `get_brand_info()` - Get brand information (convenience method)

#### Advanced Features
- ⚡ **Client-side rate limiting** (requires `aiolimiter`)
  - Configurable requests per minute
  - Automatic request throttling
  - Detailed logging for rate limit events

- 💾 **Response caching** (requires `aiocache`)
  - Memory cache backend
  - Redis cache backend
  - Configurable TTL
  - Automatic cache key generation
  - Only caches GET requests

- 🔧 **Connection pool management**
  - Configurable pool limits
  - Keep-alive connection management
  - Efficient resource utilization

#### Configuration
- `DigikalaConfig` dataclass with comprehensive options:
  - Authentication (API key or Bearer token)
  - Timeout and retry settings
  - Connection pool settings
  - Rate limiting configuration
  - Cache configuration

#### Error Handling
- Complete exception hierarchy:
  - `DigikalaAPIError` (base exception)
  - `BadRequestError` (400)
  - `UnauthorizedError` (401)
  - `ForbiddenError` (403)
  - `NotFoundError` (404)
  - `RateLimitError` (429)
  - `ServerError` (5xx)
  - `TimeoutError`
  - `ConnectionError`
  - `ValidationError`

#### Security
- Request parameter validation
- Injection attack prevention (XSS, path traversal, etc.)
- HTTP method whitelisting
- Endpoint format validation

#### Documentation
- 📚 Complete SDK documentation
- 📖 Detailed API reference for each module:
  - Products API documentation
  - Sellers API documentation
  - Brands API documentation
- 💡 Quick start guide
- ⚠️ Error handling guide
- 🎯 Real-world usage examples
- 📊 Best practices guide

#### Testing
- 🧪 Comprehensive test suite with 67 tests
- ✅ 95%+ test coverage
- Unit tests for all services
- Integration tests for error handling
- Validation tests for models
- Connection pool tests

#### Development Tools
- Optional dependencies support:
  - `[dev]` - Development dependencies
  - `[ratelimit]` - Rate limiting support
  - `[cache]` - Caching support
  - `[full]` - All optional features

### Changed
- N/A (initial release)

### Deprecated
- N/A (initial release)

### Removed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- ✅ Request parameter validation to prevent injection attacks
- ✅ Secure handling of authentication credentials
- ✅ No sensitive data in logs

---

## [Unreleased]

### Planned Features
- [ ] Additional API modules (categories, comments, etc.)
- [ ] Webhook support
- [ ] Batch operations API
- [ ] GraphQL support (if available)
- [ ] CLI tool for SDK operations
- [ ] Prometheus metrics exporter
- [ ] OpenTelemetry integration

### Under Consideration
- [ ] Sync API wrapper (for non-async applications)
- [ ] Request/response middleware system
- [ ] Custom cache serializers
- [ ] Connection pool monitoring
- [ ] Automatic API schema validation

---

## Version History

| Version | Release Date | Highlights |
|---------|--------------|------------|
| 1.0.0 | 2025-10-14 | Initial release with Products, Sellers, and Brands APIs |

---

## Migration Guides

### Migrating from 0.x to 1.0.0
N/A - This is the initial release

---

## Breaking Changes

### Version 1.0.0
- N/A (initial release)

---

## Deprecation Notices

### Version 1.0.0
- N/A (initial release)

---

## Credits

### Contributors
- Digikala SDK Team

### Third-Party Libraries
- [httpx](https://www.python-httpx.org/) - Async HTTP client
- [pydantic](https://docs.pydantic.dev/) - Data validation
- [aiolimiter](https://github.com/mjpieters/aiolimiter) (optional) - Rate limiting
- [aiocache](https://github.com/aio-libs/aiocache) (optional) - Caching

---

## Support

For questions, issues, or feature requests:
- 📚 [Documentation](SDK_Documentation.md)
- 🐛 [GitHub Issues](https://github.com/digikala/digikala-sdk/issues)
- 💬 [GitHub Discussions](https://github.com/digikala/digikala-sdk/discussions)

---

<div align="center">

**[Back to Documentation](SDK_Documentation.md)**

</div>