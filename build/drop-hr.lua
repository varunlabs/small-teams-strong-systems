-- Small Teams, Strong Systems — PDF build filter
-- Removes standalone horizontal-rule dividers ("---") from the PDF only.
-- In the book class every front-matter section and chapter already opens on
-- a fresh page, so these decorative rules are redundant and, when a section
-- fills a page exactly, orphan onto a near-blank page (e.g. old page 16).
-- Manuscript .md content is never modified — this affects rendering only.
function HorizontalRule(_)
  return {}
end
