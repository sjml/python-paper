require(pandoc.path.join{pandoc.path.directory(PANDOC_SCRIPT_FILE), 'util'})

function Cite (elem)
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
