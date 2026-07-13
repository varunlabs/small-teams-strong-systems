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
