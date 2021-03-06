# DataPages
Static pages with convenient links to WTSI's pathogen sequencing data

## Scripts

This repo creates the following scripts which can be used to build static content directing users to WTSI's pathogen
datasets. 

* `datapages_update_projects`
* `datapages_update_nctc` (still under development)

This code needs priviledged access to some of our databases so it cannot be run outside Sanger.  In addition
some of the styling and javascript is inherited from the [Sanger website](https://www.sanger.ac.uk) so it isn't
a great idea to try running it locally. Instead, ask the web team to setup a sandbox for you and check your changes
there.

### `datapages_update_projects`

This script uses / abuses the word 'domain' to mean a collection of species as detailed in a configuration file
(e.g. [helminths.yml](pages_config/helminths.yml).

For each domain configuration file, it creates a new directory using the name taken from the config.  In this directory
it creates a `data` folder and an `index.html` page which is based on the [index.html](templates/index.html) template.

In effect, each domain gets it's own single page microsite.  On this page, users can select a species and can further
filter by project name.  When a different species is selected, javascript in the page fetches data in JSON format from
the relevant `/data` folder and renders it using [DataTables](http://datatables.net/).  It also updates other content
(fetched in the same query) including things like a species description and links to other resources.

Data for these pages is merged from a number of private and public sources:
* VRTrack database (mostly species name => project mapping and public accession ids)
* Sequencescape (public names for things like strain and sample name)
* ENA (to check if the run, project, sample is actually still available for download; if not it isn't displayed)
* Local config (metadata like database names, descriptive text, etc. see [pages_config](pages_config) for examples)
* Environment variables / `--global-config` (more sensitive details like database server names and user credentials)

#### Commandline options

```
$ datapages_update_projects -h
usage: datapages_update_projects [-h] [--global-config GLOBAL_CONFIG] [-q]
                                 [-d SITE_DIRECTORY] [--save-cache SAVE_CACHE]
                                 [--load-cache LOAD_CACHE] [--html-only]
                                 domain_config [domain_config ...]

positional arguments:
  domain_config         One or more domain config files (e.g. viruses.yml)

optional arguments:
  -h, --help            show this help message and exit
  --global-config GLOBAL_CONFIG
                        Overide config (e.g. database hosts, users)
  -q, --quiet           Only output warnings and errors
  -d SITE_DIRECTORY, --site-directory SITE_DIRECTORY
                        Directory to update
  --save-cache SAVE_CACHE
                        Cache database results to this file
  --load-cache LOAD_CACHE
                        Load cached database results from this file
  --html-only           Don't update data, just html
```

The script needs to know the values for the following:
* `DATAPAGES_VRTRACK_HOST`
* `DATAPAGES_VRTRACK_PORT`
* `DATAPAGES_VRTRACK_RO_USER`
* `DATAPAGES_SEQUENCESCAPE_HOST`
* `DATAPAGES_SEQUENCESCAPE_PORT`
* `DATAPAGES_SEQUENCESCAPE_DATABASE`
* `DATAPAGES_SEQUENCESCAPE_RO_USER`

It can also optionally be provided with:
* `DATAPAGES_SITE_DATA_DIR`
* `DATAPAGES_LOAD_CACHE_PATH`
* `DATAPAGES_SAVE_CACHE_PATH`

By default these will be loaded from environment variables.  You can also pass them in a YAML formatted config file as follow:
```
---
DATAPAGES_VRTRACK_HOST: 1.2.3.4
DATAPAGES_VRTRACK_PORT: 8888
DATAPAGES_VRTRACK_RO_USER: bob
DATAPAGES_SEQUENCESCAPE_HOST: 5.6.7.8
DATAPAGES_SEQUENCESCAPE_PORT: 9999
DATAPAGES_SEQUENCESCAPE_DATABASE: foo
DATAPAGES_SEQUENCESCAPE_RO_USER: bill
DATAPAGES_SITE_DATA_DIR: /www-data/pathogen_data_site
```

You can pass in such a file using the `--global-config` argument otherwise it will look for `.datapages_global_config.yml`
in the user's home directory.  Environment variables take priority and it is possible to provide some values with environment
variables and others through config.

The `-d` option specifies the directory in which to place the new pages (e.g. `/helminths`).  It overides the `DATAPAGES_SITE_DATA_DIR` variable specified above.  If neither is provided, it creates a new `/site` directory
in the current directory and adds the data there.

`--save-cache` and `--load-cache` are useful for debugging.  At an early stage, before most data processing is done, you
can save a cache of the data collected from the various sources.  This means that you can load it from disk rather than
making lots of database or web requests.  It makes development a lot less painful but you probably don't want to use
`--load-cache` in production.

`--html-only` is another development flag.  In this case it doesn't make any updates to the relevant `/data` folders and
just updates the `index.html` output.  This is much, much faster if you're just making small changes to styling or layout.

#### Domain config

`domain_config` is one or more configuration files for a group of species which I've collectivly called a 'domain' for want of
a better word.  These files are yaml formatted, a good example is the [virus config](page_config/viruses.yml).

We start with a list of VRTrack `databases` to query for this domain.  Then we provide `metadata` including the following:

* `type` must be domain for now
* `description` is a markdown formatted description of the domain which appears at the top of each page
* `list_data` this can be used to temporarily disable all data tables for this domain
* `title` to appear at the top of all pages for this domain
* `name` used to name the folder the data is put into (and therefore the URL it will be found on).  This is also used by `--save-cache`

After that comes the data for each `species`.  This includes the following:

* The name of the species (N.B. this is used in a case insensitive search to find all species which _start with_ this name; e.g. the page for 'Staphylococcus' also includes lists of the data for Staphylococcus aureus)
* `description` is a markdown formatted description for this species.  Tables are supported but some features may be missing.
* `published_data_description` is like `description` but appears after the table of data
* `aliases` is a list of pseudonyms for this species; species begining with these aliases are also included in the data presented on this page
* `links` is a list of links to appear on the right hand side of the page
* `pubmed_ids` is a list of pubmed ids for relevant publications which are rendered into useful citations in the final page
* `show` defaults to true; when set to false it temporarily hides that species and removes the relevant JSON from `/data`

### `datapages_update_projects`

A work in progress, more to follow here.

## Installation

This uses python3; all python dependencies are installed as follows:

```
pip3 install git+https://github.com/sanger-pathogens/DataPages.git
```

You can also install the scripts in a virtualenv which has the advantage of keeping dependencies isolated:

```
virtualenv venv -p $(which python3)
. venv/bin/activate
pip install git+https://github.com/sanger-pathogens/DataPages.git
deactivate
```

You can then call the script without sourcing the virtualenv (e.g. in your cron job)

```
${PATH_TO_VENV}/venv/bin/datapages_update_projects --help
```

You store your own config anywhere but it makes more sense to also clone this repo and use it to version config in the
[pages_config](pages_config) folder.

You probably also want to create a file like `.datapages_global_config.yml` rather than relying on environment variables
if this is going to be triggered by a cron job.

## Further work

Some pages are really quite slow to load (e.g. Salmonella); I've included some thoughts on how we could give users the 
appearance that this is not the case.  You can find this in the [update_table_for_species function](site/assets/js/datapages.js).
