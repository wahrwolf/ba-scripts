# Bachelors Thesis - Script Collection
This is a collection of utils and scripts used for my thesis.

# Content:
```
data
├── cleanup		# python module to cleanup text corpora
│   └── plugins
│       └── chars.py	# filter to deal with single chars (like umlaute)
├── cleanup.py		# wrapper script to control the cleanup module
├── config.toml		# config for cleaup.py
└── get_corpora.sh	# script to receive the corpora
```

## get\_corpora.sh
A simple curl script to receive all corpora.
The files are checked and purged after downloading.

## cleanup.py
A modular framework to clean big text corpora using a plugin infrastructure.
The framework was designed for machine learning and can be configured using a TOML file

# Configuration
## cleanup.py
Use the `config.toml` file in the same directory as the script.
You can use the following syntax:
```
# data/config.toml
################################ plugin section ################################
[[modules]]			# can be repeated
name	= "Name you want to use for this plugin"
module	= "the python module to load from (e.g. cleanup.plugins.chars)"
class	= "the class to load"	# has to inheritace Plugin.Filter or Plugin.Fixer
################################ plugin section ################################
...

################################ corpus section ################################
[[corpora]]			# can be repeated
name	= "Name you want to use for this corpus"
base_path = "Path to look for files"
name_pattern = "Pattern to find locale pairs" # Must include at least <pair> and <locale> group
################################ corpus section ################################
...

################################ recipe section ################################
[[recipes]]			# can be repeated
corpus = "Name of the corpus to use	# must be listed in corpora

[[ recipes.steps]]			# can be repeated
name	= "Human readable name for the step"
plugin	= "Name of the plugin to use"	# must be listed in modules
params 	= {}				# params for the plugin
locales = {}				# dict with inlcuded locales
action	= "Action on match"		# Can be one of:
					# [count, edit, fix, report]
					# default is count
################################ recipe section ################################
...
```
On top of that you can configure the output and some runtime options:
```
# data/config.toml
...
################################ logger section ################################
[logger]
# see [python docs](https://docs.python.org/3.7/howto/logging.html#logging-advanced-tutorial) for full docs
# defaults are loaded form cleanup.default

## Examples options:

# override logging level:
root.level = "DEBUG"

# override logging output:
formatters.brief.format= '[%(module)-7s@%(lineno).3d]: %(levelname)-6s %(message)s'
################################ logger section ################################
...

################################ options section ################################
[options]
editor.path	= "Set your favorite editor"	# defaults to $EDITOR or vi if not set
keep_source	= True|False			# keep original source files?
keep_steps	= True|False			# keep file output for each filter?
keep_unaligned	= True|False			# keep unaligned files?
max_process	= "For use in Filters"		# defaults to os.cpu_count
mode		= "batch" or _			# set to batch to run all recipes
target_dir	= "The output directory"	# create temp if nothing specified
first_line	= 0|1				# Offset for displaying line numbers
################################ options section ################################
...
```

### cleanup plugins:
List of available plugins for the data cleanup module

#### Char
This plugin searches for single chars and replaces them using a dict
params:
- `chars`	: list of chars to lookup for
- `replace_dict`: dict for replacement
