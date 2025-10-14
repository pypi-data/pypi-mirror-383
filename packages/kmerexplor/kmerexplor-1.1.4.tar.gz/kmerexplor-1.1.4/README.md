# KmerExploR


- [Description](#description)
- [Installation](#installation)
	+ [Option 1: install with pip](#option-1-install-kmerexplor-with-pip)
	+ [Option 2: install with git](#option-2-install-kmerexplor-with-git-by-cloning-repository)
- [Input](#input)
- [Output](#output)
- [Examples](#examples)
- [Usage](#usage)
- [Options](#options)
	- [-k --keep-counts](#-k---keep-counts)
	- [--tags tags_file](#--tags-tags_file)
	- [--config config.yaml](#config-config.yaml)


## Description


From a bunch of fastq or countTags output files, by default, KmerExploR provides information on Human RNA-sequencing datasets :

- wether the analysis is based on poly-A selection protocol or ribo-depletion,
- whether the analysis is based on oriented or non-oriented sequencing, 
- gender, 
- whether there is a read coverage bias from 5' to 3' 	long transcripts
- wether the data are contamined by HeLa, mycoplasma is present or not, or other viruses such as hepatitis B virus
- specie

Other type of information can be queried, using ``-l/--list`` then ``-b/--builtin-tags``.

`KmerExploR` uses a set of reference specific kmers designed with Kmerator (https://github.com/Transipedia/kmerator).

For general usage, we will use one of the provided sets of tags. Howerver, it is also possible to create your own tags reference file to have specific informations on you samples such as request on a particular specie.

This code is under **GPL3** licence.

### Testing with dataset

You can use the following dataset to test the software and to illustrate the different categories, which contains 5 paired-end human RNA-seq samples:

|            |PolyA/RiboD|HeLa  | Mycoplasma | Stranded | Sex    | fastq1 | fastq2 |
|:-----------|:---------:|:----:|:----------:|:--------:|:------:|:------:| :-----:|
|SRR12010285 | PolyA     | +    |      -     |    yes   | female | [link](https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR120/085/SRR12010285/SRR12010285_1.fastq.gz) | [link](https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR120/085/SRR12010285/SRR12010285_2.fastq.gz) |
|ENCFF322RPT | PolyA     | -    |      +     |    yes   | male   | [link](https://www.encodeproject.org/files/ENCFF322RPT/@@download/ENCFF322RPT.fastq.gz) | [link](https://www.encodeproject.org/files/ENCFF782AHJ/@@download/ENCFF782AHJ.fastq.gz) |
|ENCFF001RMX | RiboD     | -    |      -     |    yes   | female | [link](https://www.encodeproject.org/files/ENCFF001RMX/@@download/ENCFF001RMX.fastq.gz) | [link](https://www.encodeproject.org/files/ENCFF001RMW/@@download/ENCFF001RMW.fastq.gz) |
|SRR1957703  | PolyA     | -    |      -     |    yes   |   NA   | [link](https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR195/003/SRR1957703/SRR1957703_1.fastq.gz) | [link](https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR195/003/SRR1957703/SRR1957703_2.fastq.gz) |
|SRR1957706  | PolyA     | -    |      -     |    no    |   NA   | [link](https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR195/006/SRR1957706/SRR1957706_1.fastq.gz) | [link](https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR195/006/SRR1957706/SRR1957706_2.fastq.gz) |



## Installation

`KmerExploR` needs `yaml` and `markdown` python module,
We recommand tu use ``pip` as it install everything you need automatically.

### Option 1: install KmerExploR with pip

```
pip install kmerexplor
```

**Nota**: make sure your PATH variable include `~/.local/bin`.


### Option 2: install KmerExploR with git by cloning repository

```
# clone the repository
git clone https://github.com/Transipedia/kmerexplor.git

# create link somewhere in your PATH
sudo ln -s $PWD/kmerexplor/kmerexplor/core.py /usr/local/bin/kmerexplor
```


## Input


**Required:**

- fastq or outputs from countTags (gzipped or not). 

For paired samples, fastq names must be in illumina format (`_R1_001` and `_R2_001`), otherwise they must end by `_1.fastq[.gz]` and `_2.fastq[.gz]` or `_R1.fastq[.gz]` and `_R2.fastq[.gz]`. `countTags` files must end by `tsv[.gz]`. `countTags` files can be aggregated in a single multi-culumn file.

**For advanced usage:**

- tags file
- yaml configuration file
- markdown file (facultative)

Both yaml and tags file must match (see below).


## Output

By default, outputs are produced in directory `kmerexplor-results`.

- `table.tsv` : tab separated table of results.
- `kmerexplor.html` : graphical results.
- `lib` directory contains css and javascript code associated with `kmerexplor.html`.
- if `--keep-counts` option is specified `countTags` directory contains __countTags__ output. 

```
kmerexplor-results
├── countTags			# with '--keep' option
├── kmerTool.html
├── lib
│   ├── echarts-en.min.js
│   ├── scripts.js
│   └── styles.css
└── table.tsv
```


## Usage

Without options or with `--help`, `KmerExploR` returns Help

```
usage: kmerexplor [-h] [-s] [-p] [-k <int>] [-K] [-d] [-b BUILTIN_TAGS] [-o <output_dir>] [--tmp-dir <tmp_dir>] [-C <file_name>] [-T <tag_file>] [-l]
                      [--dump-config file_name] [--show-tags] [--title <string>] [-y] [-c <int>] [-v]
                      [<file1> ... ...]

positional arguments:
  <file1> ...           fastq or fastq.gz or tsv countTags output files.

optional arguments:
  -h, --help            show this help message and exit
  -s, --single          when samples are single.
  -p, --paired          when samples are paired.
  -k <int>, --kmer-size <int>
                        kmer size (default 31).
  -K, --keep-counts     keep countTags outputs.
  -d, --debug           debug.
  -b BUILTIN_TAGS, --builtin-tags BUILTIN_TAGS
                        Choose a kmer set between ['human-quality'] (default: human-quality)
  -o <output_dir>, --output <output_dir>
                        output directory (default: "./kmerexplor-results").
  -l, --list-tagsets    List available kmer sets
  --tmp-dir <tmp_dir>   temporary files directory.
  --title <string>      title to be displayed in the html page.
  -y, --yes, --assume-yes
                        assume yes to all prompt answers.
  -c <int>, --cores <int>
                        specify the number of files which can be processed simultaneously by countTags. (default: 1). Valid when inputs are fastq files.
  -v, --version         show program's version number and exit

advanced features:
  -C <file_name>, --config <file_name>
                        alternate config yaml file. Used with '--tags' option
  -T <tag_file>, --tags <tag_file>
                        alternate tag file. Could be fasta or tsv file (gzip or not). 
                        Needs '--config' option

extra features:
  --dump-config file_name
                        dump builtin config file as specified name as yaml format and exit.
  --show-tags           print builtin categories and predictors and exit.

```

## Options

### -k --keep-counts

By default, `KmerExploR` deletes intermediate files, particularly countTags output (when input files are fastq files). You could keep countTags output files by using `-K/--keep-counts`option. The location of the countTags output files will then be displayed on the standard output.

countTags outputs are located in a directory named `countTags`, located in `kmerexplor-results` by default or specified by `-o` option.

If you want to run again KmerExploR with the same input dataset, you can directly use  this directory (`kmerexplor-results/countTags/*.tsv`). CountTags step will be bypassed which is saving a lot of time.

### -b/--builtin-tags

By default, the human-quality tag set is applied, alternatively, you can choose other.
To help, ``-l/--list-tagsets`` displayed available tag sets.

### -T/--tags tags_file (advanced usage)

KmerExploR uses an internal default tag file. You can specify your own tags file using `-T/--tags` option with an alternate tags file (compressed or not). It could be formated as tabuled (tsv) or fasta format


#### how the tag file should be formatted ?

Example using a tsv file :

```
AACGCCGCGCGTGACAACAAGAAGACCAGGA Histone-H2AFJ-unused
```

Example using a fasta file

```
>Histone-H2AFJ-unused
AACGCCGCGCGTGACAACAAGAAGACCAGGA
```
where:

- `AACGCCGCGCGTGACAACAAGAAGACCAGGA` : kmer
- `Histone` : category
- `H2AFJ` : seq_id
- `unused` : for convenience, but not used by KmerExploR (facultative)


__Warning__ : `seq_id` must be enclosed by dashes.

__Warning__ : `config.yaml` file must refer to the same categories than tags file, otherwise KmerExploR does not display results (`Histone` in the example).

**Notice** : the description of a set of tags can can be displayed on the main home page by creating a markdown file with the same name, but suffixed with ``.md`` (eg: my-tags.tsv -> my-tags.md).


### -C/--config config.yaml

Associated to the tags file, KmerExploR includes a configuration file. It is used to reference kmers by categories (ex: Orientation, Mycoplasma) and display some parameters for graphs. It is strongly linked to the tags file. 
When you set your own tag file, you also have to specify you own matching config file.
 
 Example for one categorie : 
 

```
Basic_features:   # Meta category, show in left sidenav (underscores are replaced by blank)
  Histone:        # Must match with first item (characters before first dash) of the second column
                  # in the tabuled tags file. Also, they will be used for Javascript function names.
                  # They must be unique, and contain uniquely letters, digits and underscores
    sidenav : Poly A / Ribo D
                  # Show in the left sidebar
    title: Poly A and Ribo depletion by Histone detection
                  # Title of the graph, in the main page.
    threshold: 350
                  # Leave blank if threshold is not needed.
                  # More than one threshold possible by adding multiple values separated by coma (ex: 350,450).
    chart_type: bar
                  # Only bar is admitted at this time.
    chart_theme: light
                  # light, dark, or nothing
    desc:         # More details on the graph, located under it
      - Short description of Poly A and Ribodepletion (show as title)
      - A paragraph of explanations.
      - Another paragraph.
```

Using an alternative tag file, you probably have to redefine the `config.yaml` file, `--config` option specifies the location of an alternative yaml configuration file.


__Nota:__ if you add `as_percent:` to a category (empty or not), results will be in percentage (take a look at `Read biases` results).



## Some Examples:

Mandatory: `-p` for paired-end or `-s` for single:

```
kmerexplor -p path/to/*.fastq.gz
```
 
`-c` for multithreading, `-K` to keep counts (input must be fastq):

``` 
kmerexplor -p -c 16 -K path/to/*.fastq.gz
```

You can skip the counting step thanks to countTags output (see `-K` option):

```
kmerexplor -p path/to/countTags/files/*.tsv
```

`-o` to choose your directory output (directory will be created),  
`--title` to show title in results:

```
kmerexplor -p -o output_dir --title 'Title in html page dir/*.fastq.gz'
```

Use an alternative tagset:

```
# display available tagsets
kmerexplor --list-tagsets
# run kmerexplor with alternative builtin tagset
kmerexplor -p  path/to/*.fastq.gz -b mouse-quality
```

Advanced: using your own tag file and associated config.yaml file:

```
kmerexplor -p --tags my_tags.tsv --config my_config.yaml dir/*.fast.gz
```

