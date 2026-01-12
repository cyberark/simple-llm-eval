import React, { useState } from 'react';
import { Search, Filter, ChevronDown, ChevronUp } from 'lucide-react';

const RED_LABEL_THRESHOLD = 0.3;
const YELLOW_LABEL_THRESHOLD = 0.7;

////////   Mock Data  ////////

const evalNameTestCase = "Eval set name: testcase-name";

const rowsData = [
  { id: 1, testName: "Basic Greeting Test", promptToLLM: "Say hello to the user", llmResponse: "Hello! How can I help you today?", expectedLLMResponse: "Hello! How can I assist you?", evalResult: "PASS", normalizedScore: 0.95, scoreExplanation: "Response matches expected greeting with minor variations", extraInfo: "Hi there, i'm extra info!" },
  { id: 2, testName: "Math Calculation", promptToLLM: "What is 2+2?", llmResponse: "The sum of 2 and 2 is 4", expectedLLMResponse: "4", evalResult: "PARTIAL", normalizedScore: 0.6, scoreExplanation: "Answer is correct but includes unnecessary verbosity" },
  { id: 3, testName: "Weather Inquiry", promptToLLM: "What's the weather like today?", llmResponse: "It's sunny and warm.", expectedLLMResponse: "It's sunny and warm.", evalResult: "PASS", normalizedScore: 0.20, scoreExplanation: "Perfect match with expected response" },
  { id: 4, testName: "Advanced Math Calculation", promptToLLM: "What is the square root of 16?", llmResponse: "The square root of 16 is 4", expectedLLMResponse: "4", evalResult: "PASS", normalizedScore: 0.9, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 5, testName: "Historical Fact", promptToLLM: "Who was the first president of the United States?", llmResponse: "George Washington was the first president of the United States.", expectedLLMResponse: "George Washington", evalResult: "PASS", normalizedScore: 0.85, scoreExplanation: "Correct answer with additional context" },
  { id: 6, testName: "Simple Addition", promptToLLM: "Add 5 and 3.", llmResponse: "5 plus 3 equals 8", expectedLLMResponse: "8", evalResult: "PASS", normalizedScore: 0.75, scoreExplanation: "Correct answer with unnecessary verbosity" },
  { id: 7, testName: "Capital City", promptToLLM: "What is the capital of France?", llmResponse: "The capital of France is Paris.", expectedLLMResponse: "Paris", evalResult: "PASS", normalizedScore: 0.95, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 8, testName: "Basic Subtraction", promptToLLM: "Subtract 2 from 10.", llmResponse: "10 minus 2 is 8", expectedLLMResponse: "8", evalResult: "PASS", normalizedScore: 0.8, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 9, testName: "Science Fact", promptToLLM: "What is the chemical symbol for water?", llmResponse: "The chemical symbol for water is H2O.", expectedLLMResponse: "H2O", evalResult: "PASS", normalizedScore: 0.9, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 10, testName: "Basic Multiplication", promptToLLM: "Multiply 4 by 3.", llmResponse: "4 times 3 is 12", expectedLLMResponse: "12", evalResult: "PASS", normalizedScore: 0.85, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 11, testName: "Geography Fact", promptToLLM: "What is the largest ocean on Earth?", llmResponse: "The largest ocean on Earth is the Pacific Ocean.", expectedLLMResponse: "Pacific Ocean", evalResult: "PASS", normalizedScore: 0.9, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 12, testName: "Basic Division", promptToLLM: "Divide 20 by 4.", llmResponse: "20 divided by 4 equals 5", expectedLLMResponse: "5", evalResult: "PASS", normalizedScore: 0.8, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 13, testName: "Historical Date", promptToLLM: "In what year did the Titanic sink?", llmResponse: "The Titanic sank in 1912.", expectedLLMResponse: "1912", evalResult: "PASS", normalizedScore: 1.00, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 14, testName: "Basic Algebra", promptToLLM: "Solve for x: 2x = 10.", llmResponse: "x equals 5", expectedLLMResponse: "5", evalResult: "PASS", normalizedScore: 0.85, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 15, testName: "Animal Fact", promptToLLM: "What is the fastest land animal?", llmResponse: "The fastest land animal is the cheetah.", expectedLLMResponse: "cheetah", evalResult: "PASS", normalizedScore: 0.9, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 16, testName: "Basic Geometry", promptToLLM: "What is the area of a circle with radius 3?", llmResponse: "The area of a circle with radius 3 is 28.27", expectedLLMResponse: "28.27", evalResult: "PASS", normalizedScore: 0.8, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 17, testName: "Literature Fact", promptToLLM: "Who wrote 'To Kill a Mockingbird'?", llmResponse: "Harper Lee wrote 'To Kill a Mockingbird'.", expectedLLMResponse: "Harper Lee", evalResult: "PASS", normalizedScore: 0.95, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 18, testName: "Basic Trigonometry", promptToLLM: "What is the sine of 90 degrees?", llmResponse: "The sine of 90 degrees is 1", expectedLLMResponse: "1", evalResult: "PASS", normalizedScore: 0.9, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 19, testName: "Geography Fact", promptToLLM: "What is the longest river in the world?", llmResponse: "The longest river in the world is the Nile River.", expectedLLMResponse: "Nile River", evalResult: "PASS", normalizedScore: 0.85, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 20, testName: "Basic Physics", promptToLLM: "What is the acceleration due to gravity on Earth?", llmResponse: "The acceleration due to gravity on Earth is 9.8 m/s².", expectedLLMResponse: "9.8 m/s²", evalResult: "PASS", normalizedScore: 0.9, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 21, testName: "Historical Figure", promptToLLM: "Who was the first man to walk on the moon?", llmResponse: "Neil Armstrong was the first man to walk on the moon.", expectedLLMResponse: "Neil Armstrong", evalResult: "PASS", normalizedScore: 0.95, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 22, testName: "Basic Chemistry", promptToLLM: "What is the atomic number of hydrogen?", llmResponse: "The atomic number of hydrogen is 1.", expectedLLMResponse: "1", evalResult: "PASS", normalizedScore: 0.9, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 23, testName: "Geography Fact", promptToLLM: "What is the smallest country in the world?", llmResponse: "The smallest country in the world is Vatican City.", expectedLLMResponse: "Vatican City", evalResult: "PASS", normalizedScore: 0.85, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 24, testName: "Basic Biology", promptToLLM: "What is the powerhouse of the cell?", llmResponse: "The powerhouse of the cell is the mitochondrion.", expectedLLMResponse: "mitochondrion", evalResult: "PASS", normalizedScore: 0.9, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 25, testName: "Basic Logic", promptToLLM: "Is 5 greater than 3?", llmResponse: "Yes, 5 is greater than 3.", expectedLLMResponse: "Yes", evalResult: "PASS", normalizedScore: 0.9, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 26, testName: "Basic Fact", promptToLLM: "What color is the sky?", llmResponse: "The sky is blue.", expectedLLMResponse: "Blue", evalResult: "PASS", normalizedScore: 0.85, scoreExplanation: "Correct answer with additional context" },
  { id: 27, testName: "Basic History", promptToLLM: "Who discovered America?", llmResponse: "Christopher Columbus discovered America.", expectedLLMResponse: "Christopher Columbus", evalResult: "PASS", normalizedScore: 0.9, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 28, testName: "Basic Science", promptToLLM: "What is the boiling point of water?", llmResponse: "The boiling point of water is 100 degrees Celsius.", expectedLLMResponse: "100 degrees Celsius", evalResult: "PASS", normalizedScore: 0.9, scoreExplanation: "Correct answer with minor verbosity" },
  { id: 29, testName: "Basic Geography", promptToLLM: "What is the capital of Japan?", llmResponse: "The capital of Japan is Tokyo.", expectedLLMResponse: "Tokyo", evalResult: "PASS", normalizedScore: 0.95, scoreExplanation: "Correct answer with minor verbosity" },
];

const aggregateData = {
  correctness: [0.2, 0.5],
  fluency: [0.7, 0.8],
  aggregateScore: [0.9, 0.99],
}

const errors = {
  llmErrors: 0,
  evalErrors: 0,
}


//////////////////////////////////////////////////


const getLabelClass = (score) => {
  if (score <= RED_LABEL_THRESHOLD) return 'bg-red-900 text-red-200';
  if (score <= YELLOW_LABEL_THRESHOLD) return 'bg-yellow-900 text-yellow-200';
  return 'bg-green-900 text-green-200';
};

const LLMEvalReport = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [scoreFilter, setScoreFilter] = useState({ min: '', max: '' });
  const [nameFilter, setNameFilter] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedExplanation, setSelectedExplanation] = useState(null);
  const [selectedPrompt, setSelectedPrompt] = useState(null);
  const [sortConfig, setSortConfig] = useState({ key: '', direction: '' });
  const [showAggregateTable, setShowAggregateTable] = useState(false);
  const [selectedExtraInfo, setSelectedExtraInfo] = useState(null);
  const itemsPerPage = 25;

  const handleClearFilters = () => {
    setSearchQuery('');
    setScoreFilter({ min: '', max: '' });
    setNameFilter('');
    setCurrentPage(1); // Reset to first page
  };

  const handleSearchQueryChange = (e) => {
    setSearchQuery(e.target.value);
    setCurrentPage(1); // Reset to first page
  };

  const handleScoreFilterChange = (key, value) => {
    setScoreFilter(prev => ({ ...prev, [key]: value }));
    setCurrentPage(1); // Reset to first page
  };

  const handleNameFilterChange = (e) => {
    setNameFilter(e.target.value);
    setCurrentPage(1); // Reset to first page
  };

  const handleSort = (key) => {
    let direction = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  const filteredData = rowsData.filter(item => {
    const matchesSearch = Object.values(item).some(value =>
      value.toString().toLowerCase().includes(searchQuery.toLowerCase())
    );
    const matchesScore = (!scoreFilter.min || item.normalizedScore >= parseFloat(scoreFilter.min)) &&
                         (!scoreFilter.max || item.normalizedScore <= parseFloat(scoreFilter.max));
    const matchesName = !nameFilter || item.testName.toLowerCase().includes(nameFilter.toLowerCase());
    return matchesSearch && matchesScore && matchesName;
  });

  const sortedData = [...filteredData].sort((a, b) => {
    if (a[sortConfig.key] < b[sortConfig.key]) {
      return sortConfig.direction === 'ascending' ? -1 : 1;
    }
    if (a[sortConfig.key] > b[sortConfig.key]) {
      return sortConfig.direction === 'ascending' ? 1 : -1;
    }
    return 0;
  });

  const totalPages = Math.ceil(filteredData.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedData = sortedData.slice(startIndex, startIndex + itemsPerPage);

  const handleScoreClick = (explanation) => {
    setSelectedExplanation(explanation);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto bg-gray-900 text-gray-100 min-h-screen">
      <div className={`bg-yellow-500 text-yellow-900 p-4 mb-4 rounded-md ${errors.llmErrors === 0 && errors.evalErrors === 0 ? 'hidden' :''}`}>
        LLM Task Errors: {errors.llmErrors}, Eval Errors: {errors.evalErrors}
      </div>
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
          <h1 className="text-2xl font-semibold text-gray-100">LLM Evaluation Report</h1>
        </div>
        <h2 className="text-2xl font-semibold text-gray-100 mb-4">
          <span className="bg-gray-700 text-gray-300 px-2 py-1 rounded">{evalNameTestCase}</span>
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
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Value</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Standard Deviation</th>
                </tr>
              </thead>
              <tbody className="bg-gray-800 divide-y divide-gray-700">
                {Object.entries(aggregateData).map(([key, value]) => (
                  <tr key={key}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-100">
                      {key.charAt(0).toUpperCase() + key.slice(1)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getLabelClass(value[0])}`}>
                        {value[0]}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-100">
                      {value[1]}
                    </td>
                  </tr>
                ))}
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
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-300">Normalized Score Range</label>
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      placeholder="Min (0)"
                      min="0"
                      max="1"
                      step="0.1"
                      className="w-24 px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-100 placeholder-gray-400"
                      value={scoreFilter.min}
                      onChange={(e) => handleScoreFilterChange('min', e.target.value)}
                    />
                    <span className="text-gray-400">to</span>
                    <input
                      type="number"
                      placeholder="Max (1)"
                      min="0"
                      max="1"
                      step="0.1"
                      className="w-24 px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-100 placeholder-gray-400"
                      value={scoreFilter.max}
                      onChange={(e) => handleScoreFilterChange('max', e.target.value)}
                    />
                  </div>
                </div>
                <div className="flex items-end gap-2">
                  <div className="flex-1">
                    <label className="block text-sm font-medium mb-1 text-gray-300">Test Name</label>
                    <input
                      type="text"
                      placeholder="Filter by test name"
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-100 placeholder-gray-400"
                      value={nameFilter}
                      onChange={handleNameFilterChange}
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('testName')}>
                  Test Name
                  <span className="ml-1">{sortConfig.key === 'testName' ? (sortConfig.direction === 'ascending' ? '▲' : '▼') : '•'}</span>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Prompt To LLM</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">LLM Response</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Expected LLM Response</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Eval Result</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('normalizedScore')}>
                  Normalized Score
                  <span className="ml-1">{sortConfig.key === 'normalizedScore' ? (sortConfig.direction === 'ascending' ? '▲' : '▼') : '•'}</span>
                </th>
              </tr>
            </thead>
            <tbody className="bg-gray-800 divide-y divide-gray-700">
              {paginatedData.map((item) => (
                <tr key={item.id} className="hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-100">
                    {item.testName}
                    {item.extraInfo && (
                      <button
                        onClick={() => setSelectedExtraInfo(item.extraInfo)}
                        className="text-blue-400 hover:text-blue-300 underline ml-2"
                      >
                        ...
                      </button>
                    )}
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
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      item.normalizedScore <= RED_LABEL_THRESHOLD ? 'bg-red-900 text-red-200' :
                      item.normalizedScore <= YELLOW_LABEL_THRESHOLD ? 'bg-yellow-900 text-yellow-200' :
                      'bg-green-900 text-green-200'
                    }`}>
                      {item.evalResult}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    <button
                      onClick={() => handleScoreClick(item.scoreExplanation)}
                      className="text-blue-400 hover:text-blue-300 underline"
                    >
                      {item.normalizedScore.toFixed(2)}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
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
              <h3 className="text-lg font-semibold mb-4">Score Explanation</h3>
              <p className="text-gray-300 whitespace-pre-wrap">{selectedExplanation}</p>
              <button
                onClick={() => setSelectedExplanation(null)}
                className="mt-4 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md"
              >
                Close
              </button>
            </div>
          </div>
        )}

        {/* Add popup for extra info */}
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
      </div>
    </div>
  );
};

export default LLMEvalReport;
