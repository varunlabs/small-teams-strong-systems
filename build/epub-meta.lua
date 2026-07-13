-- Small Teams, Strong Systems — used only for the v1 EPUB -> PDF build.
-- The v1 EPUB already contains its own title page (title_page.xhtml, the first
-- spine item). Pandoc would otherwise ALSO emit an automatic \maketitle page
-- from the EPUB's title/author metadata, producing a duplicate title page.
-- Clearing the document metadata title/author/date suppresses that auto page
-- and lets the EPUB's own title page stand. Content is untouched.
function Meta(m)
  m.title = nil
  m.subtitle = nil
  m.author = nil
  m.date = nil
  return m
end

-- In the v1 EPUB, front-matter items and Part dividers are BOTH top-level (h1),
-- while chapters are h2. With --top-level-division=part that maps every h1 to a
-- LaTeX \part, so front-matter items (Author's Note, How to Read, ...) render as
-- a title alone on one page with the body pushed to the next — the same "empty
-- page" look we removed elsewhere. Keep the true "Part ..." dividers as parts,
-- but demote the other top-level headings to chapter level so their title and
-- body sit together, matching the v2 layout.
function Header(el)
  if el.level == 1 then
    local txt = pandoc.utils.stringify(el)
    if not txt:match("^Part%s") then
      el.level = 2
      return el
    end
  end
end
