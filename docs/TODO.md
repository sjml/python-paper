* maybe some code cleanup? (cli.py is a smidge overpacked)
* `paper_meta.yml` could also be re-orged (maybe all paper data goes under one section and system data loose or under another?)
* could imagine passing it a param for what kind of output file to generate, maybe something in the metadata file? 
    - `docx` vs `pdf` vs `docx+pdf` (a PDF from Word instead of via LaTeX), for example
* project template:
    - should "resources" become ".paper_resources"? hidden from the user, maybe
    - make other folders for notes/filters/resources/research/etc? -- basically a little project scaffold for academic work
* list rendering is a bit off -- I don't use it much/at all, but let's figure out for the sake of completion

* custom CSL or more filters? 
    - catholic primary sources:
        - CCC -- no author, use CCC on subsequent cites
        - USCCB -- use abbreviation on subsequent cites
        - Aquinas -- drop author on subsequent, keep translator notes
        - Conciliar documents: lose quotes on actual name? (and short)
        - Encyclicals: lose quotes on actual name? (and short)
        - overall: use § instead of "sec."
            - probably easiest as a post-hoc filter
    - latin sources:
        - seems mostly the same, but Vulgate is special-cased bible
    
    * note that pandoc.utils.references is pulled from the csl?


make encyclical collection
make vatican 2 collection (as elements of the published book)
make aquinas entry
