#  Command Reference

We aim to maintain readable and useful help pages which can be access directly from lmctl:

```
lmctl --help

lmctl create --help
lmctl delete --help

lmctl create assembly --help
lmctl create descriptor --help 
```

We recommend referring to these first. If you find they are unclear or not helpful, please raise a Github issue with your feedback so we can improve them :speech_balloon:

As a result, we are no longer adding command reference documents to this section. 

Below are a list of command references written previously, which will maintained for the forseeable.

## Project command reference

## pkg

- [inspect](./pkg/inspect.md)
- [push](./pkg/push.md)

## project

- [build](./project/build.md)
- [create](./project/create.md)
- [list](./project/list.md)
- [pull](./project/pull.md)
- [push](./project/push.md)
- [test](./project/test.md)
- [validate](./project/validate.md)

## Deprecated command reference

These commands are deprecated in v3.0

## deployment

- [add](./deployment/add.md)
- [delete](./deployment/delete.md)
- [get](./deployment/get.md)
- [list](./deployment/list.md)

## env

- [list](./envs/list.md)

## key

- [add](./key/add.md)
- [delete](./key/delete.md)
- [get](./key/get.md)
- [list](./key/list.md)

## resourcedriver (ALM 2.2+ only)

**Note:** use [lifecycledriver](#lifecycledriver) and [vimdriver](#vimdriver) if using a 2.1 version of ALM version

- [add](./resourcedriver/add.md)
- [delete](./resourcedriver/delete.md)
- [get](./resourcedriver/get.md)

## lifecycledriver (ALM 2.1 only)

**Note:** use [resourcedriver](#resourcedriver) for ALM versions 2.2+

- [add](./lifecycledriver/add.md)
- [delete](./lifecycledriver/delete.md)
- [get](./lifecycledriver/get.md)

## vimdriver (ALM 2.1 only)

**Note:** use [resourcedriver](#resourcedriver) for ALM versions 2.2+

- [add](./vimdriver/add.md)
- [delete](./vimdriver/delete.md)
- [get](./vimdriver/get.md)
