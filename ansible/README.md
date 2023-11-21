# Provision with Vagrant

First ensure your OS is supported by VirtualBox. Then follow the `VirtualBox`
[installation guide](https://www.virtualbox.org/wiki/Linux_Downloads) and
install `vagrant` with `dnf install vagrant`.

## ansible-server-setup

1. Fork the `ansible-server-setup` repository, and then clone it to your machine:
    ```console
    $ git clone git@github.com:<username>/ansible-server-setup.git
    ```

2. Change directory to `ansible-server-setup`.

3. Add the upstream to your local git repository:
   ```console
   $ git remote add upstream git@github.com:erezlife/ansible-server-setup.git
   ```

4. Make sure AWS buckets exist for your `<NAME>`:
    ```console
    $ for bucket in development{,-sftp,-tmp}-<NAME>
    do
        aws s3api create-bucket \
            --bucket $bucket \
            --create-bucket-configuration \
            LocationConstraint=ca-central-1
    done
    ```

5. Create `config.json` at the root of `ansible-server-setup`, replacing
   `<NAME>`, `<EMAIL>` and `<github_username>` with your information.

   ```json

    {
        "aws_region": "ca-central-1",
        "aws_backup_bucket": "anonymized-databases",
        "aws_sftp_bucket": "development-sftp-<NAME>",
        "aws_upload_bucket": "development-<NAME>",
        "aws_tmp_bucket": "development-tmp-<NAME>",
        "aws_lambda_namespace": "vagrant-<NAME>",
        "aws_log_group": "/<NAME>-erezlife",
        "debug": true,
        "email": "<EMAIL>",
        "first_name": "Test",
        "last_name": "User",
        "github_username": "<github_username>"
    }
    ```

6. Run `make` to create the virtual environment.
7. Fetch credentials with `make test-credentials`
8. `vagrant up`
9. *Wait for about half an hour until provisioning is complete.*
10. Add following line to `/etc/hosts`
    ```
    192.168.56.11 test.erezlife.com
    ```

## Connecting with SSH

SSH has a Trust On First Use policy: it records the fingerprint of the remote
host on the first connection and prevents future connections if the fingerprint
no longer matches what is stored in `~/.ssh/known_hosts`.

Because virtual machines are disposable, the `known_hosts` entry becomes
outdated every time the VMs are re-created. To avoid managing the known hosts,
add the following entry to your `~/.ssh/config`:

```ssh_config
Host 192.168.56.11 192.168.56.12 192.168.56.15 test.erezlife.com
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

## erezadmin

1. Fork the `erezadmin` repository, and then clone it to your machine:
    ```console
    $ git clone git@github.com:<username>/erezadmin.git
    ```
2. Change directory to `erezadmin`.
3. Run `make`
4. Deploy and create users. Your credentials will be emailed to you.
   ```console
   $ ./venv/bin/ansible-playbook -i hosts-dev ansible/deploy.yml
   ```

## eRezLife

### Deploying eRezLife

Change directory to `erezlife`.

1. Deploy target for eRezLife
    ```console
    make base
    ```

2. Deploy at least one target in {beta,beta-test,test,training}.
   Note that the target you use must match the target when creating the site.
    ```console
   ./venv/bin/ansible-playbook -v -i hosts-dev.yml ansible/deploy.yml --extra-vars 'target=<TARGET>'
    ```

3. Navigate to https://test.erezlife.com/erezadmin. Your credentials were emailed
to you.

## Cheatsheet

An overview of Vagrant is available in their [Getting
started](https://www.vagrantup.com/intro/getting-started/index.html)
documentation.

Action                          | Command
--------------------------------|----------------------------------
Start VMs                       | `vagrant up`
Reprovision existing VMs        | `vagrant provision`
Delete VMs                      | `vagrant destroy -f`
SSH-ing to a VM                 | `vagrant ssh web`
Restart VMs                     | `vagrant reload`
List current state of VMs       | `vagrant status`
Snapshot all VMs as `<name>`    | `vagrant snapshot save <name>`
Restore snapshot named `<name>` | `vagrant snapshot restore <name>`

The *vagrant* user is a “sudoer” without password.

## Logging to CloudWatch from a VM

Inside the AWS infrastructure, EC2 instances are [attributed the IAM
`CloudWatchAgentServerRole`](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/create-iam-roles-for-cloudwatch-agent.html)
that grants them permission to log to CloudWatch. That mechanism is not
available to the virtual machines hosted on your computer. To grant them
permission, connect to the VM and follow the steps for connecting from
on-premise machines.
https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/install-CloudWatch-Agent-commandline-fleet.html#install-CloudWatch-Agent-iam_user-first

## Troubleshooting

If the eRezLife sites are not working, check the erezadmin Celery log. To do
so, first ssh into the web server. From the `ansible-server-setup` directory:

```console
$ vagrant ssh webvm
```

Then, to view the log:

```console
$ less /var/log/erezadmin/celery.log
```

It is often useful to watch the Celery log in real time. Use `tail` for this:

```console
$ tail -F /var/log/erezadmin/celery.log
```

If an error occurred, a Python exception will exist somewhere in this log. Use
the traceback to help debug the issue.

# Provision Jenkins

To provision the live Jenkins EC2 instance, first ensure you have a clean
checkout of the latest ``master`` branch:

```console
$ git checkout master
$ git clean -dxfi
$ git pull --ff-only git@github.com:erezlife/ansible-server-setup.git master
```

Build the project and fetch secrets:

```console
$ make
```

Provision:

```console
$ ./venv/bin/ansible-playbook jenkins.yml
```

## Connecting to Jenkins

Edit your SSH configuration file (`$EDITOR "$HOME/.ssh/config"`) to add the
following section:

```ssh_config
Host jenkins jenkins.erezlife.com
    Hostname jenkins.erezlife.com
    User centos
    IdentityFile /path/to/ansible-server-setup/ssh/aws_jenkins.pem
```

The `aws_jenkins.pem` file is available after running `make credentials` (see
section above).

Test your connection with `ssh jenkins`. The SSH connection should be
successful and the prompt should be similar to:

```console
$ ssh jenkins
Last login: Tue Dec  1 16:26:39 2020 from 75.157.123.48
[centos@ip-10-0-1-167 ~]$
```
