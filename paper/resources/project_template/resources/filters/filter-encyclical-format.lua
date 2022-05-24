require(pandoc.path.join{pandoc.path.directory(PANDOC_SCRIPT_FILE), 'util'})

local encyclical_keys = {}
local refs = {}

return {
  {
    Pandoc = function (doc)
      refs = pandoc.utils.references(doc)
    end
  },

  {
    Cite = function (elem)
      for _, citation in pairs(elem.citations) do
        local ref_data = findItemInListByAttribute(refs, "id", citation.id)
        if not has_keyword(ref_data, "Papal Encyclical") then return nil end
        local is_subsequent = encyclical_keys[citation.id] == true
        encyclical_keys[citation.id] = true

        if is_subsequent then
          citation.mode = "SuppressAuthor"
        end
      end
      return elem
    end
  }
}
