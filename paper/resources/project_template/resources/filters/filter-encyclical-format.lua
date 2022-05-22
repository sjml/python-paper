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
      local ref_data = findItemInListByAttribute(refs, "id", elem.citations[1].id)
      if not has_keyword(ref_data, "Papal Encyclical") then return nil end
      local is_subsequent = encyclical_keys[elem.citations[1].id] == true
      encyclical_keys[elem.citations[1].id] = true

      if is_subsequent then
        elem.citations[1].mode = "SuppressAuthor"
      end
      return elem
    end
  }
}
