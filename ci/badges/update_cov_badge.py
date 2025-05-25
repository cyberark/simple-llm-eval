#!/usr/bin/env python3

import os
import sys
import re

def get_line_rate(coverage_xml_path):
    # Intentionally avoid using xml parsing
    with open(coverage_xml_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    top_coverage_line_match = next((item for item in lines if item.strip().startswith('<coverage')), None)
    match = re.search(r'line-rate="([0-9.]+)"', top_coverage_line_match)

    if not match:
        raise ValueError('line-rate not found in coverage xml')

    coverage = match.group(1)

    # check if float
    try:
        float(coverage)
        return float(coverage)
    except ValueError:
        raise ValueError('line-rate is not a valid float')


def get_color(percentage):
    if percentage >= 90:
        return '#4c1'  # Green
    elif percentage >= 70:
        return '#dfb317'  # Yellow
    elif percentage >= 50:
        return '#fe7d37'  # Orange
    else:
        return '#e05d44'  # Red

def update_svg(svg_path, percentage, color, output_path):
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg = f.read()
    # Update color
    svg = re.sub(r'(<rect x="70" width="50" height="20" fill=")#[a-zA-Z0-9]+("/>)',
                f'\\1{color}\\2', svg)
    # Update percentage text (both occurrences)
    svg = re.sub(
        r'(<text x="95" y="15" [^>]*>)[0-9]+%(<)',
        lambda m: f'{m.group(1)}{percentage}%{m.group(2)}',
        svg
    )
    svg = re.sub(
        r'(<text x="95" y="14">)[0-9]+%(</text>)',
        lambda m: f'{m.group(1)}{percentage}%{m.group(2)}',
        svg
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg)

def main():
    if len(sys.argv) != 2:
        print('Usage: update_cov_badge.py <path-to-coverage.xml>')
        sys.exit(1)

    cov_xml = sys.argv[1]
    svg_path = 'ci/badges/coverage.svg'
    output_path = 'ci/badges/tmp/coverage.svg'
    line_rate = get_line_rate(cov_xml)
    percent = int(round(line_rate * 100))
    color = get_color(percent)
    update_svg(svg_path, percent, color, output_path)
    
    print(f'✅ Updated badge written to {output_path} with {percent}% coverage and color {color}')

if __name__ == '__main__':
    main()
