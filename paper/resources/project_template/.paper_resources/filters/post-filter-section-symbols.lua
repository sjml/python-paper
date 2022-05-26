-- Not only are section symbols (§) more visually appealing than "sec.", they're arguably
--   more correct for a variety of Church documents. So I pro-actively swap them out, unless
--   it's a newspaper article being cited.

local utils = dofile(pandoc.path.join{pandoc.path.directory(PANDOC_SCRIPT_FILE), 'util.lua'})

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
        local ref_data = utils.find_item_in_list_by_attribute(refs, "id", citation.id)
        if ref_data == nil then return nil end
        if ref_data.type == "article-newspaper" then return nil end
        return elem:walk {
          Note = function (n)
            for pi,para in pairs(n.content) do
              local newlines = para.content:walk {
                Inlines = function(inlines)
                  for i = #inlines-1, 1, -1 do
                    if inlines[i].tag == "Str" and inlines[i].text == "sec." and inlines[i+1].tag == "Space" then
                      inlines:remove(i+1)
                      inlines[i].text = "§"
                    end
                  end
                  return inlines
                end
              }
              n.content[pi].content = newlines
            end
            return n
          end
        }
      end
    end
  },
}

