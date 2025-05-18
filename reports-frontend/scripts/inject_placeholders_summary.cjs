const fs = require('fs');
const path = require('path');
const injectPlaceholders = require('./inject_placeholders_common.cjs');

////////////// Data to replace /////////
const datasets = "DATASETS_PLACEHOLDER"

/////////////////////////////////////////

// File paths
const HTML_FILE_PATH = 'dist/summary/summaryReport.html';
const OUTPUT_FILE_PATH = 'dist/summary/llm_summary_report_template.html';
const COPY_TO_DESTINATION = '../simpleval/commands/reporting/summarize'

injectPlaceholders(HTML_FILE_PATH, OUTPUT_FILE_PATH, COPY_TO_DESTINATION, [
  { name: 'datasets', value: datasets },
]);
