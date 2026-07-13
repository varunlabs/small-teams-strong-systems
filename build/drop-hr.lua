-- Small Teams, Strong Systems — PDF build filter (rendering only, no content edits)

-- 1. Remove standalone horizontal-rule dividers ("---") from the PDF.
--    In the book class every front-matter section and chapter already opens on
--    a fresh page, so these decorative rules are redundant and, when a section
--    fills a page exactly, orphan onto a near-blank page.
function HorizontalRule(_)
  return {}
end

-- 2. Keep each figure (caption + diagram) together on one page.
--    Figures are authored as a blockquote holding a bold "Figure X" caption
--    followed by the image. A LaTeX quote can break across a page boundary,
--    stranding the caption on one page and the diagram on the next. Wrapping
--    the figure in an unbreakable minipage forces the whole thing onto a single
--    page; if it does not fit in the remaining space, it moves to the next page
--    as one unit. Plain text blockquotes (epigraphs) are left untouched.
function BlockQuote(el)
  local has_image = false
  pandoc.walk_block(el, {
    Image = function(_) has_image = true end
  })
  if not has_image then
    return nil
  end
  local open = pandoc.RawBlock('latex',
    '\\par\\bigskip\\noindent\\begin{minipage}{\\linewidth}\\centering')
  local close = pandoc.RawBlock('latex',
    '\\end{minipage}\\par\\bigskip')
  local out = { open }
  for _, b in ipairs(el.content) do
    out[#out + 1] = b
  end
  out[#out + 1] = close
  return out
end
