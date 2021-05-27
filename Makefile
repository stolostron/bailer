cluster-scan:
	./memory-scanner.sh ${TAG}

cluster-diff:
	python3 ./spot-the-difference-spicy.py -f ${FIRST_FILE} -s ${SECOND_FILE} -o ${OUTPUT_TAG}