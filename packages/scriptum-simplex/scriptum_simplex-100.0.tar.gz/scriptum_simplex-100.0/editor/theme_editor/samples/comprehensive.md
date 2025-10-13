# Comprehensive Theme Test Document

This document tests all markdown elements supported by Typora themes.

## Headings

# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6

## Paragraphs

This is a regular paragraph with some text. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

This is another paragraph with **bold text**, *italic text*, ***bold and italic***, ~~strikethrough~~, and `inline code`.

## Lists

### Unordered List
- Item 1
- Item 2
  - Nested item 2.1
  - Nested item 2.2
- Item 3

### Ordered List
1. First item
2. Second item
   1. Nested item 2.1
   2. Nested item 2.2
3. Third item

### Task List
- [ ] Unchecked task
- [x] Checked task
- [ ] Another unchecked task

## Links

[Inline link](https://example.com)

[Link with title](https://example.com "Example Title")

<https://autolink.com>

## Code

### Inline Code

Use `console.log()` to print to the console.

### Code Block

```python
def hello_world():
    """Print hello world."""
    print("Hello, World!")
    return True
```

```javascript
function helloWorld() {
    // Print hello world
    console.log("Hello, World!");
    return true;
}
```

## Tables

| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |

| Left Aligned | Center Aligned | Right Aligned |
|:-------------|:--------------:|--------------:|
| Left         | Center         | Right         |
| Text         | Text           | Text          |

## Blockquotes

> This is a blockquote.
> It can span multiple lines.

> Nested blockquotes:
> > This is nested
> > > And this is double nested

## Horizontal Rules

---

***

___

## Emphasis

*Italic text with asterisks*

_Italic text with underscores_

**Bold text with asterisks**

__Bold text with underscores__

***Bold and italic with asterisks***

___Bold and italic with underscores___

~~Strikethrough text~~

## Images

![Alt text](https://via.placeholder.com/150 "Image Title")

## CriticMarkup

This has {++an addition++} here.

This has {--a deletion--} here.

This has {~~old text~>new text~~} here.

This is {==highlighted text==} that's important.

This needs review {>>Check this for accuracy<<} before publishing.

## Footnotes

Here is a footnote reference[^1].

Here is another footnote[^2].

[^1]: This is the first footnote.
[^2]: This is the second footnote with more text.

## Definition Lists

Term 1
: Definition 1

Term 2
: Definition 2a
: Definition 2b

## Abbreviations

The HTML specification is maintained by the W3C.

*[HTML]: Hyper Text Markup Language
*[W3C]: World Wide Web Consortium

## Superscript and Subscript

H~2~O is water.

X^2^ is X squared.

## Highlighting

==This text is highlighted==

## Math (if supported)

Inline math: $E = mc^2$

Block math:

$$
\frac{n!}{k!(n-k)!} = \binom{n}{k}
$$

## Mixed Content

This paragraph has **bold**, *italic*, `code`, [links](https://example.com), and ~~strikethrough~~ all together.

- List item with **bold**
- List item with *italic*
- List item with `code`
- List item with [link](https://example.com)

> Blockquote with **bold**, *italic*, and `code`.

## Long Paragraph

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.

---

*End of comprehensive test document*
