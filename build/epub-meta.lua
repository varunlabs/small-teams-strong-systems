-- Small Teams, Strong Systems — used only for the v1 EPUB -> PDF build.
--
-- 1. The v1 EPUB already contains its own title page (title_page.xhtml, the
--    first spine item). Pandoc would otherwise ALSO emit an automatic
--    \maketitle page from the EPUB's title/author metadata, producing a
--    duplicate title page. Clearing the document metadata suppresses that.
function Meta(m)
  m.title = nil
  m.subtitle = nil
  m.author = nil
  m.date = nil
  return m
end

-- 2. Reproduce how the EPUB reads in a reader. In the v1 EPUB, front-matter
--    items and Part dividers are BOTH top-level (h1) and chapters are h2. With
--    --top-level-division=part that maps h1 -> \part, h2 -> \chapter (each
--    chapter opens a fresh page, as the reader shows), h3 -> \section (flows).
--    But front-matter items (Author's Note, How to Read, ...) should not become
--    \part divider pages (title alone, body overleaf). Keep the real "Part ..."
--    dividers at part level and demote the other top-level headings to chapter
--    level, so their title and body stay together.
function Header(el)
  if el.level == 1 then
    local txt = pandoc.utils.stringify(el)
    if not txt:match("^Part%s") then
      el.level = 2
      return el
    end
  end
end
