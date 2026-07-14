-- Small Teams, Strong Systems — used only for the v1 EPUB -> PDF build.
-- Faithful reproduction of the published EPUB; content is never altered.

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

-- 2. Reproduce how the EPUB reads. In the v1 EPUB, front-matter items and Part
--    dividers are BOTH top-level (h1) and chapters are h2. With
--    --top-level-division=part that maps h1 -> \part, h2 -> \chapter (each
--    chapter opens a fresh page, as the EPUB shows), h3 -> \section (flows).
--    Front-matter items (Author's Note, How to Read, ...) must not become \part
--    divider pages, so keep the real "Part ..." dividers at part level and demote
--    the other top-level headings to chapter level (title + body stay together).
function Header(el)
  if el.level == 1 then
    local txt = pandoc.utils.stringify(el)
    if not txt:match("^Part%s") then
      el.level = 2
      return el
    end
  end
end

-- 3. Place the Table of Contents in its EPUB / front-matter position — after
--    "Who This Book Is For" and immediately before the Introduction — NOT forced
--    to the first page. (Pandoc's own --toc can only sit at the very front, so we
--    insert it here instead and omit --toc.)
function Pandoc(doc)
  local blocks = {}
  local inserted = false
  for _, b in ipairs(doc.blocks) do
    if (not inserted) and b.t == "Header"
        and pandoc.utils.stringify(b):match("^Introduction") then
      table.insert(blocks, pandoc.RawBlock("latex",
        "\\cleardoublepage\\setcounter{tocdepth}{2}\\tableofcontents\\clearpage"))
      inserted = true
    end
    table.insert(blocks, b)
  end
  return pandoc.Pandoc(blocks, doc.meta)
end
