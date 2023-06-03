# `manipleservices`

A repository demonstrating:

- Many Python packages in one repo.
- That can depend on each other.
- That talk over function calls (as opposed to REST, message queue etc).
- With well-typed CircleCI configuration.
- **With CircleCI set up to only build what has changed.**

# Tree

```
├── LICENSE
├── README.md
└── packages
    ├── account
    │   ├── pyproject.toml
    │   ├── src
    │   │   ├── account
    │   │   │   ├── __init__.py
    │   │   │   ├── api
    │   │   │   │   ├── get.py
    │   │   │   │   └── post.py
    │   │   │   ├── db.py
    │   │   │   ├── py.typed
    │   │   │   └── users.py
    │   └── tests
    │       └── test_user.py
    └── shop
        ├── pyproject.toml
        ├── src
        │   ├── shop
        │   │   ├── __init__.py
        │   │   ├── api
        │   │   │   ├── get.py
        │   │   │   └── post.py
        │   │   ├── basket.py
        │   │   ├── client
        │   │   │   └── account.py
        │   │   └── py.typed
        └── tests
            └── test_basket.py
```

# Zero to running tests

```bash
ln -s $PWD/packages /tmp/maniple-packages  # a hack to avoid relative paths
cd packages/<some-package>
python -m venv .env
source .env/bin/activate
pip install -e '.[dev]'
pytest
```

# Notes

- We only call functions from `<other-package>.api`, this is by convention, but should probably be linted (and linted such that only "dumb data" can cross the interface).
- Note that we don't import any types from `<other-package>`, we make our own types.
    - When we call `<other-package>.api.f(a)`, `a` only has to conform to a `Protocol`, not a nominal type.
    - In the return type from `<other-package>.api(...) ->`, we can just choose which bits we need, we don't have to conform to the whole return type.
    - `mypy` will check that everything lines up.
- The aim of the above, is that if we for some reason wanted to switch inter-package communication from function calls to eg. REST, it should be trivial.
- In `.circleci/continue.py`, `changed_packages(...)` could be any function that returns a list of packages that you think have changed. Ditto with `add_dependant_packages(...)` - this would normally add any packages that depend on the ones that have changed.
- `pyproject.toml` doesn't seem to support specifying editable packages, [some discussion on this kind of thing]([https://peps.python.org/pep-0660/](https://github.com/jazzband/pip-tools/issues/204)). For a nicer dev experience while working cross-package, do eg: `pip install -e '../account[dev]'` (you could probably `sed` this into existence in your pip-tools generated `requirements-dev.txt`). This is also the reason for the `ln -s $PWD/packages /tmp/maniple-packages` in the setup instructions.
- As well as packages that are "service-like", you'd have eg: `packages/shop_integration_tests` that might depend on `account` and `shop` and run tests that depend on both of them.
- To complement the above, we might want that by convention, eg: `shop` would monkeypatch any methods of `account.api` that it uses during testing.

# CircleCI setup

Make sure in your project in the CircleCI UI, you have:

```
Project Settings > Advanced > Enable dynamic config using setup workflows
```

set to Enabled.
