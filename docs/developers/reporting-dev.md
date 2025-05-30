# Reporting Dev 📊🧑‍💻

## Prerequisites 🛠 

* `Node.js` (v18.20.6 or higher)
* `npm`
️
## Building the Reports 🏗

* Run `cd reports-frontend`
* Install packages: `npm install`
* Build all reports: `npm run build`
* Build single reports:
    * `npm run build:eval`
    * `npm run build:compare`
    * `npm run build:summary`

## Running the Tests 🧪

* Run tests (watch): `npm run test`
* Run tests (once): `npm run test-no-watch`

## New Reports 🤖📊
The new reports are implemented with React with vite as the build tool.
Each report is a standalone React app that is built into a single, self contained HTML file.
This means that you can simply load the html file without needing to run a server.
It does not use TS, but it probably should eventually.

The react project is in `simpleval/reports-frontend`

Each such react app generates an HTML template that needs to be populated with data by simpleval and then saved to disk.

The results and compare reports use native react, and the summary report use Material UI.

There are some internal notes here: `reports-frontend/README.md`

## Populating the Templates 📝📊
Take a look at `reports-frontend/src/components/LLMEvalReport.jsx`
You will see mock data that is used during testing.
In this case they are:

* `rowsData`
* `aggregateData`
* `errors`

Those needs to be overwritten by simpleval with the actual data.
To do that, we have injection scripts thar run during build and create the html templates with data placeholders.
Each component has a corresponding injection script in `reports-frontend/scripts/`

In our example look at: `reports-frontend/scripts/inject_placeholders_eval.cjs`

It defines the data placeholders to inject to the html (and replace the mock data) and also where to copy the template to (This is the place that simpleval expects to find it - in our example - `simpleval/commands/reporting/eval_report/html2`).

In simpleval we need to know these placeholder and replace them with the actual data.
See: `simpleval/commands/reporting/eval_report/html2/html2_report.py`

## Adding a New Report 🚀📊
Going through all the points here let you know about the important elements of the new reports.

### Create a new component file
* Create a new component file in `reports-frontend/src/components`, you can copy one of the existing files, for this example let's say we copy `SummaryReport.jsx`
* Rename the file, in it rename all the relevant parts (e.g. `SummaryReportControl`, `SummaryReport` - this can change depending on the report you copied)
* Remove all unwanted code (generally keep only the icon and the title)

### Create a Main File
* copy `reports-frontend/src/summaryMain.jsx` and rename it.
* update the import to your new component (don't forget to update both the name of the component and the import)

### Create an html File
* copy `summaryReport.html` and rename it.
* update the import to your new main file.
* update the title

### Create an Injection File
* create an injection script in `reports-frontend/scripts/`
* copy one of the existing scripts and rename it.
* update the placeholders according to your implementation.
* update the destination folder (This is where simpleval code expects to find the template)

### Update `package.json`
* create a build step: e.g. copy `"build:summary"` and rename it.
* update `build` to include your new build step.
* create a new postbuild step: copy for example `postbuild:summary` and update as needed.

### Component Level `vite` Config File
* copy `vite.config.summary.js` and rename it for you component
* update `build.rollupOptions.input` to match your new component HTML file.  
* update `build.outDir` to match your new component output directory.

### Global `vite` Config
* update `vite.config.js` - add your new vite config file to `build.rollupOptions.input`

### Component Implementation
* Implement your component
* If you want an example of a react native component, look at `LLMEvalReport.jsx` or `CompareReport.jsx`
* If you want an example of a Material UI component, look at `SummaryReport.jsx`
* Implement tests - see `LLMEvalReport.test.jsx` for an example of a react native component test, as a minimum , test that the component renders correctly.
