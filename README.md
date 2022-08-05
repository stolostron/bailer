# Bailer

Bailer records and compares a cluster at different states to detect leaks.

This process requires the following steps:

(0) Build the Bailer Docker image with `make docker-build`.
(1) Run "scan" on a cluster to record the initial state.
(2) Make any desired changes to your cluster.
(3) Run "scan" on the cluster to record the secondary state.
(4) Run "diff" to compare the cluster's inital and secondary state.



## `scan`

To run `scan`, export the following environment variables (substituting the correct values for your use case) ...

```bash
// pre-built bailer image
export IMAGE_REF="bailer:0.0.1"

// full path to dir where scan files will be written
export SCAN_DIR_PATH="/Users/nweather/Desktop/downstream-setup/scans"

// cluster api url
export API_URL="https://api.installer-pool-4c7rb.dev01.red-chesterfield.com:6443"

// cluster kubeadmin password
export KUBEADMIN_PASS="LOLNOTTELLINGYOU"

// arbitrary suffix for scan files
export SCAN_TAG="01-clean-state"

```

... then run the following docker command as-is:

```bash
docker run -v $SCAN_DIR_PATH:/results $IMAGE_REF scan kubeadmin $KUBEADMIN_PASS $API_URL $SCAN_TAG
```

The scan files will be written into `$SCAN_DIR_PATH`.

## `diff`

To run `diff`, export the following environment variables (substituting the correct values for your use case) ...

```bash

// pre-built bailer image
export IMAGE_REF="bailer:0.0.1"

// full path to dir with scan files
export SCAN_DIR_PATH="/Users/nweather/git/bailer-files/nweather-june-2-001-acm-2.2.3"

// first file name as it exists in SCAN_DIR_PATH
export INIT_FILE_NAME="scan-01-clean.jsonl"

// second file as it exists in SCAN_DIR_PATH
export SECOND_FILE_NAME="scan-05-operator-uninstall.jsonl"

// arbitrary suffix for diff files
export DIFF_TAG="june-2-001-scan-1-to-5"

```

... then run the following docker command as-is:

```bash

docker run -v $SCAN_DIR_PATH:/results $IMAGE_REF diff /results/$INIT_FILE_NAME /results/$SECOND_FILE_NAME $DIFF_TAG

```

The diff files will be written into `$SCAN_DIR_PATH`.

