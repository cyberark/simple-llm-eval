import React from "react";
import "@testing-library/jest-dom";
import { render, screen, fireEvent, within } from "@testing-library/react";
import { describe, it, beforeEach } from "vitest";
import LLMEvalReport from "../components/LLMEvalReport";

// Helper function to render component before each test
beforeEach(() => {
  render(<LLMEvalReport />);
});

describe("LLMEvalReport Component", () => {
  it("renders the component correctly", () => {
    expect(screen.getByText("LLM Evaluation Report")).toBeInTheDocument();
  });

  it("renders table headers", () => {
    expect(screen.getByText("Test Name")).toBeInTheDocument();
    expect(screen.getByText("Prompt To LLM")).toBeInTheDocument();
    expect(screen.getByText("LLM Response")).toBeInTheDocument();
    expect(screen.getByText("Expected LLM Response")).toBeInTheDocument();
    expect(screen.getByText("Eval Result")).toBeInTheDocument();
  });

  it("allows searching by test name", () => {
    const searchInput = screen.getByPlaceholderText("Search...");
    fireEvent.change(searchInput, { target: { value: "Math" } });
    const results = screen.getAllByText("Math Calculation");
    expect(results).toHaveLength(1);
  });

  it("allows searching by Prompt To LLM", () => {
    const searchInput = screen.getByPlaceholderText("Search...");
    fireEvent.change(searchInput, { target: { value: "2+2" } });
    const results = screen.getAllByText("Math Calculation");
    expect(results).toHaveLength(1);
  });

  it("allows searching by LLM Response", () => {
    const searchInput = screen.getByPlaceholderText("Search...");
    fireEvent.change(searchInput, { target: { value: "warm" } });
    const results = screen.getAllByText("Weather Inquiry");
    expect(results).toHaveLength(1);
  });

  it("allows searching by Expected LLM Response", () => {
    const searchInput = screen.getByPlaceholderText("Search...");
    fireEvent.change(searchInput, { target: { value: "How can I assist you" } });
    const results = screen.getAllByText("Hello! How can I assist you?");
    expect(results).toHaveLength(1);
  });

  it("allows searching by Eval Result", () => {
    const searchInput = screen.getByPlaceholderText("Search...");
    fireEvent.change(searchInput, { target: { value: "partial" } });
    const results = screen.getAllByText("PARTIAL");
    expect(results).toHaveLength(1);
  });

  it("allows searching by Normalized Score", () => {
    const searchInput = screen.getByPlaceholderText("Search...");
    fireEvent.change(searchInput, { target: { value: "0.95" } });
    const results = screen.getAllByText("0.95");
    expect(results).toHaveLength(5);
  });

  it("toggles filter visibility", () => {
    const filterButton = screen.getByTestId('filter-toggle');
    fireEvent.click(filterButton);
    expect(screen.getByText(/normalized score range/i)).toBeInTheDocument();
  });

  it("renders the aggregate data table headers", () => {
    const aggregateDataButton = screen.getByText("Aggregate Data");
    fireEvent.click(aggregateDataButton);
    expect(screen.getByText("Metric")).toBeInTheDocument();
    expect(screen.getByText("Value")).toBeInTheDocument();
    expect(screen.getByText("Standard Deviation")).toBeInTheDocument();
  });

  it("shows the correct number of paginated items", () => {
    const paginationText = screen.getByText(/showing/i);
    expect(paginationText).toBeInTheDocument();
  });

  it("opens the explanation modal when clicking on a score", () => {
    const scoreButton = screen.getAllByText(/0.95|0.6|0.2/)[0];
    fireEvent.click(scoreButton);
    expect(screen.getByText("Score Explanation")).toBeInTheDocument();
  });

  it("closes the explanation modal when clicking close", () => {
    const scoreButton = screen.getAllByText(/0.95|0.6|0.2/)[0];
    fireEvent.click(scoreButton);
    fireEvent.click(screen.getByText("Close"));
    expect(screen.queryByText("Score Explanation")).not.toBeInTheDocument();
  });

  it("verifies aggregate table values and color labels", () => {
    const aggregateDataButton = screen.getByText("Aggregate Data");
    fireEvent.click(aggregateDataButton);

    const aggregateData = {
      correctness: [0.2, 0.5],
      fluency: [0.7, 0.8],
      aggregateScore: [0.9, 0.99],
    };

    Object.entries(aggregateData).forEach(([metric, [value, stdDev]]) => {
      expect(screen.getByText(metric.charAt(0).toUpperCase() + metric.slice(1))).toBeInTheDocument();
      expect(screen.getByText(value.toString())).toBeInTheDocument();
      expect(screen.getByText(stdDev.toString())).toBeInTheDocument();

      const valueElement = screen.getByText(value.toString());
      if (value <= 0.3) {
        expect(valueElement).toHaveClass('bg-red-900 text-red-200');
      } else if (value <= 0.7) {
        expect(valueElement).toHaveClass('bg-yellow-900 text-yellow-200');
      } else {
        expect(valueElement).toHaveClass('bg-green-900 text-green-200');
      }
    });
  });

  it("filters by test name", () => {
    const filterButton = screen.getByTestId('filter-toggle');
    fireEvent.click(filterButton);
    const nameFilterInput = screen.getByPlaceholderText("Filter by test name");
    fireEvent.change(nameFilterInput, { target: { value: "Math" } });
    const results = screen.getAllByText("Math Calculation");
    expect(results).toHaveLength(1);
  });

  it("filters by score", () => {
    const filterButton = screen.getByTestId('filter-toggle');
    fireEvent.click(filterButton);
    const minFilterInput = screen.getByPlaceholderText("Min (0)");
    const maxFilterInput = screen.getByPlaceholderText("Max (1)");

    fireEvent.change(minFilterInput, { target: { value: "0.5" } });
    fireEvent.change(maxFilterInput, { target: { value: "0.7" } });
    const results = screen.getAllByText("Math Calculation");
    expect(results).toHaveLength(1);
  });

  it("filters all, clear", () => {
    const filterButton = screen.getByTestId('filter-toggle');
    fireEvent.click(filterButton);

    const minFilterInput = screen.getByPlaceholderText("Min (0)");
    const maxFilterInput = screen.getByPlaceholderText("Max (1)");

    fireEvent.change(minFilterInput, { target: { value: "0.5" } });
    fireEvent.change(maxFilterInput, { target: { value: "0.7" } });

    const nameFilterInput = screen.getByPlaceholderText("Filter by test name");
    fireEvent.change(nameFilterInput, { target: { value: "Weather Inquiry" } });

    // Select the table body
    const tableBody = screen.getByRole('table').querySelector('tbody');

    // Ensure there are no rows
    expect(within(tableBody).queryAllByRole('row')).toHaveLength(0);

    // Click on clear button
    const clearButton = screen.getByText("Clear");
    fireEvent.click(clearButton);

    // Ensure there are two rows now
    expect(within(tableBody).queryAllByRole('row')).toHaveLength(25);
});

  const promptToLLMValues = [
    "Say hello to the user",
    "What is 2+2?",
    "What's the weather like today?"
  ];

  const scoreExplanations = [
    "Response matches expected greeting with minor variations",
    "Answer is correct but includes unnecessary verbosity",
    "Perfect match with expected response"
  ];

  promptToLLMValues.forEach((prompt, index) => {
    it(`shows the content of 'Prompt To LLM' when clicking the show link in row ${index + 1}`, () => {
      const showLink = screen.getAllByText("show")[index];
      fireEvent.click(showLink);
      expect(screen.getByText(prompt)).toBeInTheDocument();
    });
  });

  scoreExplanations.forEach((explanation, index) => {
    it(`shows the content of explanation when clicking the normalized score link in row ${index + 1}`, () => {
      const scoreLink = screen.getAllByText(/0.95|0.6|0.2/)[index];
      fireEvent.click(scoreLink);
      expect(screen.getByText(explanation)).toBeInTheDocument();
    });
  });

  it("renders the error banner correctly", () => {
    const errorBanner = screen.getByText(/LLM Task Errors:/).closest('div');
    try {
      expect(errorBanner).toHaveClass('bg-yellow-500 text-yellow-900 p-4 mb-4 rounded-md');
    } catch (error) {
      console.error("simleval depends on this banner value to hide it.");
      throw error;
    }
  });

  it("handles pagination correctly", () => {
    // Check initial page
    expect(screen.getByText("Showing 1 - 25 of 29 items")).toBeInTheDocument();
    expect(screen.getByText("1/2")).toBeInTheDocument();

    // Get all rows and verify first row content
    const rows = screen.getAllByRole('row');
    expect(within(rows[1]).getByText("Basic Greeting Test")).toBeInTheDocument(); // First row after header
    expect(rows).toHaveLength(26);

    // Find and click next page button
    const nextButton = screen.getByText("Next");
    fireEvent.click(nextButton);

    // Verify page number updated
    expect(screen.getByText("Showing 26 - 29 of 29 items")).toBeInTheDocument();
    expect(screen.getByText("2/2")).toBeInTheDocument();

    const rows2 = screen.getAllByRole('row');
    expect(within(rows2[1]).getByText("Basic Fact")).toBeInTheDocument();
    expect(rows2).toHaveLength(5);

    const prevButton = screen.getByText("Previous");
    fireEvent.click(prevButton);

    expect(screen.getByText("Showing 1 - 25 of 29 items")).toBeInTheDocument();
    expect(screen.getByText("1/2")).toBeInTheDocument();

    expect(screen.getAllByRole('row')).toHaveLength(26);

  });

  it("sort by test name", () => {
    const rows = screen.getAllByRole('row');
    expect(within(rows[1]).getByText("Basic Greeting Test")).toBeInTheDocument();

    const sortButton = screen.getByText('Test Name');
    fireEvent.click(sortButton);

    const rows2 = screen.getAllByRole('row');
    expect(within(rows2[1]).getByText("Advanced Math Calculation")).toBeInTheDocument();

    fireEvent.click(sortButton);
    const rows3 = screen.getAllByRole('row');
    expect(within(rows3[1]).getByText("Weather Inquiry")).toBeInTheDocument();
  });

  it("sort by score", () => {
    const rows = screen.getAllByRole('row');
    expect(within(rows[1]).getByText("0.95")).toBeInTheDocument();

    const sortButton = screen.getByText('Normalized Score');
    fireEvent.click(sortButton);

    const rows2 = screen.getAllByRole('row');
    expect(within(rows2[1]).getByText("0.20")).toBeInTheDocument();

    fireEvent.click(sortButton);
    const rows3 = screen.getAllByRole('row');
    expect(within(rows3[1]).getByText("1.00")).toBeInTheDocument();
  });

  it("prompt popup has scrollable container for long text", () => {
    const showLink = screen.getAllByText("show")[0];
    fireEvent.click(showLink);
    
    // Find the popup by the h3 heading element which is unique to the popup
    const popupHeading = screen.getByRole('heading', { name: 'Prompt To LLM' });
    const popupContainer = popupHeading.closest('div');
    expect(popupContainer).toHaveClass('max-h-[80vh]', 'overflow-y-auto');
  });

  it("score explanation popup has scrollable container for long text", () => {
    const scoreButton = screen.getAllByText(/0.95|0.6|0.2/)[0];
    fireEvent.click(scoreButton);
    
    const popupHeading = screen.getByRole('heading', { name: 'Score Explanation' });
    const popupContainer = popupHeading.closest('div');
    expect(popupContainer).toHaveClass('max-h-[80vh]', 'overflow-y-auto');
  });

});
