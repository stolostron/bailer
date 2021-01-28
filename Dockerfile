FROM registry.access.redhat.com/ubi8/ubi:latest
WORKDIR /
COPY . .
RUN curl -L https://github.com/openshift/okd/releases/download/4.6.0-0.okd-2021-01-17-185703/openshift-client-linux-4.6.0-0.okd-2021-01-17-185703.tar.gz | tar -xz
RUN cp ./oc /usr/local/bin/.
RUN yum install -y python3
RUN yum install jq -y
CMD ./oc-wrapper.sh $username $password $URL $tag