#.SILENT:
SHELL = /bin/bash

plugin_name := complex_rest_dtcd_workspaces
build_dir := make_build
plugin_dir := dtcd_workspaces
plugin_build_dir := $(build_dir)/dtcd_workspaces
requirements_file := requirements.txt


all:
	echo -e "Required section:\n\
 build - build project into build directory, with configuration file and environment\n\
 clean - clean all addition file, build directory and output archive file\n\
 test - run all tests\n\
 pack - make output archive, file name format \"$(plugin_name)_vX.Y.Z_BRANCHNAME.tar.gz\"\n\
Addition section:\n\
 venv\n\
"

GENERATE_VERSION = $(shell cat setup.py | grep __version__ | head -n 1 | sed -re 's/[^"]+//' | sed -re 's/"//g' )
GENERATE_BRANCH = $(shell git name-rev $$(git rev-parse HEAD) | cut -d\  -f2 | cut -d ^ -f1 | sed -re 's/^(remotes\/)?origin\///' | tr '/' '_')
SET_VERSION = $(eval VERSION=$(GENERATE_VERSION))
SET_BRANCH = $(eval BRANCH=$(GENERATE_BRANCH))

define clean_docker_containers
	@echo "Stopping and removing docker containers"
	docker-compose -f docker-compose-test.yml stop
	if [[ $$(docker ps -aq -f name=dtcd_workspaces) ]]; then docker rm $$(docker ps -aq -f name=dtcd_workspaces);  fi;
endef

pack: make_build
	$(SET_VERSION)
	$(SET_BRANCH)
	rm -f $(plugin_name)-*.tar.gz
	cd $(build_dir); tar czf ../$(plugin_name)-$(VERSION)-$(BRANCH).tar.gz $(plugin_dir) --transform "s/^complex_rest_//"

clean_pack: clean_build
	rm -f $(plugin_name)-*.tar.gz

complex_rest_dtcd_workspaces.tar.gz: build
	cd $(build_dir); tar czf ../$(plugin_name).tar.gz $(plugin_dir) --transform "s/^complex_rest_//" && rm -rf ../$(build_dir)

build: make_build

make_build: venv.tar.gz
	mkdir $(build_dir)
	cp -r $(plugin_dir) $(build_dir)

	# copy configuration files
	cp docs/dtcd_workspaces.conf.example $(plugin_build_dir)/dtcd_workspaces.conf.example

	cp *.md $(plugin_build_dir)
	cp *.py $(plugin_build_dir)
#	scripts
	cp -u docs/scripts/*.sh $(plugin_build_dir)
	chmod 755 $(plugin_build_dir)/*.sh

	# virtual environment
	mkdir $(plugin_build_dir)/venv
	tar -xzf ./venv.tar.gz -C $(plugin_build_dir)/venv

clean_build: clean_venv
	rm -rf $(build_dir)

venv:
	conda create --copy -p ./venv -y
	conda install -p ./venv python==3.9.7 -y
	./venv/bin/pip install --no-input -r $(requirements_file)

venv.tar.gz: venv
	conda pack -p ./venv -o ./venv.tar.gz

clean_venv:
	rm -rf venv
	rm -f ./venv.tar.gz

clean: clean_build clean_venv clean_pack clean_test

test: docker_test

logs:
	mkdir -p ./logs

docker_test: logs
	$(call clean_docker_containers)
	@echo "Testing..."
	CURRENT_UID=$$(id -u):$$(id -g) docker-compose -f docker-compose-test.yml run --rm  complex_rest python ./complex_rest/manage.py test ./tests --settings=core.settings.test --no-input -k test_create_directory
	$(call clean_docker_containers)

clean_docker_test:
	$(call clean_docker_containers)

clean_test: clean_docker_test
	@echo "Clean tests"