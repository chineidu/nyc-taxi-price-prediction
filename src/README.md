# Add Git Tag

```console
# Create tag
$ git tag <tag> -m "enter your message"

# Push the tag to remote repo
$ git push origin <tag> 
```

## Create A Package (Locally)

* In the root directory of your project which mush contain `setup.py` and `requirements.txt`\
run the command:

```console
# To build package
$ python setup.py sdist
# Install package in editable mode
$ pip install -e .
```
