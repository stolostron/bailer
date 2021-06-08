docker-build:
	docker build . -t bailer:0.0.1

cluster-scan:
	./memory-scanner.sh ${TAG}

cluster-diff:
	python3 ./spot-the-difference.py -f ${FIRST_FILE} -s ${SECOND_FILE} -o ${OUTPUT_TAG}