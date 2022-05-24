local utils = dofile(pandoc.path.join{pandoc.path.directory(PANDOC_SCRIPT_FILE), 'util.lua'})

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
      for _, citation in pairs(elem.citations) do
        local ref_data = utils.findItemInListByAttribute(refs, "id", citation.id)
        if ref_data == nil or ref_data.author == nil then return nil end
        if not ref_data.author[1].family == "Aquinas" and ref_data[1].given == "Thomas" then
          return nil
        end
        local is_subsequent = aquinas_keys[citation.id] == true
        aquinas_keys[citation.id] = true

        if is_subsequent then
          citation.mode = "SuppressAuthor"
        end
      end
      return elem
    end
  }
}
