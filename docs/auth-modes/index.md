# Authentication Modes

## Cloud Paks

**Users of Cloud Pak for Network Automation** should read the [Login to Cloud Pak for Network Automation](#../getting-started.md#login-to-cloud-pak-for-network-automation) section of the getting started guide.

The other types of authentication listed in this section are for other types of environments.

## Client Credentials

> Note: Cloud Pak installations do not support this method

To login client credentials, you must have a set of valid credentials created on your behalf by an admin, using the `/api/v1/credentials` API. 

Run `lmctl login`, changing the `--client` values to valid credentials for your environment:

```
lmctl login $API_GATEWAY --client my-client
```

You will be prompted for your client secret:

```
Client Secret []: 
```

> Note: if you need to login from an environment which cannot support prompts then the secret can be provided with the `--client-secret` option instead. Note, caution is advised as this may make the secret visible in your command history.

You should see output similar to:

```
Login success
Updating config at: /home/myuser/.lmctl/config.yaml
```

You can test access is ready using `ping`:

```
lmctl ping env
```

If the output of this command ends with `CP4NA orchestration tests passed! ✅` then you're ready to go. 

## OAuth Username and Password

> Note: Cloud Pak installations do not support this method

To login username and password you use to access the NA4D/ALM/TNCO orchestration user interface (UI), you will need to provide the UI address (Nimrod) for your environment. On most OCP installations, this can be retrieved with:

```
UI_ADDRESS=https://$(oc get route cp4na-o-nimrod -o jsonpath='{.spec.host}')
```

On other installations, Nimrod may be accessed by an Ingress or port instead.

Run `lmctl login`, changing the `--username` values to valid credentials for your environment:

```
lmctl login $API_GATEWAY --auth-address $UI_ADDRESS --username almadmin
```

You will be prompted for your password:

```
Password []: 
```

> Note: if you need to login from an environment which cannot support prompts then the password can be provided with the `--password` option instead. Note, caution is advised as this may make the password visible in your command history.

You should see output similar to:

```
Login success
Updating config at: /home/myuser/.lmctl/config.yaml
```

You can test access is ready using `ping`:

```
lmctl ping env
```

If the output of this command ends with `CP4NA orchestration tests passed! ✅` then you're ready to go. 