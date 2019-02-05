#!/bin/bash
#baseurl='http://opus.nlpl.eu/download.php?f='
baseurl='https://wolfpit.net/share/archive/opus/'

locales='cs,da,de,en,ja'
corpora='ECB/v1,EMEA/v3,News-Commentary/v11,Europarl/v7,OpenSubtitles/v2018,Ubuntu/v14.10'

full_url="${baseurl}{${corpora}}/{tmx,moses}/{${locales}}-{${locales}}.{tmx.gz,txt.zip}"

# Download all textcorpora
curl 			\
	--location	\
	--create-dir	\
	--output '#1/#2/#3-#4.#5' "$full_url"

# Filter out all empty files
find . -name '*.tmx.gz' -size -2k -exec rm '{}' ';'

# Unzip all files
find . -name '*.tmx.gz' -exec gunzip --verbose '{}' '+'
