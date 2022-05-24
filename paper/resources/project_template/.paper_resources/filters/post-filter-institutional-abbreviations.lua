local utils = dofile(pandoc.path.join{pandoc.path.directory(PANDOC_SCRIPT_FILE), 'util.lua'})
dofile(pandoc.path.join{pandoc.path.directory(PANDOC_SCRIPT_FILE), 'institutional-abbreviations.lua'})

local refs = {}

return {
  {
    Pandoc = function (doc)
      refs = pandoc.utils.references(doc)
    end
  },
  {
    Cite = function (elem)
      for citation_idx, citation in pairs(elem.citations) do
        local ref_data = utils.find_item_in_list_by_attribute(refs, "id", citation.id)
        if ref_data.author == nil then return nil end
        local auth = pandoc.utils.stringify(ref_data.author)
        if institutional_abbreviations[auth] ~= nil and citation.mode == "SuppressAuthor"then
          return elem:walk {
            Note = function (n)
              local insertion_pt = 1
              if citation_idx > 1 then
                local text = n.content[1].content
                local divider_count = 0
                for i,s in pairs(text) do
                  if s.text == ";" and text[i+1].tag == "Space" then
                    divider_count = divider_count + 1
                    if divider_count == citation_idx - 1 then
                      insertion_pt = i+2
                      break
                    end
                  end
                end
              end
              table.insert(n.content[1].content, insertion_pt, pandoc.Str(institutional_abbreviations[auth]..", "))
              return n
            end
          }
        end
      end
    end
  },
}
