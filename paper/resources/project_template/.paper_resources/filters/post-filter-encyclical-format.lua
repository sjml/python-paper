local utils = dofile(pandoc.path.join{pandoc.path.directory(PANDOC_SCRIPT_FILE), 'util.lua'})

local refs = {}

function lowerWalk(elem)
  return elem:walk {
    Str = function(s)
      return pandoc.Str(s.text:lower())
    end
  }
end

function fixCase(target, searchElem)
  local lowered = lowerWalk(target)
  if searchElem.tag == lowered.tag then
    local lowered_search = lowerWalk(searchElem)
    if lowered_search == lowered then
      return target
    end
  end
  return nil
end

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
        if not utils.has_keyword(ref_data, "Papal Encyclical") then return nil end
        local proper = ref_data["title-short"][1]
        return elem:walk {
          Block = function(e)
            return fixCase(proper, e)
          end,
          Inline = function(e)
            return fixCase(proper, e)
          end,
          Span = function(s)
            if s.content[1].text == "“" and s.content[#s.content].text == "”" then
              s.content:remove(1)
              s.content:remove(#s.content)
              return s
            end
          end,
        }
      end
    end,

    Div = function (elem)
      if utils.starts_with(elem.attr.identifier, "ref-") then
        local ref_data = utils.find_item_in_list_by_attribute(refs, "id", elem.attr.identifier:sub(#"ref-"+1))
        if not utils.has_keyword(ref_data, "Papal Encyclical") then return nil end
        local proper = ref_data["title-short"][1]
        return elem:walk {
          Block = function(e)
            return fixCase(proper, e)
          end,
          Inline = function(e)
            return fixCase(proper, e)
          end,
        }
      end
    end
  }
}
