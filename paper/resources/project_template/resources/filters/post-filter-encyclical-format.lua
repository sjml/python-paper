require(pandoc.path.join{pandoc.path.directory(PANDOC_SCRIPT_FILE), 'util'})

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
    local loweredSearch = lowerWalk(searchElem)
    if loweredSearch == lowered then
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
        local ref_data = findItemInListByAttribute(refs, "id", citation.id)
        if not has_keyword(ref_data, "Papal Encyclical") then return nil end
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
    end,

    Div = function (elem)
      if starts_with(elem.attr.identifier, "ref-") then
        local ref_data = findItemInListByAttribute(refs, "id", elem.attr.identifier:sub(#"ref-"+1))
        if not has_keyword(ref_data, "Papal Encyclical") then return nil end
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
