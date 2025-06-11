import React from "react";
import "@testing-library/jest-dom";
import { render, screen, fireEvent, within } from "@testing-library/react";
import { describe, it, beforeEach, expect } from "vitest";
import CompareReport from "../components/CompareReport";


// Helper function to render component before each test
beforeEach(() => {
  render(<CompareReport />);
});

describe("CompareReport Component", () => {

  it("renders the component correctly", () => {
    expect(screen.getByText("Comparison Report:")).toBeInTheDocument();
    expect(screen.getByText("EVAL-SET-PLACEHOLDER")).toBeInTheDocument();
  });

  it("renders the aggregate data table correctly", () => {
    const aggregateData = [
      { metric: "completeness", leftScore: 0.21, rightScore: 0.92 },
      { metric: "correctness", leftScore: 0.91, rightScore: 0.42 },
      { metric: "relevance", leftScore: 0.51, rightScore: 0.62 },
      { metric: "aggregate mean", leftScore: 0.31, rightScore: 0.72 },
    ];

    const rows = screen.getAllByRole("row");

    aggregateData.forEach(({ metric, leftScore, rightScore }) => {
      let found = false;
      rows.forEach((row) => {
        if (found) return;
        const rowWithin = within(row);
        if (rowWithin.queryByText(metric)) {
          found = true;
          const cells = row.querySelectorAll("td");
          expect(cells.length).toBe(3); // Ensure correct number of columns (Metric, Left Score, Right Score)
          expect(cells[1]).toHaveTextContent(leftScore.toString());
          expect(cells[2]).toHaveTextContent(rightScore.toString());

          const leftScoreSpan = cells[1].querySelector("span");
          const rightScoreSpan = cells[2].querySelector("span");

          if (leftScore > rightScore) {
            expect(leftScoreSpan).toHaveClass("bg-green-900 text-green-200");
          } else if (rightScore > leftScore) {
            expect(rightScoreSpan).toHaveClass("bg-green-900 text-green-200");
          }
        }
      });
      expect(found).toBe(true);
    });
  });

  it("marks the higher score with a green label", () => {
    const rows = screen.getAllByRole("row");
    rows.forEach((row, index) => {
      if (index === 0) return; // Skip header row
      const cells = row.querySelectorAll("td");
      if (cells.length === 3) { // Ensure it's a data row
        const leftScore = parseFloat(cells[1].textContent);
        const rightScore = parseFloat(cells[2].textContent);
        const leftScoreSpan = cells[1].querySelector("span");
        const rightScoreSpan = cells[2].querySelector("span");

        if (leftScore > rightScore) {
          expect(leftScoreSpan).toHaveClass("bg-green-900 text-green-200");
        } else if (rightScore > leftScore) {
          expect(rightScoreSpan).toHaveClass("bg-green-900 text-green-200");
        }
        else {
          expect(leftScoreSpan).not.toHaveClass("bg-green-900 text-green-200");
        }
      }
    });
  });

  it("allows searching by test name", () => {
    const searchInput = screen.getByPlaceholderText("Search...");
    fireEvent.change(searchInput, { target: { value: "testcase1:test1" } });
    const results = screen.getAllByText("testcase1:test1");
    expect(results).toHaveLength(3);

    const results2 = screen.getAllByText("testcase2:test1");
    expect(results2).toHaveLength(3);
  });


  it("allows searching by metric", () => {
    const searchInput = screen.getByPlaceholderText("Search...");
    fireEvent.change(searchInput, { target: { value: "Correctness" } });
    const results = screen.getAllByText("correctness");
    expect(results).toHaveLength(5);
  });

  it("allows searching by eval result", () => {
    const searchInput = screen.getByPlaceholderText("Search...");
    fireEvent.change(searchInput, { target: { value: "The response was mostly correct with minor inaccuracies. 2:1" } });
    const results = screen.getAllByText("testcase1:test1");
    expect(results).toHaveLength(1);

    const results2 = screen.getAllByText("testcase2:test1");
    expect(results2).toHaveLength(1);
  });

  it("allows searching by llm response", () => {
    const searchInput = screen.getByPlaceholderText("Search...");
    fireEvent.change(searchInput, { target: { value: "The user clicked on the 'EC2' icon in the taskbar. 1:1" } });
    const results = screen.getAllByText("testcase1:test1");
    expect(results).toHaveLength(2);

    const results2 = screen.getAllByText("testcase2:test1");
    expect(results2).toHaveLength(2);
  });

  it("allows searching by expected response", () => {
    const searchInput = screen.getByPlaceholderText("Search...");
    fireEvent.change(searchInput, { target: { value: "The user clicked the EC2 Microsoft Window Icon 1:1" } });
    const results = screen.getAllByText("testcase1:test1");
    expect(results).toHaveLength(2);

    const results2 = screen.getAllByText("testcase2:test1");
    expect(results2).toHaveLength(2);
  });

  it("allows searching by eval result", () => {
    const searchInput = screen.getByPlaceholderText("Search...");
    fireEvent.change(searchInput, { target: { value: "prompt to llm test1 1:1" } });
    const results = screen.getAllByText("testcase1:test1");
    expect(results).toHaveLength(1);

    const results2 = screen.getAllByText("testcase2:test1");
    expect(results2).toHaveLength(1);
  });

  it("checks the first two 'show' elements", () => {
    const showElements = screen.getAllByText("show");
    expect(showElements.length).toBeGreaterThanOrEqual(2);

    fireEvent.click(showElements[0]);
    expect(screen.getByText("prompt to llm test1 1:1")).toBeInTheDocument();

    fireEvent.click(showElements[1]);
    expect(screen.getByText("The response was somewhat accurate but missed some key details. 1:1")).toBeInTheDocument();

  });

  it("filters by metric correctly", () => {
    const filterButton = screen.getByTestId('filter-toggle');
    fireEvent.click(filterButton);

    const metricFilterInput = screen.getByPlaceholderText("Filter by Metric");
    fireEvent.change(metricFilterInput, { target: { value: "correctness" } });

    const rows = screen.getAllByRole("row");
    rows.slice(6).forEach((row, index) => {
      if (index % 3 === 0) { // Check every third row (1st, 4th, etc.)
        expect(row.textContent).toContain("correctness");
      }
    });
  });

  it("filters by test name correctly", () => {
    const filterButton = screen.getByTestId('filter-toggle');
    fireEvent.click(filterButton);

    const metricFilterInput = screen.getByPlaceholderText("Filter by Testcase:Test");
    fireEvent.change(metricFilterInput, { target: { value: "test4" } });

    const rows = screen.getAllByRole("row");
    rows.slice(7).forEach((row, index) => {
      // console.log(index);
      // console.log(row.textContent);

      if ((index) % 3 === 0) {
        expect(row.textContent).toContain("testcase1:test4");
      }
      else if ((index) % 4 === 0) {
        expect(row.textContent).toContain("testcase2:test4");
      }
    });
  });

  it("filters by min score diff", () => {
    const filterButton = screen.getByTestId('filter-toggle');
    fireEvent.click(filterButton);

    const metricFilterInput = screen.getByPlaceholderText("Min (0)");
    fireEvent.change(metricFilterInput, { target: { value: "1" } });

    const rows = screen.getAllByRole("row");
    rows.slice(6).forEach((row) => {
      const cells = row.querySelectorAll("td");
      if (cells.length === 3) { // Check only score rows
        const leftScore = parseFloat(cells[1].textContent);
        const rightScore = parseFloat(cells[2].textContent);
        const scoreDiff = Math.abs(leftScore - rightScore);
        expect(scoreDiff).toBe(1.0);
        expect([0.0, 1.0]).toContain(leftScore);
        expect([0.0, 1.0]).toContain(rightScore);
      }
    });
  });

  it("handles pagination correctly", () => {
    // Check initial page
    expect(screen.getByText("Showing 1 - 10 of 12 items")).toBeInTheDocument();
    expect(screen.getByText("1/2")).toBeInTheDocument();

    // Find and click next page button
    const nextButton = screen.getByText("Next");
    fireEvent.click(nextButton);

    // Verify page number updated
    expect(screen.getByText("Showing 11 - 12 of 12 items")).toBeInTheDocument();
    expect(screen.getByText("2/2")).toBeInTheDocument();

    // Verify content changed
    const rows = screen.getAllByRole("row");
    const firstRowOnSecondPage = rows[7]; // First data row after header and aggregate rows
    expect(firstRowOnSecondPage).toHaveTextContent("testcase1:test3");
    expect(rows.length).toBe(12);

    const prevButton = screen.getByText("Previous");
    fireEvent.click(prevButton);

    expect(screen.getByText("Showing 1 - 10 of 12 items")).toBeInTheDocument();
    expect(screen.getByText("1/2")).toBeInTheDocument();

    expect(screen.getAllByRole("row").length).toBe(36);

  });

  it("sorts by metric correctly", () => {
    const rows = screen.getAllByRole("row");
    expect(rows[6]).toHaveTextContent("completeness");

    // Find and click the metric sort button - get the second Metric header
    const metricHeaders = screen.getAllByText("Metric");
    fireEvent.click(metricHeaders[1].closest('th'));

    // Get rows after sorting
    const sortedRows = screen.getAllByRole("row");
    expect(sortedRows[6]).toHaveTextContent("relevance");
  });

  it("sorts by testcase:test correctly", () => {
    const rows = screen.getAllByRole("row");
    expect(rows[7]).toHaveTextContent("testcase1:test1");

    // Find and click the metric sort button - get the second Metric header
    const metricHeaders = screen.getAllByText("Testcase:Test");
    fireEvent.click(metricHeaders[0].closest('th'));

    // Get rows after sorting
    const sortedRows = screen.getAllByRole("row");
    expect(sortedRows[7]).toHaveTextContent("testcase1:test4");
  });

  it("sorts by score correctly", () => {
    const rows = screen.getAllByRole("row");
    expect(rows[7]).toHaveTextContent("0.75");
    expect(rows[8]).toHaveTextContent("1.00");

    // Find and click the metric sort button - get the second Metric header
    const metricHeaders = screen.getAllByText("Score");
    fireEvent.click(metricHeaders[0].closest('th'));

    // Get rows after sorting
    const sortedRows = screen.getAllByRole("row");
    expect(rows[7]).toHaveTextContent("0.00");
    expect(rows[8]).toHaveTextContent("1.00");
  });


});
