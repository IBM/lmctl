# Add LMCTL to Python project

Assuming you are using <a href="https://pypi.org/project/setuptools/" target="_blank">Setuptools</a> to manage your Python project/application, you can add LMCTL as a dependency in your `setup.py` file:

```python
setup(
    name='My Application',
    install_requires=[
        'lmctl>=3.0'
    ]
)
```

This will ensure LMCTL is installed for any user installing your Python project/application.

Alternatively, you may add it to a `requirements.txt` file:

```
lmctl>=3.0
```

This will ensure LMCTL is installed when any user installs the dependencies listed in this file:

```
python3 -m pip install -r requirements.txt
```

