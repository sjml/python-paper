- could we do the doc munging with lua filters instead?
    - see if the pandoc list responds
        - https://groups.google.com/g/pandoc-discuss/c/aj9Ov_4eEU4

default vs code tasks for scaffolding template? 

can't get margins below tables due to limitations in how word table styles work 😕
    - would work with a post-process by adding this bit of XML to each table definition to make it floating, but with "infinite" margins to the left and right... dubious, but recording here until/unless a better idea comes along
    - `<w:tblpPr w:leftFromText="31680" w:rightFromText="31680" w:bottomFromText="240" w:vertAnchor="text" w:tblpXSpec="center" w:tblpY="1"/><w:tblOverlap w:val="never"/>`
