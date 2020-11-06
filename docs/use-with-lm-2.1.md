# Using with ALM 2.1

To use this version of LMCTL with LM 2.1 you must replace the `rm` type the `lmproject.yml` files of your existing projects, changing the value of `brent` (or `lm`) to `brent2.1` (`lm2.1`). For example:

lmproject.yml
```
schema: '2.0'
name: example
version: '1.0'
type: Resource
resource-manager: brent2.1
```

Also, note that the `resourcedriver` command will not work with version 2.1. Instead you should use the `vimdriver` and `lifecycledriver` commands.