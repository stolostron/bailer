

The spot the different process requires 3 steps to complete the comparison. Run "memory-scanner" on a cluster in the initial state. 
Then after making changes to the cluster run "memory-scanner" again.
Finally, run "spot-the-difference" to complete the comparison.

To run "memory-scanner" use the below docker command replacing variables as necessary:

```
docker run -v <results output location>:/results <docker image name> scan <openshift cluster username> '<openshift cluster password' '<openshift cluster URL>' '<unique reference tag>'
```

To run "spot-the-difference" use the below docker command replacing variables as necessary:

```
docker run -v <results output location>:/results < diff <initial file location> <secondary file location> <unique reference tag>
```

In the above, we are using volumes to inject locally stored directories into our container. The <results output location> contents will match those of `/results`
When designating the file locations for the diff run, it is necessary to use their location on the container following this injection