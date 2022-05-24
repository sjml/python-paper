local utils = dofile(pandoc.path.join{pandoc.path.directory(PANDOC_SCRIPT_FILE), 'util.lua'})
dofile(pandoc.path.join{pandoc.path.directory(PANDOC_SCRIPT_FILE), 'institutional-abbreviations.lua'})

local refs = {}
local seen_authors = {}

return {
  {
    Pandoc = function (doc)
      refs = pandoc.utils.references(doc)
    end
  },
  {
    Cite = function (elem)
      for _, citation in pairs(elem.citations) do
        local ref_data = utils.find_item_in_list_by_attribute(refs, "id", citation.id)
        if ref_data.author == nil then return nil end
        local auth = pandoc.utils.stringify(ref_data.author)
        if seen_authors[auth] == true and institutional_abbreviations[auth] ~= nil then
          citation.mode = "SuppressAuthor"
        end

        seen_authors[auth] = true
      end
      return elem
    end
  },
}
