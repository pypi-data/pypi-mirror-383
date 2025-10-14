# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-10-14

### Added
- 🎨 Enhanced hypergraph viewer with improved visual interactions and hover effects
- 🔍 Dynamic attribute display for vertices and hyperedges in the viewer
- 📊 Key-value information display enhancement in visualization
- 🎯 Support for normal edges in 2-node entries with cluster assignment based on hyperedges
- 🌐 API endpoints for hypergraph data retrieval and dynamic data loading
- 📦 Added uv.lock to version control for reproducible builds

### Changed
- 🔧 **Major Type System Improvements**: Enhanced type annotations and fixed Liskov Substitution Principle violations
- ⚡ Improved method signatures and return types across base and derived classes
- 🎨 Refactored hypergraph viewer with better color mapping and tooltip display
- 🛠️ Enhanced CI/CD pipeline with updated release workflow and quality checks
- 📝 Updated load() and save() methods to return bool for better API consistency
- 🎛️ Improved vertex sorting logic and layout optimization in viewer
- 🔍 Better hover interactions and custom G6 library integration

### Fixed
- 🐛 Fixed mypy type errors and method signature mismatches
- 🔧 Corrected spelling of "Hypergraph" in viewer component
- 📖 Updated documentation for hypergraph visualization
- 🎯 Fixed return types for methods that should return List but were returning Set
- 💾 Improved dictionary type annotations to support various key types
- 🎨 Enhanced draw_hypergraph() function compatibility with BaseHypergraphDB

## [0.2.0] - 2025-09-09

### Added
- 📖 Chinese documentation support
- 🌐 Internationalization (i18n) configuration
- 📚 Comprehensive API documentation
- 🎨 Improved visualization interface
- Migrated documentation from Sphinx to MkDocs
- Advanced usage patterns and tutorials

### Changed
- 🔧 Better error handling
- ⚡ Performance optimizations
- 📝 More detailed code examples
- 🧪 Enhanced test coverage
- Updated project structure for modern Python development
- Migrated from Poetry to uv for dependency management
- Enhanced development workflow with automated scripts

### Fixed
- 🐛 Fixed visualization rendering issues
- 📖 Documentation and code consistency fixes
- 🔗 Fixed internal link issues

## [0.1.2] - 2024-12-22

### Fixed
- 🐛 Fixed bugs in `remove_e()` function
- 📖 Updated README documentation

## [0.1.1] - 2024-12-16

### Added
- 🧪 More comprehensive test suite
- 📊 Dedicated stress tests to ensure system stability and performance

### Changed
- ⚡ **Major Performance Improvement**: 100x speed boost for hypergraph construction and querying
  - Constructing a hypergraph with 10,000 nodes and performing 40,000 vertex and hyperedge queries
  - v0.1.0 took 90 seconds, v0.1.1 only takes 0.05 seconds
- Improved API design and consistency
- Better documentation and examples

## [0.1.0] - 2024-12-16

### Added
- 🎉 Initial release of Hypergraph-DB
- 📊 Core hypergraph data structure implementation
- 🎨 Web visualization interface
- 📖 Basic documentation and API reference
- 🧪 Basic test suite

### Core Features
- 🏗️ `Hypergraph` core class
- 🔗 Hyperedge operations
- 📊 Hypervertex operations
- 📈 Basic graph algorithms
- 🎯 Neighbor query functionality

### Visualization Features
- 🌐 Web-based hypergraph visualization
- 🎨 Interactive hypergraph display
- 📱 Responsive design
- 🎛️ Customizable visual styles

### API Features
- ➕ `add_hyperedge()` - Add hyperedge
- ➕ `add_hypervertex()` - Add hypervertex
- 🗑️ `remove_hyperedge()` - Remove hyperedge
- 🗑️ `remove_hypervertex()` - Remove hypervertex
- 📊 `degree_v()` - Calculate hypervertex degree
- 📊 `degree_e()` - Calculate hyperedge degree
- 🔍 `nbr_v_of_e()` - Query adjacent hypervertices of hyperedge
- 🔍 `nbr_e_of_v()` - Query adjacent hyperedges of hypervertex
- 🎨 `draw()` - Visualize hypergraph

[Unreleased]: https://github.com/iMoonLab/Hypergraph-DB/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/iMoonLab/Hypergraph-DB/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/iMoonLab/Hypergraph-DB/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/iMoonLab/Hypergraph-DB/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/iMoonLab/Hypergraph-DB/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/iMoonLab/Hypergraph-DB/releases/tag/v0.1.0
