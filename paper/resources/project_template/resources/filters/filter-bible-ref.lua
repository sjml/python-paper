-- Unlike the rest of Chicago style, biblical citations should be parenthetical inline.
-- The first citation needs to mention the translation being used. e.g.: (John 1:1 _NABRE_)
-- After that, the translation is dropped **unless** there are multiple translations being
--   used, in which case each citation includes the translation.
--
-- This filter will also normalize biblical book names to the preferred SBL abbreviation.
--

require(pandoc.path.join{pandoc.path.directory(PANDOC_SCRIPT_FILE), 'util'})

-- first two in each table are "canonical" names,
--   with the second being the standard SBL abbreviation
local bible_books = {
  {"Genesis", "Gen", nil, "Gn", "Ge"},
  {"Exodus", "Ex", nil, "Ex", "Exo", "Exod"},
  {"Leviticus", "Lev", nil, "Lv", "Le"},
  {"Numbers", "Num", nil, "Nb", "Nu", "Nm"},
  {"Deuteronomy", "Deut", nil, "Dt", "De"},
  {"Joshua", "Josh", nil, "Jos", "Jsh"},
  {"Judges", "Judg", nil, "Jdg", "Jg", "Jdgs"},
  {"Ruth", "Ruth", nil, "Rth", "Ru"},
  {"1 Samuel", "1 Sam", nil, "1 Sa", "1Sa", "1Sam", "1Samuel"},
  {"2 Samuel", "2 Sam", nil, "2 Sa", "2Sa", "2Sam", "2Samuel"},
  {"1 Kings", "1 Kgs", nil, "1Kgs", "1Kings"},
  {"2 Kings", "2 Kgs", nil, "2Kgs", "2Kings"},
  {"1 Chronicles", "1 Chr", nil, "1Chr", "1 Ch", "1Ch", "1 Chron", "1Chron", "1Chronicles"},
  {"2 Chronicles", "2 Chr", nil, "2Chr", "2 Ch", "2Ch", "2 Chron", "2Chron", "2Chronicles"},
  {"Ezra", "Ezra", nil, "Ez", "Ezr"},
  {"Nehemiah", "Neh", nil, "Ne"},
  {"Esther", "Esth", nil, "Es", "Est"},
  {"Job", "Job", nil, "Jb"},
  {"Psalms", "Pss", nil, "Ps", "Psa", "Psm"},
  {"Proverbs", "Prov", nil, "Pr", "Pro", "Prv"},
  {"Ecclesiastes", "Eccl", "Qoh", "Ec", "Ecc", "Eccle", "Eccles"},
  {"Song of Songs", "Song", "Cant", "So", "Canticles"},
  {"Isaiah", "Isa", nil, "Is"},
  {"Jeremiah", "Jer", nil, "Je", "Jr"},
  {"Lamentations", "Lam", nil, "La"},
  {"Ezekial", "Ezek", nil, "Eze", "Ezk"},
  {"Daniel", "Dan", nil, "Dn", "Da"},
  {"Hosea", "Hos", nil, "Ho"},
  {"Joel", "Joel", nil, "Jl"},
  {"Amos", "Amos", nil, "Am"},
  {"Obadiah", "Obad", nil, "Ob"},
  {"Jonah", "Jonah", nil, "Jnh", "Jon"},
  {"Micah", "Mic", nil, "Mc"},
  {"Nahum", "Nah", nil, "Na"},
  {"Habakkuk", "Hab", nil, "Hb"},
  {"Zephaniah", "Zeph", nil, "Zp", "Zep"},
  {"Haggai", "Hag", nil, "Hg"},
  {"Zechariah", "Zech", nil, "Zc", "Zec"},
  {"Malachi", "Mal", nil, "Ml"},
  {"Matthew", "Matt", nil, "Mt"},
  {"Mark", "Mark", nil, "Mk", "Mrk"},
  {"Luke", "Luke", nil, "Lk", "Luk"},
  {"John", "John", nil, "Jn", "Jhn"},
  {"Acts", "Acts", nil, "Ac", "Act"},
  {"Romans", "Rom", nil, "Ro", "Rm"},
  {"1 Corinthians", "1 Cor", nil, "1Cor", "1 Co", "1Co", "1Corinthians"},
  {"2 Corinthians", "2 Cor", nil, "2Cor", "2 Co", "2Co", "2Corinthians"},
  {"Galations", "Gal", nil, "Ga"},
  {"Ephesians", "Eph", nil, "Ephes"},
  {"Philippians", "Phil", nil, "Php", "Pp"},
  {"Colossians", "Col", nil, "Co"},
  {"1 Thessalonians", "1 Thess", nil, "1Thess", "1 Thes", "1Thes", "1 Th", "1Th", "1Thessalonians"},
  {"2 Thessalonians", "2 Thess", nil, "2Thess", "2 Thes", "2Thes", "2 Th", "2Th", "2Thessalonians"},
  {"1 Timothy", "1 Tim", nil, "1Tim", "1 Ti", "1Ti"},
  {"2 Timothy", "2 Tim", nil, "2Tim", "2 Ti", "2Ti"},
  {"Titus", "Titus", nil, "Ti", "Tit"},
  {"Philemon", "Phlm", nil, "Pm", "Philem", "Phm"},
  {"Hebrews", "Heb"},
  {"James", "Jas", nil, "Jm"},
  {"1 Peter", "1 Pet", nil, "1Pet", "1 Pe", "1Pe", "1 Pt", "1Pt", "1Peter"},
  {"2 Peter", "2 Pet", nil, "2Pet", "2 Pe", "2Pe", "2 Pt", "2Pt", "2Peter"},
  {"1 John", "1 John", nil, "1John", "1 Jn", "1Jn", "1 Jhn", "1Jhn"},
  {"2 John", "2 John", nil, "2John", "2 Jn", "2Jn", "2 Jhn", "2Jhn"},
  {"3 John", "3 John", nil, "3John", "3 Jn", "3Jn", "3 Jhn", "3Jhn"},
  {"Jude", "Jude", nil, "Jd", "Jud"},
  {"Revelation", "Rev", nil, "Re", "Rv"},
  {"Baruch", "Bar"},
  {"1 Esdras", "1 Esd", nil, "1Esd", "1 Esdr", "1Esdr", "1Esdras"},
  {"2 Esdras", "2 Esd", nil, "2Esd", "2 Esdr", "2Esdr", "2Esdras"},
  {"Judith", "Jdt", nil, "Jth", "Jdth"},
  {"1 Maccabees", "1 Macc", nil, "1Macc", "1 Mac", "1Mac", "1 Ma", "1Ma", "1Maccabees"},
  {"2 Maccabees", "2 Macc", nil, "2Macc", "2 Mac", "2Mac", "2 Ma", "2Ma", "2Maccabees"},
  {"3 Maccabees", "3 Macc", nil, "3Macc", "3 Mac", "3Mac", "3 Ma", "3Ma", "3Maccabees"},
  {"4 Maccabees", "4 Macc", nil, "4Macc", "4 Mac", "4Mac", "4 Ma", "4Ma", "4Maccabees"},
  {"Sirach", "Sir"},
  {"Tobit", "Tob", nil, "Tb"},
  {"Wisdom", "Wis", nil, "Ws"}
}

function normalizeBookName(book, idx)
  if idx > 2 then
    error("Cannot normalize a Bible book to an index greater than 2.")
  end

  for _, list in pairs(bible_books) do
    for _, bk in pairs(list) do
      if bk == book then
        suff = ""
        if list[1] ~= list[2] then
          suff = "."
        end
        return list[idx]..suff
      end
    end
  end

  error("Could not normalize book name: \""..book.."\"")
end

function processBibleCitation(suffix, translation)
  local suffix = strip(suffix)
  if suffix:sub(1,1) == "," then
    suffix = suffix:sub(2)
    suffix = strip(suffix)
  end
  local book = ""
  local range = ""

  for tok in string.gmatch(suffix, "[^%s]+") do
    if #book == 0 then
      book = tok
    elseif #range > 0 then
      range = range.." "..tok
    else
      if tonumber(tok:sub(1,1)) ~= nil then
        range = tok
      else
        book = book.." "..tok
      end
    end
  end
  book = normalizeBookName(strip(book), 2)
  range = strip(range)

  return book.." "..range
end

local bible_translations = {}

function filterCiteElementForBiblicalRefs(elem)
  local translations = {}
  local bible_cites = {}
  local other_count = 0
  for _, citation in pairs(elem.citations) do
    if starts_with(citation.id, "Bible-") then
      local translation = citation.id:sub(#"Bible-"+1)
      translations[translation] = 1
      local bcite = processBibleCitation(pandoc.utils.stringify(citation.suffix), translation)
      table.insert(bible_cites, bcite)
    else
      other_count = other_count + 1
    end
  end
  local translation_list = {}
  for t, _ in pairs(translations) do table.insert(translation_list, t) end
  if #translation_list > 1 then
    error("Cannot mix translations in a single citation. ("..table.concat(translation_list, " + ")..")")
  end

  if #bible_cites > 0 and other_count > 0 then
    error("Cannot mix Bible citations with other types.")
  end

  if other_count > 0 then
    return nil
  end

  local translation = translation_list[1]
  local cite = {}
  table.insert(cite, pandoc.Str("("))
  for i,c in pairs(bible_cites) do
    table.insert(cite, pandoc.Str(c))
    if i < #bible_cites then
      table.insert(cite, pandoc.Str(";"))
      table.insert(cite, pandoc.Space())
    end
  end
  table.insert(cite, pandoc.Span({pandoc.Space(), pandoc.Emph(pandoc.Str(translation))}, {class="bible-translation-cite"}))
  table.insert(cite, pandoc.Str(")"))

  bible_translations[translation] = true

  return cite
end

function filterSpanElementsForTranslationReference(elem)
  if is_string_in_list("bible-translation-cite", elem.classes) then
    -- if using more than one translation, name it every time
    if count_table_entries(bible_translations) > 1 then
      return nil
    end
    -- otherwise, only name it the first time
    local tkey = strip(pandoc.utils.stringify(elem))
    if bible_translations[tkey] == true then
      bible_translations[tkey] = false
      return nil
    else
      return {}
    end
  end
end

-- Two passes: one to make the citations, the other to clean up excess translation mentions.
return {
  { Cite = filterCiteElementForBiblicalRefs },
  { Span = filterSpanElementsForTranslationReference },
}
