require(pandoc.path.join{pandoc.path.directory(PANDOC_SCRIPT_FILE), 'util'})

local aquinas_keys = {}
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
      if not ref_data.author[1].family == "Aquinas" and ref_data[1].given == "Thomas" then
        return nil
      end
      local is_subsequent = aquinas_keys[elem.citations[1].id] == true
      aquinas_keys[elem.citations[1].id] = true

      if is_subsequent then
        elem.citations[1].mode = "SuppressAuthor"
      end
      return elem
    end
  }
}
