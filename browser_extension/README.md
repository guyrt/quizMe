## Node Setup
### Install [Node Version Manager](https://github.com/nvm-sh/nvm) (nvm)
```shell
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
```
### Reopen terminal

### Install Latest Node [Docs](https://github.com/nvm-sh/nvm?tab=readme-ov-file#usage)
```shell
nvm install node
```
### Use node installed in prior step: 
```shell
nvm use node
```
## Yarn Steps 
[Yarn Docs](https://yarnpkg.com/getting-started/install)
### Enable corepack 
```shell
corepack enable
```
### Install yarn managed packages
```shell
yarn
yarn dev
```

Load the `dist` folder as your extension.

### Linting: 
```shell
yarn run lint --fix
yarn run format 
```