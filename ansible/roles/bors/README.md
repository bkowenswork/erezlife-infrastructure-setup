# Bors-ng

## GitHub app setup

Follow https://github.com/bors-ng/bors-ng#step-1-register-a-new-github-app.

## Initial synchronization

Visit https://bors.erezlife.com/ and grant it access to your GitHub. That
creates a user in bors-ng with your GitHub username.

Make yourself an admin by running a query on bors database:

```bash
$ sudo docker exec -it postgresql \
    psql -U postgres -d bors_ng \
    -c "UPDATE users SET is_admin=true WHERE login=GITHUB_USERNAME"
```

Refresh https://bors.erezlife.com/. On your account menu, visit the new
Administration entry. Press the “Sync installations” button. Visit the
repositories page, `erezlife/erezlife` should be listed.

On `erezlife/erezlife` details page, update the name of the staging and trying
branches to `bors-staging` and `bors-trying`. Can run the following query to the
same effect:

```bash
$ sudo docker exec -it postgresql \
    psql -U postgres -d bors_ng \
    -c "UPDATE projects SET staging_branch='bors-staging', trying_branch='bors-trying'"
```

## Activate the app

On the [GitHub app
details](https://github.com/organizations/erezlife/settings/apps/bors-erezlife),
check the “Active” checkbox to enable webhooks delivery to bors.
