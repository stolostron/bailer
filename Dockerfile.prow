FROM registry.access.redhat.com/ubi8/ubi:latest
WORKDIR /
COPY . .
RUN curl -L https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest-4.6/openshift-client-linux.tar.gz | tar -xz
RUN cp ./oc /usr/local/bin/.
RUN yum install -y python3
RUN yum install jq -y
ENTRYPOINT ["./entrypoint-script.sh"]