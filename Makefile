# GITHUB_USER containing '@' char must be escaped with '%40'
GITHUB_USER := $(shell echo $(GITHUB_USER) | sed 's/@/%40/g')
GITHUB_TOKEN ?=
-include $(shell [ -f ".build-harness-bootstrap" ] || curl --fail -sSL -o .build-harness-bootstrap -H "Authorization: token $(GITHUB_TOKEN)" -H "Accept: application/vnd.github.v3.raw" "https://raw.github.com/open-cluster-management/build-harness-extensions/master/templates/Makefile.build-harness-bootstrap"; echo .build-harness-bootstrap)
-include Makefile.prow



docker-build:
	docker build . -t bailer:0.0.1

cluster-scan:
	./memory-scanner.sh ${TAG}

cluster-diff:
	python3 ./spot-the-difference.py -f ${FIRST_FILE} -s ${SECOND_FILE} -o ${OUTPUT_TAG}

