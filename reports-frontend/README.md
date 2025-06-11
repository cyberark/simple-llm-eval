# react + Vite Reports

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Build and run the reports

* install packages: `npm install`
* build all reports: `npm run build` or `npm run build:eval`/`npm run build:compare`/`npm run build:summary`
* run tests (watch): `npm run test`

## What was done

### Main steps

- `npm create vite@latest local-report-app`
    - choose: React, Javascript
- `cd local-report-app`
- `npm install`
- `npm run dev`
- `npm install lucide-react`
- followed tailwindcss guide: https://tailwindcss.com/docs/installation/using-vite for vite
    - added the css import in index.css
- added code in `src/components/LLMEvalReport.jsx`
- update main.jsx: 
    - import LLMEvalReport from './components/LLMEvalReport.jsx'
    - LLMEvalReport
- `npm run dev` to load page
- cleanups: `rm -rf node_modules package-lock.json` (then `npm install`)
- disabled minification in `vite.config.js` (build.minify = false)

### Self contained html
* once: `npm install vite-plugin-singlefile --save-dev`
* once: updated `vite.config.js` to include the plugin
* after each change:
    * run `npm run build`
    * see `dist/.../...html`
    * run only individual app: `npm run build:eval` or `npm run build:compare`

### AST Manipulation
To be able to inject placeholders I did:
* `npm install @babel/parser @babel/traverse @babel/generator`
* created `inject_placeholders_eval.js` to inject placeholders into the eval report
* created `inject_placeholders_compare.js` to inject placeholders into the compare report
* Run the scripts in package.json

### Additional components for charts
Some reports like summary and radar users additional components from material-ui
* followed instructions in https://mui.com/material-ui/getting-started/installation/
* charts from: https://mui.com/x/react-charts/

### Testing
* To solve some issues I had to add the test section in `vite.config.js` and also the `tests/setup.jsx`
* To run tests in vscode I had to set `vite.config.js` in `Vitest: Root Config`

## Other resources
### Some react examples
* https://dribbble.com/shots/21455518-Filter-Component
* https://dribbble.com/shots/21712963-Add-Tags-Filter-System

## Assorted components sites
* https://ui.shadcn.com/
* https://mui.com/
* https://chakra-ui.com/
* html reports: https://www.chartjs.org/
