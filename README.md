# doxygen2hugo
# A [Doxygen](https://doxygen.nl/) to [Hugo](https://gohugo.io/) markdown generator

## Background
Wanted an auto-generator for documentation to upload on my website, default Doxygen HTML was far too bloated and barely customisable, so I made this to generate Hugo markdown files from Doxygen XML output, maybe I'll support more languages later on but for me right now it's find just working for C.

## Languages 
| Language | Support |
| -------- | ------- |
| C        | in-progress |
## Usage
Generate XML with Doxygen on your codebase then point doxygen2hugo to the XML directory.

E.g.
```bash
doxygen doxygen.conf ; # -> xml/
doxygen2hugo -o /{path_to_hugo_site}/content/doc/doxygen2hugo/ xml/
```

See `doxygen2hugo -h` for more options.
