"""
Syntax Highlighting for Code Blocks

Uses Pygments to provide syntax highlighting for code blocks.
"""

from pygments import lex
from pygments.lexers import get_lexer_by_name, guess_lexer, PythonLexer
from pygments.token import Token
from typing import List, Tuple


# Token type to color mapping (GitHub Dark style)
GITHUB_DARK_COLORS = {
    Token.Keyword: '#ff7b72',  # Keywords (def, class, if, etc.)
    Token.Keyword.Namespace: '#ff7b72',
    Token.Keyword.Type: '#ff7b72',
    Token.Name.Function: '#d2a8ff',  # Function names
    Token.Name.Class: '#f0883e',  # Class names
    Token.Name.Builtin: '#79c0ff',  # Built-in functions
    Token.String: '#a5d6ff',  # Strings
    Token.String.Doc: '#8b949e',  # Docstrings
    Token.Number: '#79c0ff',  # Numbers
    Token.Comment: '#8b949e',  # Comments
    Token.Comment.Single: '#8b949e',
    Token.Comment.Multiline: '#8b949e',
    Token.Operator: '#ff7b72',  # Operators
    Token.Punctuation: '#c9d1d9',  # Punctuation
    Token.Name: '#c9d1d9',  # Default names
    Token.Text: '#c9d1d9',  # Default text
}

# Fallback colors for token types not in the map
DEFAULT_COLOR = '#c9d1d9'


def get_token_color(token_type) -> str:
    """
    Get color for a token type.
    
    Args:
        token_type: Pygments token type
        
    Returns:
        Hex color string
    """
    # Try exact match first
    if token_type in GITHUB_DARK_COLORS:
        return GITHUB_DARK_COLORS[token_type]
    
    # Try parent types
    while token_type.parent:
        if token_type in GITHUB_DARK_COLORS:
            return GITHUB_DARK_COLORS[token_type]
        token_type = token_type.parent
    
    return DEFAULT_COLOR


def highlight_code(code: str, language: str = None) -> List[Tuple[str, str]]:
    """
    Highlight code and return list of (text, color) tuples.
    
    Args:
        code: Code to highlight
        language: Programming language (e.g., 'python', 'javascript')
        
    Returns:
        List of (text, color) tuples
    """
    # Get lexer
    try:
        if language:
            lexer = get_lexer_by_name(language, stripall=False)
        else:
            # Try to guess the language
            lexer = guess_lexer(code)
    except:
        # Fallback to Python lexer
        lexer = PythonLexer()
    
    # Tokenize and colorize
    result = []
    for token_type, text in lex(code, lexer):
        color = get_token_color(token_type)
        result.append((text, color))
    
    return result


def detect_language(code: str) -> str:
    """
    Try to detect the programming language from code.
    
    Args:
        code: Code snippet
        
    Returns:
        Language name or 'text'
    """
    try:
        lexer = guess_lexer(code)
        return lexer.name.lower()
    except:
        return 'text'
