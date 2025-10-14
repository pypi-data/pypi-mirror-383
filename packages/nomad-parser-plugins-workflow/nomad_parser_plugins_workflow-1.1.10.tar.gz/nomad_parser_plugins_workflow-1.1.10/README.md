[![DOI](https://zenodo.org/badge/461070260.svg)](https://zenodo.org/badge/latestdoi/461070260)

This is a collection of the NOMAD parsers for the following workflow codes:

1. [AFLOW](http://www.aflowlib.org/)
2. [ASR](https://asr.readthedocs.io/en/latest/index.html)
3. [Atomate](https://www.atomate.org/)
4. [ElaStic](http://exciting.wikidot.com/elastic)
5. [FHI-vibes](https://vibes.fhi-berlin.mpg.de/)
6. [LOBSTER](http://schmeling.ac.rwth-aachen.de/cohp/)
7. [phonopy](https://phonopy.github.io/phonopy/)
8. [QuantumEspressoEPW](https://www.quantum-espresso.org)
9. [QuantumEspressPhonon](https://www.quantum-espresso.org)
10. [QuantumEspressoXSpectra](https://www.quantum-espresso.org/Doc/INPUT_XSpectra.txt)

## Preparing code input and output file for uploading to NOMAD

An *upload* is basically a directory structure with files. If you have all the files locally
you can just upload everything as a `.zip` or `.tar.gz` file in a single step. While the upload is
in the *staging area* (i.e. before it is published) you can also easily add or remove files in the
directory tree via the web interface. NOMAD will automatically try to choose the right parser
for you files.

For each parser there is one type of file that the respective parser can recognize. We call
these files *mainfiles*. For each mainfile that NOMAD discovers it will create an *entry*
in the database, which users can search, view, and download. NOMAD will consider all files
in the same directory as *auxiliary files* that also are associated with that entry. Parsers
might also read information from these auxillary files. This way you can add more files
to an entry, even if the respective parser/code might not use them. However, we strongly
recommend to not have multiple mainfiles in the same directory. For CMS calculations, we
recommend having a separate directory for each code run.

Go to the [NOMAD upload page](https://nomad-lab.eu/prod/rae/gui/uploads) to upload files
or find instructions about how to upload files from the command line.

## Using the parser

You can use NOMAD's parsers and normalizers locally on your computer. You need to install
NOMAD's pypi package:

```
pip install nomad-lab
```

To parse code input/output from the command line, you can use NOMAD's command line
interface (CLI) and print the processing results output to stdout:

```
nomad parse --show-archive <path-to-file>
```

To parse a file in Python, you can program something like this:
```python
import sys
from nomad.client import parse, normalize_all

# match and run the parser
archives = parse(sys.argv[1])

# Run all normalizers
for archive in archives:
    normalize_all(archive)

    # Get the 'main section' section_run as a metainfo object
    section_run = archive.run[0]

    # Get the same data as JSON serializable Python dict
    python_dict = section_run.m_to_dict()
```

## Developing the parser

Create a virtual environment to install the parser in development mode:

```
pip install virtualenv
virtualenv -p `which python3` .pyenv
source .pyenv/bin/activate
```

Install NOMAD's pypi package:

```
pip install nomad-lab
```

Clone the parser project and install it in development mode:

```
git clone https://github.com/nomad-coe/workflow-parsers.git workflow-parsers
pip install -e workflow-parsers
```

Running the parser now, will use the parser's Python code from the clone project.

## How to cite this work
Ladines, A. N., Daelman, N., Pizarro, J. M., Ondračka, P., Himanen, L., Fekete, A., Scheidgen, M., Chang, T., Ilyas, A., & Rudzinski, J. F. (2025). Workflow Parsers (all versions). Zenodo. https://doi.org/10.5281/zenodo.14900119