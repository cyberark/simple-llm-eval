const fs = require('fs');
const path = require('path');
const injectPlaceholders = require('./inject_placeholders_common.cjs');

////////////// Data to replace /////////
const evalNameTestCase = "EVAL_TESTCASE_TITLE_PLACEHOLDER"

const rowsData = "DATA_ITEMS_PLACEHOLDER"

const aggregateData = "AGGREGATE_DATA_PLACEHOLDER"

const errors = {
  llmErrors: 0,
  evalErrors: 0,
}
/////////////////////////////////////////

// File paths
const HTML_FILE_PATH = 'dist/eval/evalReport.html';
const OUTPUT_FILE_PATH = 'dist/eval/llm_eval_report_template.html';
const COPY_TO_DESTINATION = '../simpleval/commands/reporting/eval/html2'

injectPlaceholders(HTML_FILE_PATH, OUTPUT_FILE_PATH, COPY_TO_DESTINATION, [
  { name: 'evalNameTestCase', value: evalNameTestCase },
  { name: 'rowsData', value: rowsData },
  { name: 'aggregateData', value: aggregateData },
  { name: 'errors', value: errors }
]);
