# Setup

- linger
- create tempfile /tmp/4dahmen/run/
- install pipenv+pyenv nach /tmp/4dahmen/
- load pipfile in /data/4dahmen/$corpus/
- create virtualenv
- run preprocess with pipenv
- run train with pipenv
- export models to wolfpit
- notify via sms?
- stop linger

# preprocess
- figure out where the data comes from
- and goes to

- figure out how to merge bootstrap and install
- integrate a recipe repo where all the config lies in..

# visual aid
sequenceDiagram
	participant bootstrap.sh
	participant get-corpora.sh
	participant install.sh
	participant workdir
	participant datadir

	bootstrap.sh->>datadir: clone script-repo
	bootstrap.sh->>datadir: install systemd-units
	bootstrap.sh->>datadir: install tmpfiles

	bootstrap.sh-->>+install.sh: start install.sh

	loop If script-repo does not exist
		install.sh->>datadir: install script-repo
	end
	install.sh->>datadir: update script-repo

	install.sh->>workdir: install pip
	install.sh->>workdir: install pipenv

	loop If onmt does not exist
		install.sh->>workdir: download onmt
	end
	install.sh->>workdir: install onmt

	get-corpora.sh->>datadir: install corpus data
	datadir->>get-corpora.sh: envsubst config
	get-corpora.sh->>datadir: install corpus config
