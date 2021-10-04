# login

## Description

Authenticate with an environment and save credentials in the lmctl config file for subsequent use

## Usage

```
lmctl login [OPTIONS] ADDRESS
```

## Arguments

| Name        | Description                                        | Default | Example                    |
| ----------- | -------------------------------------------------- | ------- | -------------------------- |
| Address | API gateway (Ishtar) address of the target environment | -       | alm-ishtar.example.com     |

## Options

| Name             | Description                                                                                                                          | Default                       | Example                                    |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- | ------------------------------------------ |
| `-u`, `--username`       | Username used to authenticate                           | - | --username almadmin   |
| `-p`, `--pwd`, `--password`          | Password used for authenticating the user given on `username`  | -                             | --pwd secret                               |
| `--api-key`         | API Key for the given user (when using "--zen")       | -                       | --api-key 123                             |
| `--client`         | Client ID used to authenticate       | -                       | --client Admin                             |
| `--client-secret`          | Secret used for authenticating the client given on `client`   | -                             | --client-secret secret |
| `--token` | Authenticate with a token instead of credentials    | -                         | --token eyJhbGciOiJIUzI1NiIsInR5cCI6.....8enat7Ao       |
| `--zen` | Indicate that the Zen authentication method should be used (must provide --api-key) | False | --zen |
| `--name` | Name given to the environment saved in the configuration file | default | --name dev |
| `--auth-address` | Auth address required for username/password access (without client credentials). This is usually the Nimrod route in your environment. When `--zen` is provided, this should be the address for the Zen authorization API | - | --auth-address alm-nimrod.example.com |
| `--save-creds` | Save the credentials instead of the token | False | --save-creds |
| `--print` | Print the access token rather than saving it | False | --print |
| `-y` | Force command to accept all confirmation prompts e.g. to override existing environment with the same name | False | -y |

## Examples

### Combination 1: Login with UI username/password

```
lmctl login alm-ishtar.example.com --auth-address alm-nimrod.example.com --username almadmin --password password
```

### Combination 2: Login with Rest API username/password

```
lmctl login alm-ishtar.example.com --client Client --client-secret secret --username almadmin --password password
```

> Note: if you run `lmctl login alm-ishtar.example.com` then you will be prompted for the values suited to this combination

### Combination 3: Login with Rest API client credentials

```
lmctl login alm-ishtar.example.com --client Admin --client-secret secret
```

### Combination 4: Login with existing Token

```
lmctl login alm-ishtar.example.com --token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZSI6WyJhbGwiXSwiZXhwIjoxNjIzMTEwNTc4LCJhdXRob3JpdGllcyI6WyJSRVNPVVJDRVBLR19XUklURSIsIk5TSU5TVFNNR1RfV1JJVEUiLCJJTlRFTlRSRVFTT1BTX1JFQUQiLCJWTkZJTlNUU01HVF9SRUFEIiwiVkRVTUdUX1dSSVRFIiwiTlNERVNNR1RfUkVBRCIsIlJNRFJWUktFWVNfUkVBRCIsIlZEVUdSUE1HVF9XUklURSIsIlZEVURFU01HVF9FWEVDVVRFIiwiVk5GREVTTUdUX0VYRUNVVEUiLCJCRUhWUlNDRU5FWEVDX1dSSVRFIiwiUk1EUlZSX1dSSVRFIiwiVkRVREVTTUdUX1dSSVRFIiwiU0xNQURNSU5fUkVBRCIsIlNMTUFETUlOX0VYRUNVVEUiLCJWTkZJTlNUU01HVF9FWEVDVVRFIiwiVkRVTUdUX0VYRUNVVEUiLCJTTE1BRE1JTl9XUklURSIsIlZEVUdSUE1HVF9SRUFEIiwiVk5GREVTTUdUX1JFQUQiLCJERVBMT1lMT0NNR1RfRVhFQ1VURSIsIkJFSFZSU0NFTkRFU19SRUFEIiwiTUFJTlRNT0RFT1JJREVfUkVBRCIsIklOVEVOVFJFUVNPUFNfRVhFQ1VURSIsIk5TREVTTUdUX0VYRUNVVEUiLCJERVBMT1lMT0NNR1RfUkVBRCIsIlJNRFJWUl9SRUFEIiwiVkRVSU5TVFNNR1RfV1JJVEUiLCJOU0RFU01HVF9XUklURSIsIk5TSU5TVFNNR1RfUkVBRCIsIk5TSU5TVFNNR1RfRVhFQ1VURSIsIk1BSU5UTU9ERU9SSURFX0VYRUNVVEUiLCJCRUhWUlNDRU5ERVNfV1JJVEUiLCJWTkZJTlNUU01HVF9XUklURSIsIlZEVUlOU1RTTUdUX1JFQUQiLCJWRFVHUlBNR1RfRVhFQ1VURSIsIkRFUExPWUxPQ01HVF9XUklURSIsIkJFSFZSU0NFTkVYRUNfUkVBRCIsIlZEVUlOU1RTTUdUX0VYRUNVVEUiLCJJTlRFTlRSRVFTTE1HVF9SRUFEIiwiSU5URU5UUkVRU0xNR1RfRVhFQ1VURSIsIlZEVURFU01HVF9SRUFEIiwiQkVIVlJTQ0VORVhFQ19FWEVDVVRFIiwiVk5GREVTTUdUX1dSSVRFIiwiVkRVTUdUX1JFQUQiXSwianRpIjoiZWE2NTFkMTQtNGJhNy00NDUyLWE0MWUtYjcxYWM2ZTIzZTBkIiwiY2xpZW50X2lkIjoiTG1DbGllbnQifQ.Csx0FT8q0ZWAatKUUofpTfyjcolnm7ziJ4s8enat7Ao
```

### Combination 5: Login with Zen username/api-key

```
lmctl login alm-ishtar.example.com --auth-address zen.example.com --zen --username almadmin --api-key 123
```

### Save with alternative name

This will name the environment `my-test-env` instead of the `default` value.

```
lmctl login alm-ishtar.example.com --client Admin --client-secret secret --name my-test-env
```

Check the environment:

```
lmctl get env my-test-env
```

### Update environment

You may call `login` on an existing environment to refresh the token or to replace credentials. You will be asked to confirm that the existing environment should be overriden:

```
# First login
lmctl login alm-ishtar.example.com --client Admin --client-secret secret

# Second login
lmctl login alm-ishtar.example.com --client Admin --client-secret alt-secret

Login success
An environment with name "default" already exists, do you want to override it? [y/N]: y
Updating config at: /home/dvs/.lmctl/config.yaml
```

Alternatively, supply `-y` to pre-confirm:

```
lmctl login alm-ishtar.example.com --client Admin --client-secret alt-secret -y

Login success
Updating config at: /home/dvs/.lmctl/config.yaml
```

### Prompt for password

```
lmctl login alm-ishtar.example.com --auth-address alm-nimrod.example.com --username almadmin

Password []:
Login success
Updating config at: /home/myuser/.lmctl/config.yaml
```

### Prompt for client secret

```
lmctl login alm-ishtar.example.com --client Admin 

Client Secret []:
Login success
Updating config at: /home/myuser/.lmctl/config.yaml
```