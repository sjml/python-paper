# Paper

A little tool for generating and managing academic papers. Focused on Chicago Style citations and the paper standards of the [BC STM](https://www.bc.edu/bc-web/schools/stm.html).

## installation
```shell
pip install git+https://github.com/sjml/paper.git
```
or

```shell
git clone git+https://github.com/sjml/paper.git
cd paper
pip install -e .
```

## paper_meta.yml
The metadata file that assists in the generation. YAML format. `paper` will walk up the directory tree until the root looking for similarly named files, so you can have a root `paper_meta.yml` with the author name, one in a directory for each class with the professor and mnemonic, etc. (Note this is only traversed when the project is set up; it doesn't automatically pick up changes, but writes it to the lowest file in the hierarchy.)

* `data`: 
    * (These items are moved under this `data` heading because otherwise pandoc will try to print a title block. Could this all be better organized? Probably.)
    * `date`: due date in ISO-8601 format OR null OR placeholder "[DATE]" (if set, will be graphed as a red line on the progress image)
    * `author`: author's name
    * `title`: title of paper
* `class_mnemonic`: like "PHIL 101" or whatever.
* `class_name`: like "Introduction to Philosophy" or whatever
* `professor`: the person to whom the paper is being given
* `target_word_count`: if not null, will be graphed as a green line on the progress image


## Commands
* `paper new`: generates a new scaffold directory
* `paper init`: sets up the directory you're in as the scaffold, so long as it's empty
* `paper build`: builds a Word document and PDF version of the paper
* `paper wc`: outputs word count information, broken down by file
* `paper save`: modifies the metrics in the readme (word count, progress towards goal) and makes a git commit, prompting for a message and appending some extra data to it
* `paper push`: if you've already set up an upstream repository, pushes to it. if not, will make a GitHub repo, prompting for a name (recommended template based on metadata), private v public, etc. 


## Notes
Assumes: 
* you have git set up
* you have [gh](https://cli.github.com/) installed
* you have [pandoc](https://pandoc.org/) installed
* your are logged in to a GitHub account
* you have MS Word installed
* you are running on a Mac (uses AppleScript to turn docx to pdf)
* you are not doing any zany branching stuff with your repo
    - maybe would still work, but who knows?

"Why generate a docx first instead of going direct to PDF, since pandoc could do that?" 
Because some professors insist you submit Word documents, so I'd have to be ready to 
generate them anyway, and no need to write the logic twice. 
