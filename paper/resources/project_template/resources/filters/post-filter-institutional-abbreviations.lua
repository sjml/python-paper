require(pandoc.path.join{pandoc.path.directory(PANDOC_SCRIPT_FILE), 'util'})
require(pandoc.path.join{pandoc.path.directory(PANDOC_SCRIPT_FILE), 'institutional-abbreviations'})


local refs = {}

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
      if institutional_abbreviations[auth] ~= nil and elem.citations[1].mode == "SuppressAuthor"then
        return elem:walk {
          Note = function (n)
            table.insert(n.content[1].content, 1, pandoc.Str(institutional_abbreviations[auth]..", "))
            return n
          end
        }
      end
    end
  },
}
