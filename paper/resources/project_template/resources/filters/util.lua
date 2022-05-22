function dump(t, prefix)
  if prefix == nil then prefix = "" end
  for k,v in pairs(t) do
    print(prefix..k,v)
  end
end

function starts_with(str, start)
  return str:sub(1, #start) == start
end

function strip(str)
  return (str:gsub("^%s*(.-)%s*$", "%1"))
end

function is_str_truthy(str)
  if str == nil then
    return false
  end
  if lua_is
  numval = tonumber(str)
  if numval ~= nil then
    return numval ~= 0
  end
  str = string.lower(str)
  if str == "true" or str == "t" then
    return true
  elseif str == "yes" or str == "y" then
    return true
  end
  return false
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

function findItemInListByAttribute(list, attr, value)
  if #list == 0 then return nil end
  if attr == nil or value == nil then return nil end

  for _, item in pairs(list) do
    if item[attr] == value then
      return item
    end
  end
  return nil
end
