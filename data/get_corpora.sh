#!/bin/bash
baseurl='http://opus.nlpl.eu/download.php'

locales='cs,da,de,en,ja'
corpora='EMEA/v3,News-Commentary/v11,Europarl/v7,OpenSubtitles/v2018,Ubuntu/v14.10'

full_url="${baseurl}?f={${corpora}}/tmx/{${locales}}-{${locales}}.tmx.gz"

# Download all textcorpora
curl 			\
	--location	\
	--create-dir	\
	--output '#1/#2-#3.tmx.gz' "$full_url"

# Filter out all empty files
find . -name '*.tmx.gz' -size -2k -exec rm '{}' ';'

# Unzip all files
find . -name '*.tmx.gz' -exec gunzip --verbose '{}' '+'
