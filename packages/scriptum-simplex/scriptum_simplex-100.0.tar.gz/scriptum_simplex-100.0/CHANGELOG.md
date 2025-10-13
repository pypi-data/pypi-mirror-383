# Changelog

All notable changes to Scriptum Simplex will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Major UI Enhancement Release

- **Tabbed Interface**: Complete redesign with four-tab preview system
  - **Preview Tab**: Enhanced MarkdownCanvas with improved table rendering and cell padding
  - **Outline Tab**: TreeView-based document navigation with hierarchical structure
  - **Critic Tab**: Interactive CriticMarkup analysis with color-coded highlighting
  - **Supplements Tab**: Comprehensive link, footnote, and reference extraction

- **Unified CriticMarkup Highlighting**: Consistent color scheme across all panes
  - **Editor Pane**: Real-time syntax highlighting as you type
  - **Preview Pane**: Canvas-based rendering with CriticMarkup colors preserved
  - **Critic Pane**: Interactive elements with click navigation and fade effects
  - Color scheme: Green (additions), Red (deletions), Blue (substitutions), Yellow (highlights/comments)

- **Advanced Navigation Features**:
  - **Dual-pane scrolling**: Click outline items to navigate both editor and preview
  - **Clickable CriticMarkup**: Click any markup in Critic tab to jump to source line
  - **3-second fade animation**: Visual feedback when clicking CriticMarkup elements
  - **Single selection mode**: Only one element highlighted at a time

- **Enhanced Table Rendering**:
  - Improved cell padding (increased from 10px to 16px height, 12px horizontal)
  - Better text positioning with proper bottom padding
  - Canvas repaint on window resize for responsive layout
  - Professional table appearance with proper spacing

- **Document Structure Analysis**:
  - **TreeView Outline**: Clean display with bold headings, regular content text
  - **Element type indicators**: `[Code Block: python]`, `[Table]`, `[Image: alt-text]`
  - **Smart content filtering**: Shows substantial content (15+ characters)
  - **Hierarchical indentation**: Proper heading level visualization

- **Comprehensive Supplements Analysis**:
  - **Links**: Direct `[text](url)` and reference-style `[text][ref]` links
  - **Footnotes**: Full support for `[^1]: content` syntax with reference tracking
  - **Images**: `![alt](src)` with alt-text extraction
  - **Email addresses**: Automatic detection and listing
  - **Organized display**: Categorized sections with clear formatting

### Enhanced - Previous Features
- **Marko Parser Integration**: Replaced markdown2 with Marko parser for better CommonMark compliance
  - Added `editor/markdown_parser.py` - Clean adapter layer for Marko with GFM extension
  - Full GitHub Flavored Markdown support (tables, strikethrough, task lists, autolinks)
  - AST (Abstract Syntax Tree) access for advanced document manipulation
  
- **AST Support in Model**: Model now provides direct access to parsed document structure
  - `Model.get_ast()` - Returns parsed AST with intelligent caching
  - `Model.get_processed_text()` - Returns CriticMarkup-processed text with caching
  - Smart cache invalidation on text changes, new file, and file operations
  
- **Development Tools**: Added comprehensive code quality tooling
  - mypy configuration for strict type checking
  - flake8 configuration for PEP8 compliance
  - pytest-cov for test coverage reporting
  - `run_checks.py` - Automated quality check script

- **Testing**: Comprehensive test coverage for new functionality
  - 19 unit tests for MarkdownParser adapter
  - 8 new tests for Model AST functionality
  - Tests for caching behavior and cache invalidation

### Changed
- **UI Architecture**: Complete redesign from single preview to tabbed interface
  - Replaced single preview pane with four specialized tabs
  - Enhanced user experience with dedicated analysis views
  - Improved workflow for document editing and review

- **CriticMarkup Processing**: Enhanced parsing with unified color system
  - Extended `_parse_inline_formatting()` to handle CriticMarkup syntax
  - Added color mapping for all CriticMarkup types
  - Integrated highlighting across editor, preview, and analysis panes

- **Model Architecture**: Refactored to use new parser architecture
  - Replaced direct `markdown2` calls with `MarkdownParser` adapter
  - Maintained full backward compatibility with existing HTML rendering
  - Improved performance through intelligent AST caching

- **Project Name**: Renamed from "CriticMarkup Editor" to "Scriptum Simplex"
  - Updated all documentation and code comments
  - Updated window titles and UI text
  - Updated README and project structure references

### Technical Details
- Python 3.11+ required
- Added dependency: `marko>=2.0.0`
- Added dev dependencies: `mypy>=1.0.0`, `flake8>=6.0.0`, `pytest-cov>=4.0.0`
- All new code includes full type hints and passes mypy strict mode
- All new code passes flake8 linting with max line length 100

### Completed
- **Phase 5: Integration & Validation** - Final testing and documentation (100% project completion)
  - Created comprehensive test document (`test_document.md`) with all features
  - Updated README.md with table rendering documentation
  - Added table syntax examples and alignment guide
  - Updated dependency documentation
  - All 79 core tests passing
  - Code quality verified (flake8, mypy)
  - Project cleanup completed
- **Phase 4: Table Rendering** - Advanced table rendering with proper column alignment (80% project completion)
  - Implemented `CanvasRenderer.render_table()` - Extracts table data from AST
  - Implemented `MarkdownCanvas._render_table_from_ast()` - Full table rendering (237 lines)
  - Implemented `MarkdownCanvas._render_cell_text()` - Cell rendering with inline formatting
  - Dynamic column width calculation based on content
  - Proper text alignment (left/center/right) per column from markdown syntax
  - Header row with gray background and bold text
  - Table borders and cell padding
  - Auto-scaling when table exceeds available width
  - Support for inline formatting in cells (**bold**, *italic*, `code`)
  - 19 comprehensive unit tests in `tests/test_table_rendering.py` (all passing)
  - **Total: 79 tests passing across all core modules**

- **Phase 3: Custom Canvas Renderer** - Direct AST-to-Canvas rendering (60% project completion)
  - Created `editor/canvas_renderer.py` - Custom Marko renderer that outputs to MarkdownCanvas
  - Created `editor/render_styles.py` - Flexible style system for future theme support
  - Implemented renderers for all Markdown elements (headings, lists, paragraphs, code, quotes)
  - 17 comprehensive unit tests in `tests/test_canvas_renderer.py` (all passing)
  - Reuses 100% of existing MarkdownCanvas rendering logic
  - Built-in style themes (Default, Typora-inspired, GitHub-inspired)
  - Bypasses HTML as intermediate format for improved performance

---

## [0.1.0] - 2024-XX-XX (Previous Version)

### Added
- Initial release of CriticMarkup Editor
- Two-pane Markdown editor with live preview
- Full CriticMarkup syntax support (additions, deletions, substitutions, comments, highlights)
- File operations (New, Open, Save, Save As)
- MVC architecture (Model-View-Controller)
- Custom MarkdownCanvas widget for rendering
- Modern UI with TTK Bootstrap
- Basic Markdown support (headings, lists, code blocks, inline formatting)
- Cross-platform support (Windows, macOS, Linux)

### Known Limitations (to be addressed in future releases)
- Table rendering incomplete (placeholder implementation)
- Limited Markdown parsing capabilities with markdown2
- No AST access for advanced document manipulation
