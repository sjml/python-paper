require(pandoc.path.join{pandoc.path.directory(PANDOC_SCRIPT_FILE), 'util'})
require(pandoc.path.join{pandoc.path.directory(PANDOC_SCRIPT_FILE), 'institutional-abbreviations'})


local refs = {}
local seenAuthors = {}

return {
  {
    Pandoc = function (doc)
      refs = pandoc.utils.references(doc)
    end
  },
  {
    Cite = function (elem)
      local ref_data = findItemInListByAttribute(refs, "id", elem.citations[1].id)
      if ref_data.author == nil then return nil end
      local auth = pandoc.utils.stringify(ref_data.author)
      if seenAuthors[auth] == true and institutional_abbreviations[auth] ~= nil then
        elem.citations[1].mode = "SuppressAuthor"
      end

      seenAuthors[auth] = true
      return elem
    end
  },
}
