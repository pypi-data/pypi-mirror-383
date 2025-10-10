# Robocorp Inspector

Robocorp Inspector is a tool for exploring various user interfaces
and developing ways to target elements within them. An expression
that can target specific UI elemements is called a _locator_, and
these locators can be used to automate applications typically
used by humans.

## Dependencies

You might need to create a `.npmrc` file at project level with contents similar to the following, but with your own `authToken`.
This is needed for private repositories.

```
registry=https://registry.npmjs.org/
@robocorp:registry=https://npm.pkg.github.com/
//npm.pkg.github.com/:_authToken=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

> There is a hard dependency to the [Inspector Commons](https://github.com/robocorp/inspector-commons) implementation.
> Most of the implementation resides in `inspector-commons` and if you spot any misalignment then you should correct it

## Development

The project uses `invoke` for overall project management, `poetry` for
python dependencies and environments, and `yarn` for Javascript dependencies
and building.

Both `invoke` and `poetry` should be installed via pip: `pip install poetry invoke`

- To see all possible tasks: `invoke --list`
- To run the project: `invoke run `
- For a quick build and run you can try running: `inv build-js && inv build && inv run`
- To clean the dev environment you can use `inv clean` or `inv clean --force`

All source code is hosted on [GitHub](https://github.com/robocorp/inspector/).

### Python & NPM

To launch the development environment you'll need:
```
pyenv + virtualenv -> these will help building a dedicated python virtual environment
nvm -> will help with a contained version of node + npm
```

In order for everything to install and build properly use the following versions:
```
python -> v3.8.10
node -> v16.14.2
npm -> 8.5.0
```

## Usage

Robocorp Inspector is distributed as a Python package with all front-end
components compiled and included statically.

If the package (and all required dependencies) is installed manually,
it can be run with the command: `inspector`.

## Code Organization

> Attention: these might change over time & hopefully they will be maintained.

### Inspector Class Diagram

- not extremely precise
- created to show how things link together from local implementation to `inspector-commons`

![Inspector Class Diagram](./assets/InspectorClassDiagram.jpg)

---

<p align="center">
  <img height="100" src="https://cdn.robocorp.com/brand/Logo/Dark%20logo%20transparent%20with%20buffer%20space/Dark%20logo%20transparent%20with%20buffer%20space.svg">
</p>
