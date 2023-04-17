# whoami

## Description

Show information about the active environment. This can be used to print the current user or client credentials and environment in use. The active environment can be changed with the [use env](./use-env.md) command.

This command can also be used to print an access token instead. This token is generated using the credentials associated with the active environment.

## Usage

```
lmctl whoami [OPTIONS]
```

## Options

| Name                 | Description                                                             | Default | Example |
| -------------------- | ----------------------------------------------------------------------- | ------- | ------- |
| `-t`, `--show-token` | Print only the current user access token, instead of the default output | -       | -t      |
| `-u`, `--show-user`  | Print only the user information, instead of the default output          | -       | -u      |
| `-e`, `--show-env`   | Print only the environment details, instead of the default output       | -       | -e      |

> Note: you can only use one of `-t`, `-u` or `-e`. 

## Examples

### Default

```
lmctl whoami
```

Example output:
```
User: jack
Environment: dev (https://myenv.example.com)
```

### Print Token

```
lmctl whoami -t 
```

Example output:
```
eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiRXhhbXBsZSIsIklzc3VlciI6Iklzc3VlciIsIlVzZXJuYW1lIjoiRXhhbXBsZSIsImV4cCI6MTY4MTczMTk5NywiaWF0IjoxNjgxNzMxOTk3fQ.siBmQylXDJw8ESxMEy3Xk2A9NGQytyj2Fvp4l7l-Uz0
```

### Print User

```
lmctl whoami -u
```

Example output:
```
jack
```

### Print Environment

```
lmctl whoami -e
```

Example output:
```
cp4na242 (https://cp4na-o-ishtar-lifecycle-manager.apps.cp4na242.cp.fyre.ibm.com)
```