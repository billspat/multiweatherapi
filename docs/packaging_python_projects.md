# Packaging Python Projects

### Required libraries

- build
- twine
- pip

### Creating the package files

- pyproject.toml

  pyproject.toml tells “frontend” build tools like `pip` and `build` what “backend” tool to use to create distribution packages for your project. You can choose from a number of backends such as `setuptools`, `Hatchling`, etc.

  ```bash
  [build-system]
  requires = ["setuptools>=61.0"]
  build-backend = "setuptools.build_meta"
  ```

  - `requires` is a list of packages that are needed to build your package. You don’t need to install them; build frontends like pip will install them automatically in a temporary, isolated virtual environment for use during the build process.
  - `build-backend` is the name of the Python object that frontends will use to perform the build.

  > NOTE: Instead of having `setup.cfg` to build and package your project, you may just utilize `pyproject.toml` to note all the configurations required for your project to be packaged. See the  [project metadata specification](https://packaging.python.org/en/latest/specifications/declaring-project-metadata/#declaring-project-metadata) for details on these and other fields that can be defined in the `[project]` table. Other common fields are `keywords` to improve discoverability and the `dependencies` that are required to install your package.

- setup.cfg

  This configuration files is used by `setuptools` during package and contains various configuration information for your project. See the [confuguring setuptools using `setup.cfg` files](https://setuptools.pypa.io/en/latest/userguide/declarative_config.html) for details on various fields that can be defined in the `setup.cfg` file.

  > NOTE: The [Python Packaging Tutorial](https://packaging.python.org/tutorials/packaging-projects/) recommends that "Static metadata (setup.cfg) should be preferred.  Dynamic metadata (setup.py) should be used only as an escape hatch when  absolutely necessary. setup.py used to be required, but can be omitted  with newer versions of setuptools and pip."

- README.md

  Create project main README. This will be displayed on PyPI

- LICENSE

  Create license file. FYI: please refer to this page to choose from different licenses (https://choosealicense.com/)

### VERSION Info

- Be sure to check the ***VERSION*** information on following files

  - `setup.cfg` 
  - `multiweatherapi.py` (MWAPI specific)

  Python package will use version information in `setup.cfg` to create and note the version of your packaged project. The version information in the `multiweatherapi.py` is used by MWAPI for meta data and debuggin purposes.

  > NOTE: Keep in mind that no matter how small or large the change is, once the version number is used, it can never be reused unless you completely delete the project existence out of PyPI and start fresh from scratch.

### Generating Distribution Archives

The next step is to generate distribution packages for the package. These are archives that are uploaded to the Python Package Index and can be installed by pip.

1. Make sure you have the latest version of PyPA’s [build](https://packaging.python.org/en/latest/key_projects/#build) installed:

   ```bash
   python3 -m pip install --upgrade build
   ```

2. Run following command from the same directory where `pyproject.toml` is located:

   ```bash
   python3 -m build
   ```

3. The command should output a lot of text and once completed should generate two files in the `dist` directory:

   ```bash
   dist/
   ├── multiweatherapi-[VERSION]-py3-none-any.whl
   └── multiweatherapi-[VERSION].tar.gz
   ```

   > NOTE: The `tar.gz` file is a [source distribution](https://packaging.python.org/en/latest/glossary/#term-Source-Distribution-or-sdist) whereas the `.whl` file is a [built distribution](https://packaging.python.org/en/latest/glossary/#term-Built-Distribution). Newer [pip](https://packaging.python.org/en/latest/key_projects/#pip) versions preferentially install built distributions, but will fall back to source distributions if needed. You should always upload a source distribution and provide built distributions for the platforms your project is compatible with.

### Uploading the distribution archives

Make sure you register an account on PyPI and your email address must be verified before you are able to upload any packages.

> NOTE: This is optional but recommended. Please do create API Token from account manage `API Token` section, setting the ***Scope*** to ***Entire account***. Do ***NOT*** close the page until you have copied and saved the token. You will not be able to see that token ever again - You will need to delete and create new one.

You may utilize [twine](https://packaging.python.org/en/latest/key_projects/#twine) to upload the distribution packages.

```bash
python3 -m twine upload dist/*
```

You will be prompted for a username and password. For the username, use `__token__`. For the password, use the token value, including the `pypi-` prefix.

After the command completes, you should see output similar to this:

```bash
Uploading distributions to https://pypi.org
Enter your username: __token__
Uploading multiweatherapi-[VERSION]-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 8.2/8.2 kB • 00:01 • ?
Uploading multiweatherapi-[VERSION].tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6.8/6.8 kB • 00:00 • ?
```

Once uploaded, your package should be viewable on PyPI; for example:

https://pypi.org/project/multiweatherapi/