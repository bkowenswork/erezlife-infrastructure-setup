# Testing Jenkins

Make sure [VirtualBox and Vagrant are
available](../README.md#Provision-with-Vagrant).
New to Vagrant? There’s a [cheatsheet for using Vagrant](../README.md#Cheatsheet).

The virtual machine IP address is fixed to
[192.168.57.2](https://github.com/erezlife/ansible-server-setup/blob/master/jenkins_tests/Vagrantfile#L5).

Add following line to `/etc/hosts`:
```
192.168.57.2 jenkins-test.erezlife.com
```

After the provisioning is complete, navigate to
https://jenkins-test.erezlife.com/. Your password is available under
`~jenkins/users/initial-passwords`.

## Testing a job

In the VM, most jobs are disabled or setup not to run to avoid side-effects on
production.

**Make sure your tests will not affect production.**

By default, Jenkins uses credentials to access the upstream repositories.

1. Generate a personal access token to your fork on https://github.com/settings/tokens.
2. Replace the jenkins user credentials on Jenkins with your token on https://jenkins-test.erezlife.com/credentials/store/system/domain/_/credential/jenkins-github-plain-credential/.
3. Update the job to build from your fork instead of the upstream repository.
4. Update the job to build your test branch instead of master.
5. Trigger the job manually with the Build button.
