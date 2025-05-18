import * as React from 'react';
import { BarChart } from '@mui/x-charts/BarChart';
import { ThemeProvider, createTheme } from '@mui/material/styles';

/////////////// Mock Data ///////////////
const datasets = [
  {
    correctness: [
      {
        correctness: 0.95,
        testcase: 'Claude Sonnet 3.5 moshe moshe',
      },
      {
        correctness: 0.91,
        testcase: 'Testcase7',
      },
      {
        correctness: 0.90,
        testcase: 'Testcase6',
      },
      {
        correctness: 0.85,
        testcase: 'Testcase5',
      },
      {
        correctness: 0.84,
        testcase: 'Testcase4',
      },
      {
        correctness: 0.77,
        testcase: 'Testcase3',
      },
      {
        correctness: 0.65,
        testcase: 'Testcase2',
      },
      {
        correctness: 0.50,
        testcase: 'Testcase1',
      },
    ],
  },
  {
    completeness: [
      {
        completeness: 0.65,
        testcase: 'Claude Sonnet 3.5 moshe moshe',
      },
      {
        completeness: 0.64,
        testcase: 'Testcase7',
      },
      {
        completeness: 0.63,
        testcase: 'Testcase6',
      },
      {
        completeness: 0.59,
        testcase: 'Testcase5',
      },
      {
        completeness: 0.59,
        testcase: 'Testcase4',
      },
      {
        completeness: 0.59,
        testcase: 'Testcase3',
      },
      {
        completeness: 0.58,
        testcase: 'Testcase2',
      },
      {
        completeness: 0.57,
        testcase: 'Testcase1',
      },
    ],
  },
  {
    relevance: [
      {
        relevance: 0.90,
        testcase: 'Claude Sonnet 3.5 moshe moshe',
      },
      {
        relevance: 0.80,
        testcase: 'Testcase7',
      },
      {
        relevance: 0.75,
        testcase: 'Testcase6',
      },
      {
        relevance: 0.75,
        testcase: 'Testcase5',
      },
      {
        relevance: 0.7,
        testcase: 'Testcase4',
      },
      {
        relevance: 0.7,
        testcase: 'Testcase3',
      },
      {
        relevance: 0.6,
        testcase: 'Testcase2',
      },
      {
        relevance: 0.5,
        testcase: 'Testcase1',
      },
    ],
  },
  {
    faithfulness: [
      {
        faithfulness: 0.49,
        testcase: 'Claude Sonnet 3.5 moshe moshe',
      },
      {
        faithfulness: 0.45,
        testcase: 'Testcase7',
      },
      {
        faithfulness: 0.44,
        testcase: 'Testcase6',
      },
      {
        faithfulness: 0.43,
        testcase: 'Testcase5',
      },
      {
        faithfulness: 0.30,
        testcase: 'Testcase4',
      },
      {
        faithfulness: 0.20,
        testcase: 'Testcase3',
      },
      {
        faithfulness: 0.20,
        testcase: 'Testcase2',
      },
      {
        faithfulness: 0.15,
        testcase: 'Testcase1',
      },
    ],
  },
];
////////////////////////////////////////

const theme = createTheme({
  colorSchemes: {
    dark: true,
  },
});

function valueFormatter(value) {
  return `${value}`;
}

const chartSetting = {
  xAxis: [
    {
      label: 'Normalized Score',
      colorMap: {
        type: 'continuous',
        max: 1.00,
        min: 0.50,
        color: ['orange', 'green']
      }
    },
  ],
  width: 1500,
  height: 400,
};

// See BarChart docs: https://mui.com/x/api/charts/bar-chart/
const SummaryReportControl = () => {
  return (
    <div className="p-6 max-w-7xl mx-auto bg-gray-900 text-gray-100 flex flex-col items-center text-center">
      <div className="mb-6">
        <div className="flex items-center mb-4">
          <svg width="32" height="32" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 mr-2">
            <circle cx="50" cy="50" r="48" stroke="#2E7D32" stroke-width="4" fill="#A5D6A7"/>
            <rect x="20" y="20" width="60" height="60" rx="5" fill="#66BB6A" stroke="#2E7D32" stroke-width="3"/>
            <path d="M30 40L37 47L45 35" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M30 50L37 57L45 45" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M30 60L37 67L45 55" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <rect x="50" y="45" width="5" height="20" fill="#388E3C"/>
            <rect x="60" y="40" width="5" height="25" fill="#1B5E20"/>
            <rect x="70" y="50" width="5" height="15" fill="#4CAF50"/>
          </svg>
          <h1 className="text-2xl font-semibold text-gray-100">LLM Evaluation Summary Report</h1>
        </div>
      </div>
      {datasets.map((data, index) => (
        <div key={index} className="mb-10">
          {Object.keys(data).map(key => (
            <BarChart
              key={key}
              margin={{ left: 500, right: 500 }}
              dataset={data[key]}
              yAxis={[{ scaleType: 'band', dataKey: 'testcase' }]}
              xAxis={[{ min: 0.0, max: 1.0 }]}
              series={[{ dataKey: key, label: key, valueFormatter, color: '#1a8400' }]}
              layout="horizontal"
              {...chartSetting}
            />
          ))}
        </div>
      ))}
    </div>
  );
};

function SummaryReport() {
  return (
    <ThemeProvider theme={theme}>
      <SummaryReportControl />
    </ThemeProvider>
  );
}

export default SummaryReport;
