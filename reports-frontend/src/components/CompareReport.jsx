import React, { useState } from 'react';
import { Search, Filter, ChevronDown, ChevronUp } from 'lucide-react';

const evalSet = "EVAL-SET-PLACEHOLDER";

/////////////////////// MOCK DATA /////////////////////////
const aggregateData = {
  leftSide: {
    testcase: "Left Side Testcase",
    metrics: [
      { metric: "correctness", score: 0.91 },
      { metric: "relevance", score: 0.51 },
      { metric: "completeness", score: 0.21 },
      { metric: "aggregate mean", score: 0.31 },
    ]
  },
  rightSide: {
    testcase: "Right Side Testcase",
    metrics: [
      { metric: "completeness", score: 0.92 },
      { metric: "correctness", score: 0.42 },
      { metric: "relevance", score: 0.62 },
      { metric: "aggregate mean", score: 0.72 },
    ]
  }
}

const rowsData = [
  {
    metric: "completeness",
    rows: [
      {
        testCaseTest: "testcase1:test1",
        promptToLLM: "prompt to llm test1 1:1",
        llmResponse: "The user clicked on the 'EC2' icon in the taskbar. 1:1",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 1:1",
        normalizedScore: 0.75,
        evalResult: "Partially",
        explanation: "The response was somewhat accurate but missed some key details. 1:1",
        extraInfo: "this is extra info for 1:1!"
      },
      {
        testCaseTest: "testcase2:test1",
        promptToLLM: "prompt to llm test1 B 2:1",
        llmResponse: "The user clicked on the 'EC3 Microsoft Windows' icon in the start menu on the desktop. 2:1",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 2:1",
        normalizedScore: 1.0,
        evalResult: "Generally",
        explanation: "The response was mostly correct with minor inaccuracies. 2:1"
      }
    ]
  },
  {
    metric: "correctness",
    rows: [
      {
        testCaseTest: "testcase1:test1",
        promptToLLM: "prompt to llm test1 A 1:1",
        llmResponse: "The user clicked on the 'EC4' icon in the taskbar. 1:1",
        expectedLLMResponse: "The user clicked the EC4 Microsoft Window Icon 1:1",
        normalizedScore: 0.5,
        evalResult: "Not Really",
        explanation: "The response did not meet the expected criteria. 1:1"
      },
      {
        testCaseTest: "testcase2:test1",
        promptToLLM: "specialprompt prompt to llm test1 B 2:1",
        llmResponse: "The user clicked on the 'EC2 Microsoft Windows' icon in the start menu on the desktop. 2:1",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 2:1",
        normalizedScore: 1.0,
        evalResult: "Correct",
        explanation: "The response was accurate and met all expectations. 2:1"
      }
    ]
  },
  {
    metric: "relevance",
    rows: [
      {
        testCaseTest: "testcase1:test1",
        promptToLLM: "prompt to llm test1 A 1:1",
        llmResponse: "The user clicked on the 'EC2' icon in the taskbar. 1:1",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 1:1",
        normalizedScore: 0.5,
        evalResult: "Awesome",
        explanation: "The response was excellent and exceeded expectations. 1:1"
      },
      {
        testCaseTest: "testcase2:test1",
        promptToLLM: "prompt to llm test1 B 2:1",
        llmResponse: "The user clicked on the 'EC2 Microsoft Windows' icon in the start menu on the desktop. 2:1",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 2:1",
        normalizedScore: 1.0,
        evalResult: "Partially",
        explanation: "The response was somewhat accurate but missed some key details. 2:1",
        extraInfo: "this is extra info! 2:1"
      }
    ]
  },
  {
    metric: "completeness",
    rows: [
      {
        testCaseTest: "testcase1:test2",
        promptToLLM: "prompt to llm test2 A 1:2",
        llmResponse: "The user clicked on the 'EC2' icon in the taskbar. 1:2",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 1:2",
        normalizedScore: 0.0,
        evalResult: "Generally",
        explanation: "The response was mostly correct with minor inaccuracies. 1:2"
      },
      {
        testCaseTest: "testcase2:test2",
        promptToLLM: "prompt to llm test2 B 2:2",
        llmResponse: "The user clicked on the 'EC2 Microsoft Windows' icon in the start menu on the desktop. 2:2",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 2:2",
        normalizedScore: 1.0,
        evalResult: "Not Really",
        explanation: "The response did not meet the expected criteria. 2:2"
      }
    ]
  },
  {
    metric: "correctness",
    rows: [
      {
        testCaseTest: "testcase1:test2",
        promptToLLM: "prompt to llm test2 A 1:2",
        llmResponse: "The user clicked on the 'EC2' icon in the taskbar. 1:2",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 1:2",
        normalizedScore: 0.5,
        evalResult: "Correct",
        explanation: "The response was accurate and met all expectations. 1:2"
      },
      {
        testCaseTest: "testcase2:test2",
        promptToLLM: "prompt to llm test2 B 2:2",
        llmResponse: "The user clicked on the 'EC2 Microsoft Windows' icon in the start menu on the desktop. 2:2",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 2:2",
        normalizedScore: 1.0,
        evalResult: "Awesome",
        explanation: "The response was excellent and exceeded expectations. 2:2"
      }
    ]
  },
  {
    metric: "relevance",
    rows: [
      {
        testCaseTest: "testcase1:test2",
        promptToLLM: "prompt to llm test2 A 1:2",
        llmResponse: "The user clicked on the 'EC2' icon in the taskbar. 1:2",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 1:2",
        normalizedScore: 1.0,
        evalResult: "Partially",
        explanation: "The response was somewhat accurate but missed some key details. 1:2"
      },
      {
        testCaseTest: "testcase2:test2",
        promptToLLM: "prompt to llm test2 B 2:2",
        llmResponse: "The user clicked on the 'EC2 Microsoft Windows' icon in the start menu on the desktop. 2:2",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 2:2",
        normalizedScore: 0.1,
        evalResult: "Generally",
        explanation: "The response was mostly correct with minor inaccuracies. 2:2"
      }
    ]
  },
  {
    metric: "completeness",
    rows: [
      {
        testCaseTest: "testcase1:test3",
        promptToLLM: "prompt to llm test1 A 1:3",
        llmResponse: "The user clicked on the 'EC2' icon in the taskbar. 1:3",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 1:3",
        normalizedScore: 0.75,
        evalResult: "Not Really",
        explanation: "The response did not meet the expected criteria. 1:3"
      },
      {
        testCaseTest: "testcase2:test3",
        promptToLLM: "prompt to llm test1 B 2:3",
        llmResponse: "The user clicked on the 'EC3 Microsoft Windows' icon in the start menu on the desktop. 2:3",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 2:3",
        normalizedScore: 1.0,
        evalResult: "Correct",
        explanation: "The response was accurate and met all expectations. 2:3"
      }
    ]
  },
  {
    metric: "correctness",
    rows: [
      {
        testCaseTest: "testcase1:test3",
        promptToLLM: "prompt to llm test1 A 1:3",
        llmResponse: "The user clicked on the 'EC4' icon in the taskbar. 1:3",
        expectedLLMResponse: "The user clicked the EC4 Microsoft Window Icon 1:3",
        normalizedScore: 1.0,
        evalResult: "Awesome",
        explanation: "The response was excellent and exceeded expectations. 1:3"
      },
      {
        testCaseTest: "testcase2:test3",
        promptToLLM: "prompt to llm test1 B 2:3",
        llmResponse: "The user clicked on the 'EC2 Microsoft Windows' icon in the start menu on the desktop. 2:3",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 2:3",
        normalizedScore: 1.0,
        evalResult: "Partially",
        explanation: "The response was somewhat accurate but missed some key details. 2:3"
      }
    ]
  },
  {
    metric: "relevance",
    rows: [
      {
        testCaseTest: "testcase1:test3",
        promptToLLM: "prompt to llm test1 A 1:3",
        llmResponse: "The user clicked on the 'EC2' icon in the taskbar. 1:3",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 1:3",
        normalizedScore: 0.5,
        evalResult: "Generally",
        explanation: "The response was mostly correct with minor inaccuracies. 1:3"
      },
      {
        testCaseTest: "testcase2:test3",
        promptToLLM: "prompt to llm test1 B 2:3",
        llmResponse: "The user clicked on the 'EC2 Microsoft Windows' icon in the start menu on the desktop. 2:3",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 2:3",
        normalizedScore: 1.0,
        evalResult: "Not Really",
        explanation: "The response did not meet the expected criteria. 2:3"
      }
    ]
  },
  {
    metric: "completeness",
    rows: [
      {
        testCaseTest: "testcase1:test4",
        promptToLLM: "prompt to llm test2 A 1:4",
        llmResponse: "The user clicked on the 'EC2' icon in the taskbar. 1:4",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 1:4",
        normalizedScore: 0.75,
        evalResult: "Correct",
        explanation: "The response was accurate and met all expectations. 1:4"
      },
      {
        testCaseTest: "testcase2:test4",
        promptToLLM: "prompt to llm test2 B 2:4",
        llmResponse: "The user clicked on the 'EC2 Microsoft Windows' icon in the start menu on the desktop. 2:4",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 2:4",
        normalizedScore: 1.0,
        evalResult: "Awesome",
        explanation: "The response was excellent and exceeded expectations. 2:4"
      }
    ]
  },
  {
    metric: "correctness",
    rows: [
      {
        testCaseTest: "testcase1:test4",
        promptToLLM: "prompt to llm test2 A 1:4",
        llmResponse: "The user clicked on the 'EC2' icon in the taskbar. 1:4",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 1:4",
        normalizedScore: 0.5,
        evalResult: "Partially",
        explanation: "The response was somewhat accurate but missed some key details. 1:4"
      },
      {
        testCaseTest: "testcase2:test4",
        promptToLLM: "prompt to llm test2 B 2:4",
        llmResponse: "The user clicked on the 'EC2 Microsoft Windows' icon in the start menu on the desktop. 2:4",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 2:4",
        normalizedScore: 1.0,
        evalResult: "Generally",
        explanation: "The response was mostly correct with minor inaccuracies. 2:4"
      }
    ]
  },
  {
    metric: "relevance",
    rows: [
      {
        testCaseTest: "testcase1:test4",
        promptToLLM: "prompt to llm test2 A 1:4",
        llmResponse: "The user clicked on the 'EC2' icon in the taskbar. 1:4",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 1:4",
        normalizedScore: 0.1,
        evalResult: "Not Really",
        explanation: "The response did not meet the expected criteria. 1:4"
      },
      {
        testCaseTest: "testcase2:test4",
        promptToLLM: "prompt to llm test2 B 2:4",
        llmResponse: "The user clicked on the 'EC2 Microsoft Windows' icon in the start menu on the desktop. 2:4",
        expectedLLMResponse: "The user clicked the EC2 Microsoft Window Icon 2:4",
        normalizedScore: 1.0,
        evalResult: "Correct",
        explanation: "The response was accurate and met all expectations. 2:4"
      }
    ]
  }
];
///////////////////////////////////////////////////////////

const getLabelClass = (leftScore, rightScore, isLeft) => {
  if (isLeft && leftScore > rightScore) return 'bg-green-900 text-green-200';
  if (!isLeft && rightScore > leftScore) return 'bg-green-900 text-green-200';
  return '';
};

const getScoreClass = (score1, score2, isScore1) => {
  if (isScore1 && score1 > score2) return 'bg-green-900 text-green-200';
  if (!isScore1 && score2 > score1) return 'bg-green-900 text-green-200';
  return '';
};

const getRightMetricByName = (name) => {
  return aggregateData.rightSide.metrics.find(metric => metric.metric === name);
};
////////////////////

const CompareReport = () => {
  const [showAggregateTable, setShowAggregateTable] = useState(true); // make it expanded by defauדםראlt
  const [searchQuery, setSearchQuery] = useState('');
  const [metricTestFilter, setMetricTestFilter] = useState('');
  const [testCaseFilter, setTestCaseFilter] = useState('');
  const [minScoreDiff, setMinScoreDiff] = useState(0);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedPrompt, setSelectedPrompt] = useState(null);
  const [selectedExplanation, setSelectedExplanation] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  const [sortOrder, setSortOrder] = useState('asc');
  const [scoreSortOrder, setScoreSortOrder] = useState('asc');
  const [selectedExtraInfo, setSelectedExtraInfo] = useState(null);
  const [sortBy, setSortBy] = useState('metric'); // Track sorting type
  const [testcaseSortOrder, setTestcaseSortOrder] = useState('asc'); // Sorting order for Testcase:Test


  const handleSearchQueryChange = (e) => {
    setSearchQuery(e.target.value);
    setCurrentPage(1); // Reset page to 1 when searching
  };

  const handleMetricTestFilterChange = (e) => {
    setMetricTestFilter(e.target.value);
    setCurrentPage(1); // Reset page to 1 when filtering
  };

  const handleTestCaseFilterChange = (e) => {
    setTestCaseFilter(e.target.value);
    setCurrentPage(1); // Reset page to 1 when filtering
  };

  const handleMinScoreDiffChange = (e) => {
    setMinScoreDiff(parseFloat(e.target.value));
    setCurrentPage(1); // Reset page to 1 when filtering
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setMetricTestFilter('');
    setTestCaseFilter('');
    setMinScoreDiff(0);
    setCurrentPage(1); // Reset page to 1 when clearing filters
  };

  const handleSort = () => {
    setSortBy('metric');
    setSortOrder(prevOrder => (prevOrder === 'asc' ? 'desc' : 'asc'));
    setCurrentPage(1);
  };

  const handleScoreSort = () => {
    setSortBy('score');
    setScoreSortOrder(prevOrder => (prevOrder === 'asc' ? 'desc' : 'asc'));
    setCurrentPage(1);
  };

  const handleTestcaseSort = () => {
    setSortBy('testcase');
    setTestcaseSortOrder(prevOrder => (prevOrder === 'asc' ? 'desc' : 'asc'));
    setCurrentPage(1);
  };

  const filteredData = rowsData.filter(group => {
    const groupMatchesMetricTestFilter = !metricTestFilter || group.metric.toLowerCase().includes(metricTestFilter.toLowerCase());
    const filteredRows = group.rows.filter(item => {
      const matchesSearch =
        group.metric.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.testCaseTest.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.promptToLLM.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.llmResponse.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.expectedLLMResponse.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.evalResult.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.explanation.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (item.extraInfo && item.extraInfo.toLowerCase().includes(searchQuery.toLowerCase()));
      const matchesTestCase = item.testCaseTest.toLowerCase().includes(testCaseFilter.toLowerCase());
      const scoreDiff = Math.abs(item.normalizedScore - group.rows[0].normalizedScore);
      const matchesScoreDiff = scoreDiff >= minScoreDiff;
      return matchesSearch && matchesTestCase && matchesScoreDiff;
    });
    return groupMatchesMetricTestFilter && filteredRows.length > 0;
  });

  const sortedData = [...filteredData].sort((a, b) => {
    if (sortBy === 'metric') {
      return sortOrder === 'asc' ? a.metric.localeCompare(b.metric) : b.metric.localeCompare(a.metric);
    }
    if (sortBy === 'score') {
      const diffA = Math.abs(a.rows[0].normalizedScore - a.rows[1].normalizedScore);
      const diffB = Math.abs(b.rows[0].normalizedScore - b.rows[1].normalizedScore);
      return scoreSortOrder === 'asc' ? diffA - diffB : diffB - diffA;
    }
    if (sortBy === 'testcase') {
      // Extract the value after ":"
      const extractTestValue = (str) => str.split(':')[1] || str;
      const valA = extractTestValue(a.rows[0].testCaseTest);
      const valB = extractTestValue(b.rows[0].testCaseTest);
      return testcaseSortOrder === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
    }
    return 0;
  });

  const totalPages = Math.ceil(sortedData.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedData = sortedData.slice(startIndex, startIndex + itemsPerPage);

  return (
    <div className="p-6 max-w-7xl mx-auto bg-gray-900 text-gray-100 min-h-screen">
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
          <h1 className="text-2xl font-semibold text-gray-100">
            Comparison Report: <span className="bg-gray-700 text-gray-300 px-2 py-1 rounded">{evalSet}</span>
          </h1>
        </div>
        <h2 className="text-2xl font-semibold text-gray-100 mb-4">
          <span className="bg-gray-700 text-gray-300 px-2 py-1 rounded">{aggregateData.leftSide.testcase}</span> vs <span className="bg-gray-700 text-gray-300 px-2 py-1 rounded">{aggregateData.rightSide.testcase}</span>
        </h2>

        <div className="border border-gray-700 rounded-md overflow-hidden mb-4">
          <div className="bg-gray-800 px-6 py-3 flex justify-between items-center cursor-pointer" onClick={() => setShowAggregateTable(!showAggregateTable)}>
            <h2 className="text-xs font-medium text-gray-300 uppercase tracking-wider">Aggregate Data</h2>
            {showAggregateTable ? <ChevronUp className="h-5 w-5 text-gray-400" /> : <ChevronDown className="h-5 w-5 text-gray-400" />}
          </div>
          {showAggregateTable && (
            <table className="min-w-full divide-y divide-gray-700">
              <thead className="bg-gray-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Metric</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Score ({aggregateData.leftSide.testcase})</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Score ({aggregateData.rightSide.testcase})</th>
                </tr>
              </thead>
              <tbody className="bg-gray-800 divide-y divide-gray-700">
                {aggregateData.leftSide.metrics.map((leftItem) => {
                  const rightItem = getRightMetricByName(leftItem.metric);
                  return (
                    <tr key={leftItem.metric}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-100">{leftItem.metric}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getLabelClass(leftItem.score, rightItem.score, true)}`}>
                          {leftItem.score}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getLabelClass(leftItem.score, rightItem.score, false)}`}>
                          {rightItem.score}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>

        {/* Search and Filters */}
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search..."
                className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-md text-gray-100 placeholder-gray-400 focus:outline-none focus:border-blue-500"
                value={searchQuery}
                onChange={handleSearchQueryChange}
              />
            </div>
            <button
              data-testid="filter-toggle"
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-4 py-2 bg-gray-800 border border-gray-700 rounded-md hover:bg-gray-700 text-gray-100"
            >
              <Filter className="h-5 w-5" />
              <ChevronDown className="h-4 w-4" />
            </button>
          </div>

          {/* Filter Panel */}
          {showFilters && (
            <div className="p-4 bg-gray-800 border border-gray-700 rounded-md mb-4">
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-300">Metric</label>
                  <input
                    type="text"
                    placeholder="Filter by Metric"
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-100 placeholder-gray-400"
                    value={metricTestFilter}
                    onChange={handleMetricTestFilterChange}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-300">Testcase:Test</label>
                  <input
                    type="text"
                    placeholder="Filter by Testcase:Test"
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-100 placeholder-gray-400"
                    value={testCaseFilter}
                    onChange={handleTestCaseFilterChange}
                  />
                </div>
                <div className="flex items-end gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-300">Min Score Diff</label>
                    <input
                      type="number"
                      placeholder="Min (0)"
                      min="0"
                      max="1"
                      step="0.1"
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-100 placeholder-gray-400"
                      value={minScoreDiff}
                      onChange={handleMinScoreDiffChange}
                    />
                  </div>
                  <button
                    onClick={handleClearFilters}
                    className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md text-gray-100"
                  >
                    Clear
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="border border-gray-700 rounded-md overflow-hidden">
          <table className="min-w-full divide-y divide-gray-700">
            <thead className="bg-gray-800">
              <tr>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider cursor-pointer"
                  onClick={handleSort}
                >
                  <div className="flex items-center gap-1">
                    <span>Metric</span>
                    <span>{sortOrder === 'asc' ? '▲' : '▼'}</span>
                  </div>
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider cursor-pointer"
                  onClick={handleTestcaseSort}
                  title="Sort by test name"
                >
                  <div className="flex items-center gap-1">
                    <span>Testcase:Test</span>
                    <span>{testcaseSortOrder === 'asc' ? '▲' : '▼'}</span>
                  </div>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Prompt To LLM</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">LLM Response</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Expected Response</th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider cursor-pointer"
                  onClick={handleScoreSort}
                  title="Sort by scores diff"
                >
                  <div className="flex items-center gap-1">
                    <span>Score</span>
                    <span>{scoreSortOrder === 'asc' ? '▲' : '▼'}</span>
                  </div>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Eval Result</th>
              </tr>
            </thead>
            <tbody className="bg-gray-800 divide-y divide-gray-700">
              {paginatedData.map((group, index) => (
                <React.Fragment key={index}>
                  <tr className="bg-gray-700">
                    <td colSpan={7} className="px-6 py-3 font-semibold text-gray-200 text-sm uppercase">{group.metric}</td>
                  </tr>
                  {group.rows.map((item, subIndex) => (
                    <tr key={subIndex} className="hover:bg-gray-700">
                      <td className="px-6 py-4 text-sm text-gray-300"></td>
                      <td className="px-6 py-4 text-sm text-gray-300">
                        <div className="flex items-center">
                          {item.testCaseTest}
                          {item.extraInfo && (
                            <button
                              onClick={() => setSelectedExtraInfo(item.extraInfo)}
                              className="text-blue-400 hover:text-blue-300 underline ml-2"
                            >
                              ...
                            </button>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-300">
                        <button
                          onClick={() => setSelectedPrompt(item.promptToLLM)}
                          className="text-blue-400 hover:text-blue-300 underline"
                        >
                          show
                        </button>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-300">{item.llmResponse}</td>
                      <td className="px-6 py-4 text-sm text-gray-300">{item.expectedLLMResponse}</td>
                      <td className="px-6 py-4 text-sm text-gray-300">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getScoreClass(item.normalizedScore, group.rows[subIndex === 0 ? 1 : 0].normalizedScore, true)}`}>
                          {item.normalizedScore.toFixed(2)}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-300">
                        <button
                          onClick={() => setSelectedExplanation({ evalResult: item.evalResult, explanation: item.explanation })}
                          className="text-blue-400 hover:text-blue-300 underline"
                        >
                          show
                        </button>
                      </td>
                    </tr>
                  ))}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between mt-4 text-gray-300">
          <div className="text-sm">
            Showing {startIndex + 1} - {Math.min(startIndex + itemsPerPage, filteredData.length)} of {filteredData.length} items
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 border border-gray-700 rounded-md bg-gray-800 hover:bg-gray-700 disabled:opacity-50 disabled:hover:bg-gray-800"
            >
              Previous
            </button>
            <span className="px-3 py-1 border border-gray-700 rounded-md bg-gray-800">{currentPage}/{totalPages}</span>
            <button
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 border border-gray-700 rounded-md bg-gray-800 hover:bg-gray-700 disabled:opacity-50 disabled:hover:bg-gray-800"
            >
              Next
            </button>
          </div>
        </div>

        {/* Add popup for prompt */}
        {selectedPrompt && (
          <div className="fixed inset-0 bg-gray-50/25 flex items-center justify-center" onClick={() => setSelectedPrompt(null)}>
            <div className="bg-gray-800 p-6 rounded-lg w-1/3 max-h-[80vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
              <h3 className="text-lg font-semibold mb-4">Prompt To LLM</h3>
              <p className="text-gray-300 whitespace-pre-wrap">{selectedPrompt}</p>
              <button
                onClick={() => setSelectedPrompt(null)}
                className="mt-4 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md"
              >
                Close
              </button>
            </div>
          </div>
        )}

        {/* Add popup */}
        {selectedExplanation && (
          <div className="fixed inset-0 bg-gray-50/25 flex items-center justify-center" onClick={() => setSelectedExplanation(null)}>
            <div className="bg-gray-800 p-6 rounded-lg w-1/3 max-h-[80vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
              <h3 className="text-lg font-semibold mb-4">Eval Result</h3>
              <p className="text-gray-300"><strong>Eval result:</strong></p>
              <p className="text-gray-300 whitespace-pre-wrap">{selectedExplanation.evalResult}</p>
              <br />
              <p className="text-gray-300"><strong>Explanation:</strong></p>
              <p className="text-gray-300 whitespace-pre-wrap">{selectedExplanation.explanation}</p>
              <button
                onClick={() => setSelectedExplanation(null)}
                className="mt-4 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md"
              >
                Close
              </button>
            </div>
          </div>
        )}

        {/* Add popup for extraInfo */}
        {selectedExtraInfo && (
          <div className="fixed inset-0 bg-gray-50/25 flex items-center justify-center" onClick={() => setSelectedExtraInfo(null)}>
            <div className="bg-gray-800 p-6 rounded-lg w-1/3 max-h-[80vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
              <h3 className="text-lg font-semibold mb-4">Extra Info</h3>
              <p className="text-gray-300 whitespace-pre-wrap">{selectedExtraInfo}</p>
              <button
                onClick={() => setSelectedExtraInfo(null)}
                className="mt-4 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md"
              >
                Close
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default CompareReport;
