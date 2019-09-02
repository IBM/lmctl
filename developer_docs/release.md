# Release

The following steps detail how the LMCTL release is produced. This may only be performed by a user with admin rights to this Github and Pypi repository.

## 1. Setting the Version

Start by setting the version of the release in `lmctl/pkg_info.json`:

```
{
  "version": "<release version number>"
}
```

## 2. Build Python Wheel

Build the python wheel by navigating to the root directory of this project and executing:

```
python3 setup.py bdist_wheel
```

The whl file is created in `dist/`

## 3. Upload to Pypi

Upload the whl file to pypi using `twine` (note: this command will ask for your pypi repository access credentials)

```
python3 -m twine upload dist/<whl file>.whl
```
