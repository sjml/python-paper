* maybe some code cleanup? (cli.py is a smidge overpacked)
    - lua naming conventions all over the place, global v local variables, require to variable?
* `paper_meta.yml` could also be re-orged (maybe all paper data goes under one section and system data loose or under another?)
* project template:
    - should "resources" become ".paper_resources"? hidden from the user, maybe
    - make other folders for notes/filters/resources/research/etc? -- basically a little project scaffold for academic work
* list rendering is a bit off -- I don't use it much/at all, but let's figure out for the sake of completion

* custom CSL or more filters? 
    - catholic primary sources:
        - CCC -- no author, use CCC on subsequent cites
            - think it "just works" but test it
        - Encyclicals and conciliar documents: lose quotes on actual name (probably a type/CSL thing?)
            - also set encyclical filters to handle multiple cites
    - latin sources:
        - seems mostly the same, but Vulgate is special-cased bible
    
    * note that pandoc.utils.references is pulled from the csl?


make encyclical collection
make vatican 2 collection (as elements of the published book)
make aquinas summa entry
