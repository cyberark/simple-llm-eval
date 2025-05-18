import React from "react";
import "@testing-library/jest-dom";
import { render, screen, fireEvent, within } from "@testing-library/react";
import { describe, it, beforeEach } from "vitest";
import SummaryReport from "../components/SummaryReport";

// Helper function to render component before each test
beforeEach(() => {
  render(<SummaryReport />);
});

describe("SummaryReport Component", () => {
  it("renders the component correctly", () => {
    expect(screen.getByText("LLM Evaluation Summary Report")).toBeInTheDocument();
  });

  it("renders all BarChart components", () => {
    const chartLabels = ["correctness", "completeness", "relevance", "faithfulness"];
    chartLabels.forEach(label => {
      expect(screen.getByText(label)).toBeInTheDocument();
    });
  });

});
