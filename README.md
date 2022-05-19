# Paper

A little tool for generating and managing academic papers. Focused on [Chicago Manual of Style citations](https://www.chicagomanualofstyle.org/tools_citationguide.html) and the [paper submission standards of the BC STM](https://libguides.bc.edu/academicpapers_stm/).

## Installation
```shell
pip install git+https://github.com/sjml/paper.git
```
or

```shell
git clone git+https://github.com/sjml/paper.git
cd paper
pip install -e .
```

## Commands
* `paper new`: generates a new scaffold directory
* `paper init`: sets up the directory you're in as the scaffold, so long as it's empty
* `paper reinit`: recalculates the metadata and replaces the `./resources` directory, but does not touch the content or any other files
* `paper build`: builds a Word document and PDF version of the paper
* `paper wc`: outputs word count information, broken down by file
* `paper save`: modifies the metrics in the readme (word count, progress towards goal) and makes a git commit, prompting for a message and appending some extra data to it
* `paper push`: if you've already set up an upstream repository, pushes to it. if not, will make a GitHub repo, prompting for a name (recommended template based on metadata), private v public, etc. 

## `paper_meta.yml`
The metadata file that assists in the generation. YAML format. `paper` will walk up the directory tree until the root looking for similarly named files, so you can have a root `paper_meta.yml` with the author name, one in a directory for each class with the professor and mnemonic, etc. (Note this is only traversed when the project is set up; it doesn't automatically pick up changes live, but writes the full coalesced data to the lowest file in the hierarchy at init time.)

* `data`: 
    * (These items are moved under this `data` heading because otherwise pandoc will try to print a title block. Could this all be better organized? Probably.)
    * `date`: due date in ISO-8601 format OR `null` OR placeholder `"[DATE]"` (if set, will be graphed as a red line on the progress image)
    * `author`: author's name
    * `title`: title of paper
* `class_mnemonic`: like "PHIL 101" or whatever
* `class_name`: like "Introduction to Philosophy" or whatever
* `professor`: the person what teaches the class
* `target_word_count`: if not null, will be graphed as a green line on the progress image
* `sources`: An array of paths to BibTeX (`.bib`) files that contain citation data exported from Zotero, for example. If present and non-empty, [`pandoc` will be given these files in an effort to process citations](https://pandoc.org/MANUAL.html#citations).

## `./content` folder
Any file in this folder that ends with `.md` will be given to pandoc for assembly into the final paper. Note that they're given in alphabetical order, and should be Markdown files. At the moment, no metadata in them is processed. 

## Metrics
On top of doing the document generation, assuming you use `paper save` to commit your work, it also generates progress reports like the below, based on git commits. (This example shows good consistent progress towards a ~50,000 word thesis. The green line is target word count; the red line is the due date.)

<!-- begin paper metadata -->
### Example progress metrics
| File                    | Word Count |
| ----------------------- | ---------- |
| 00_intro.md             | 2838       |
| 01_initial_problem.md   | 9782       |
| 02_literature_review.md | 6465       |
| 03_experiment_design.md | 18254      |
| 04_analysis.md          | 10075      |
| 05_next_steps.md        | 2483       |
| 06_conclusion.md        | 2162       |
| **TOTAL**               | 52059      |

![WordCountProgress](./docs/fake_progress.svg)
<!-- end paper metadata -->

## Notes
Assumes: 
* you have git set up
* you have [gh](https://cli.github.com/) installed
* you have [pandoc](https://pandoc.org/) installed
* you are logged in to a GitHub account
* you have Microsoft Word installed
* you are running on a Mac (uses AppleScript to turn docx to pdf)
* you are not doing any zany branching stuff with your repo
    - should still work, but who knows? I tend to not branch on non-collaborative projects, so not a use case I've looked at a ton
* your content folder is flat; not set up to handle nested structures
* you are not malicious; input is not sanitized or anything
* you are not afraid of error messages; it happily crashes on exceptions

"Why generate a docx file first instead of going direct to PDF, since pandoc could do that?" 
Because some professors insist you submit Word documents, so I'd have to be ready to 
generate them anyway, and no need to write the logic twice. 
