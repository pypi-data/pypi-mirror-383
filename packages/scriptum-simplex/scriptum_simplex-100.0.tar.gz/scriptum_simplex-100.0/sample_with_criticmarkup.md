# Sample Document with CriticMarkup

This is a **sample document** to test the enhanced renderer with *full Typora theme support*.

## Features Being Tested

### 1. Basic Markdown Elements

This paragraph demonstrates basic text rendering with proper word wrapping. The text should flow naturally within the envelope width defined by the theme, respecting margins and padding.

### 2. Lists

**Bullet List:**
- First item in the list
- Second item with more text to test wrapping
- Third item

**Numbered List:**
1. First numbered item
2. Second numbered item  
3. Third numbered item

### 3. Code Blocks

Here's a Python code block with syntax highlighting:

```python
def hello_world():
    """A simple function."""
    print("Hello, World!")
    return 42
```

Inline code looks like this: `print("Hello")` within a sentence.

### 4. CriticMarkup Annotations

**Addition:** This text has an {++added section++} in the middle.

**Deletion:** This text has a {--deleted section--} removed.

**Substitution:** Change {~~old text~>new text~~} in place.

**Highlight:** This is {==important text==} that should stand out.

**Comment:** Here's a comment {>>This needs review<<} for the editor.

### 5. Blockquotes

> This is a blockquote with a left border.
> It should have proper styling from the theme.

### 6. Horizontal Rule

---

## Conclusion

This document tests all major features of the enhanced renderer including:
- Markdown parsing with Marko
- CriticMarkup support
- Syntax highlighting with Pygments
- Full Typora theme CSS application
- Proper text wrapping and layout
