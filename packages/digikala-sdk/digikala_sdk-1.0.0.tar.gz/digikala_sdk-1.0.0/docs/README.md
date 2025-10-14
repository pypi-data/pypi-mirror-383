# Digikala SDK Documentation

Welcome to the Digikala SDK documentation! This directory contains comprehensive guides for using the SDK.

## 📚 Documentation Structure

### Main Documentation
- **[SDK_Documentation.md](SDK_Documentation.md)** - Complete SDK manual with installation, configuration, and usage guides

### API Module Documentation
Each API module has its own detailed documentation:

| Module | File | Description |
|--------|------|-------------|
| **Products API** | [products.md](products.md) | Product details and search operations |
| **Sellers API** | [sellers.md](sellers.md) | Seller information and product listings |
| **Brands API** | [brands.md](brands.md) | Brand information and product listings |

## 🚀 Quick Links

### Getting Started
1. [Introduction](SDK_Documentation.md#introduction)
2. [Installation](SDK_Documentation.md#installation)
3. [Quick Start](SDK_Documentation.md#quick-start)
4. [Configuration](SDK_Documentation.md#configuration)

### API References
- [Products API](products.md) - Get product details, search products
- [Sellers API](sellers.md) - Get seller info, list seller products
- [Brands API](brands.md) - Get brand info, list brand products

### Advanced Topics
- [Advanced Features](SDK_Documentation.md#advanced-features) - Rate limiting, caching
- [Error Handling](SDK_Documentation.md#error-handling) - Exception hierarchy and handling
- [Best Practices](SDK_Documentation.md#best-practices) - Recommended patterns
- [Examples](SDK_Documentation.md#examples) - Real-world use cases

## 📖 Documentation Overview

### SDK_Documentation.md
The main SDK manual covering:
- ✅ Installation and setup
- ✅ Basic and advanced configuration
- ✅ All API modules overview
- ✅ Error handling guide
- ✅ Best practices
- ✅ Complete examples
- ✅ Troubleshooting guide

**Size**: ~22 KB | **Sections**: 15

### products.md
Complete Products API reference:
- ✅ `get_product()` - Get product by ID
- ✅ `search()` - Search products with pagination
- ✅ Response models and schemas
- ✅ Error handling examples
- ✅ Best practices for product operations
- ✅ Real-world usage examples

**Size**: ~10 KB | **Methods**: 2

### sellers.md
Complete Sellers API reference:
- ✅ `get_seller_products()` - Get seller products with pagination
- ✅ `get_seller_info()` - Get seller information
- ✅ Response models and schemas
- ✅ Seller performance analysis examples
- ✅ Use cases: comparison, monitoring, export
- ✅ Best practices for seller operations

**Size**: ~13 KB | **Methods**: 2

### brands.md
Complete Brands API reference:
- ✅ `get_brand_products()` - Get brand products with pagination
- ✅ `get_brand_info()` - Get brand information
- ✅ Response models and schemas
- ✅ Brand analysis and comparison examples
- ✅ Use cases: portfolio analysis, dashboards
- ✅ Best practices for brand operations

**Size**: ~18 KB | **Methods**: 2

## 🎯 What's Included

Each documentation file includes:

### Method Documentation
- ✅ Method signature with type hints
- ✅ Parameter descriptions (name, type, required/optional)
- ✅ Return type descriptions
- ✅ Exception documentation
- ✅ Multiple usage examples

### Code Examples
- ✅ Basic usage examples
- ✅ Advanced usage patterns
- ✅ Error handling examples
- ✅ Real-world use cases
- ✅ Best practice demonstrations

### Response Models
- ✅ Complete JSON schemas
- ✅ Field descriptions
- ✅ Type information
- ✅ Optional field indicators

## 📊 Documentation Statistics

| Metric | Value |
|--------|-------|
| Total Files | 4 |
| Total Size | ~63 KB |
| Code Examples | 50+ |
| API Methods Documented | 6 |
| Use Cases | 12+ |

## 🔍 How to Use This Documentation

### 1. Start Here
If you're new to the SDK:
1. Read [SDK_Documentation.md](SDK_Documentation.md#quick-start)
2. Try the [Quick Start](SDK_Documentation.md#quick-start) examples
3. Review [Configuration](SDK_Documentation.md#configuration) options

### 2. API References
When working with specific APIs:
- Need product data? → [products.md](products.md)
- Need seller data? → [sellers.md](sellers.md)
- Need brand data? → [brands.md](brands.md)

### 3. Advanced Usage
For production applications:
1. Review [Advanced Features](SDK_Documentation.md#advanced-features)
2. Implement [Error Handling](SDK_Documentation.md#error-handling)
3. Follow [Best Practices](SDK_Documentation.md#best-practices)

### 4. Troubleshooting
Having issues?
1. Check [Troubleshooting](SDK_Documentation.md#troubleshooting) guide
2. Review [Error Handling](SDK_Documentation.md#error-handling) examples
3. Search for similar examples in module docs

## 🎨 Documentation Features

### Interactive Examples
All code examples are:
- ✅ **Runnable** - Copy-paste ready
- ✅ **Complete** - Include all imports and setup
- ✅ **Tested** - Verified to work with SDK
- ✅ **Commented** - Clear explanations

### Progressive Learning
Documentation follows a learning path:
1. **Basic** - Simple, single-operation examples
2. **Intermediate** - Multi-step operations with error handling
3. **Advanced** - Production-ready patterns with optimization

### Real-World Focus
Examples based on actual use cases:
- Price monitoring and comparison
- Seller performance analysis
- Brand portfolio management
- Product catalog export
- Data aggregation and reporting

## 📝 Documentation Standards

All documentation follows these standards:

### Code Style
- ✅ PEP 8 compliant
- ✅ Type hints included
- ✅ Async/await patterns
- ✅ Context manager usage

### Example Quality
- ✅ Self-contained
- ✅ Error handling included
- ✅ Resource cleanup shown
- ✅ Best practices demonstrated

### Content Organization
- ✅ Consistent structure across files
- ✅ Cross-references between docs
- ✅ Table of contents for navigation
- ✅ Clear section hierarchy

## 🔗 External Resources

- **Main README**: [../README.md](../README.md)
- **Examples Directory**: [../examples/](../examples/)
- **Tests**: [../tests/](../tests/)
- **Source Code**: [../src/](../src/)

## 💡 Tips for Using the Documentation

### Quick Reference
Use Ctrl+F (Cmd+F on Mac) to search for:
- Specific method names
- Error types
- Configuration options
- Example patterns

### Navigation
- Start from [SDK_Documentation.md](SDK_Documentation.md) for overview
- Jump to specific API docs for detailed references
- Use cross-references to explore related topics

### Learning Path
1. **Day 1**: Read Quick Start, try basic examples
2. **Day 2**: Explore one API module in depth
3. **Day 3**: Learn configuration and error handling
4. **Day 4**: Study advanced features and best practices
5. **Day 5**: Build your first production application

## 🆘 Getting Help

If you can't find what you need:

1. **Search Documentation**: Use Ctrl+F to search all docs
2. **Check Examples**: Review the [Examples](SDK_Documentation.md#examples) section
3. **Review Tests**: Check [../tests/](../tests/) for more usage patterns
4. **Ask Questions**: Open an issue on GitHub

## 📅 Documentation Updates

This documentation is:
- ✅ Up-to-date with SDK version 1.0.0
- ✅ Covers all public APIs
- ✅ Includes latest features (rate limiting, caching)
- ✅ Reflects current best practices

Last updated: October 14, 2025

---

<div align="center">

**Happy Coding! 🚀**

[SDK Documentation](SDK_Documentation.md) | [Products](products.md) | [Sellers](sellers.md) | [Brands](brands.md)

</div>