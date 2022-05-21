function starts_with(str, start)
  return str:sub(1, #start) == start
end

function strip(str)
  return (str:gsub("^%s*(.-)%s*$", "%1"))
end

function is_string_in_list(str, list)
  for _,s in pairs(list) do
    if s == str then
      return true
    end
  end
  return false
end

function count_table_entries(tbl)
  count = 0
  for _ in pairs(tbl) do
    count = count + 1
  end
  return count
end
