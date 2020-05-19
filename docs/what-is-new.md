# What's new in LMCTL 2.5.0

# Changes for LM 2.2+

## resourcedriver command

New `resourcedriver` command added to manage drivers. 
Note: `vimdriver` and `lifecycledriver` should not be used with LM 2.2+, use `resourcedriver` instead. 

## Kubernetes driver project support

`lmctl project create` can generated the basic files needed to build a Resource suitable for the [Kubernetes driver](https://github.com/accanto-systems/kubernetes-driver) 

Try it out:
```
lmctl project create --type Resource --param driver kubernetes
```

## Support latest Brent package changes

The version of Brent included in LM 2.2+ no longer needs a `infrastructure` directory in the Resource package. Instead, templates are held in the lifecycle directory for the intended Resource driver. 

LMCTL has been updated to understand this new structure, so any new projects will adhere to the latest changes. 

Any existing projects must be refactored and may use the `--autocorrect` option on `project validate`, `project build` or `project push` commands to do so. Existing packages may also be refactored with the `--autocorrect` option on `pkg push`. 

If you intend to use this version of LMCTL with a 2.1 version of LM, then you must read [Use with LM 2.1](use-with-lm-2.1.md) and make changes to your project. Otherwise, use an older version of LMCTL when dealing with LM 2.1

# Other Changes

## Commands for managing infrastructure keys

A group of commands named `key` have been added to allow you to manage infrastructure keys in LM. 