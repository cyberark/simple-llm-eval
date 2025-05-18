const fs = require('fs');
const path = require('path');
const injectPlaceholders = require('./inject_placeholders_common.cjs');

////////////// Data to replace /////////
const aggregateData = {
    leftSide: "AGGREGATE_DATA_LEFT_SIDE_PLACEHOLDER",
    rightSide: "AGGREGATE_DATA_RIGHT_SIDE_PLACEHOLDER"
}

const rowsData = "DATA_ITEMS_PLACEHOLDER"

/////////////////////////////////////////

// File paths
const HTML_FILE_PATH = 'dist/compare/compareReport.html';
const OUTPUT_FILE_PATH = 'dist/compare/compare_report_template.html';
const COPY_TO_DESTINATION = '../simpleval/commands/reporting/compare/compare_html2'

injectPlaceholders(HTML_FILE_PATH, OUTPUT_FILE_PATH, COPY_TO_DESTINATION, [
    { name: 'aggregateData', value: aggregateData },
    { name: 'rowsData', value: rowsData }
]);
