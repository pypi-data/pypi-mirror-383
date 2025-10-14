# renoir

A computational tool that analyzes and visualizes artist-specific works from the WikiArt dataset, bridging traditional art history with data-driven methods. Designed for creative coding courses, design research, and digital humanities practitioners who explore visual culture through computational approaches.

<!-- [![DOI](https://joss.theoj.org/papers/10.21105/joss.XXXXX/status.svg)](https://doi.org/10.21105/joss.XXXXX) -->

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Overview

`renoir` addresses a gap in the art and design research toolkit by providing accessible art data analysis capabilities. Unlike computer vision tools focused on algorithmic complexity, it emphasizes clarity and visual communication for art and design practitioners and educators.

**Applications:**

- **Creative Coding Courses**: Teach programming through culturally meaningful datasets
- **Art and Design Research**: Analyze visual patterns and artistic influences quantitatively
- **Computational Design**: Explore historical precedents through data-driven methods
- **Dynamic Branding Projects**: Study stylistic evolution and visual consistency across artists
- **Digital Humanities Research**: Generate publication-ready visualizations for academic work
- **Art and Design Studios**: Integrate historical analysis into contemporary practice

**Why `renoir` for the art and design community:**

- Fills a gap in art and design research tools
- Focuses on visual culture and artistic practice
- Publication-ready visualizations suitable for academic and professional contexts
- Pedagogical clarity without sacrificing analytical depth
- Extensible foundation for advanced art and design research projects

## Key Features

- **Easy Art Analysis**: Extract and analyze works by 100+ artists from WikiArt
- **Built-in Visualizations**: Genre distributions, style comparisons, artist overviews
- **Educational Focus**: Designed specifically for classroom use and student projects
- **Publication Ready**: High-quality plots suitable for presentations and reports
- **Flexible Usage**: Works with or without visualization dependencies
- **Export Capabilities**: Save plots as PNG files for reports and presentations
- **Pure Python**: Easy to install and integrate into existing curricula

## For Art & Design Education & Research

### Research Applications

Support both pedagogical and scholarly work in art and design:

- **Style Evolution Analysis**: Quantify artistic development across periods
- **Movement Comparison**: Compare visual approaches across artistic schools
- **Influence Mapping**: Explore shared themes and techniques through data
- **Portfolio Diversity**: Measure stylistic variety and consistency in artistic practice

### Pedagogical Integration

`renoir` serves art and design educators teaching computational methods:

- Clean, readable code that students can understand and extend
- Professional visualizations suitable for academic presentations
- Jupyter notebook compatibility for interactive exploration
- Minimal dependencies to reduce classroom setup friction
- Extensible architecture for advanced student projects

### Curriculum Applications

- **Creative Coding**: Teach programming through visual culture analysis
- **Computational Design**: Integrate historical research with contemporary practice
- **Design Research Methods**: Introduce quantitative analysis in design contexts
- **Dynamic Branding**: Study visual consistency and evolution in artistic identity
- **Digital Humanities**: Bridge traditional art history with computational approaches

## Installation

### Basic Installation

```bash
pip install renoir
```

### With Visualization Support

```bash
pip install 'renoir[visualization]'
```

Or install from source:

```bash
git clone https://github.com/MichailSemoglou/renoir.git
cd renoir
pip install -e .
# For visualizations:
pip install -e .[visualization]
```

## Quick Start

### Basic Usage

```python
from renoir import quick_analysis

# Text-based analysis
quick_analysis('pierre-auguste-renoir')

# With visualizations (requires matplotlib)
quick_analysis('pierre-auguste-renoir', show_plots=True)
```

### Advanced Usage

```python
from renoir import ArtistAnalyzer

# Initialize analyzer
analyzer = ArtistAnalyzer()

# Extract works by a specific artist
works = analyzer.extract_artist_works('pierre-auguste-renoir')

# Analyze genre and style distributions
genres = analyzer.analyze_genres(works)
styles = analyzer.analyze_styles(works)

print(f"Found {len(works)} works")
print(f"Genres: {genres}")
print(f"Styles: {styles}")
```

### Visualization Examples

```python
from renoir import ArtistAnalyzer

analyzer = ArtistAnalyzer()

# Create visualizations for a single artist
analyzer.plot_genre_distribution('pierre-auguste-renoir')
analyzer.plot_style_distribution('pablo-picasso')

# Compare multiple artists
analyzer.compare_artists_genres(['claude-monet', 'pierre-auguste-renoir', 'edgar-degas'])

# Comprehensive overview
analyzer.create_artist_overview('vincent-van-gogh')

# Save visualizations to files
analyzer.plot_genre_distribution('monet', save_path='monet_genres.png')
analyzer.create_artist_overview('picasso', save_path='picasso_overview.png')
```

### Check Visualization Support

```python
from renoir import check_visualization_support

# Check if visualization libraries are installed
check_visualization_support()
```

### List Available Artists

```python
from renoir import ArtistAnalyzer

analyzer = ArtistAnalyzer()
artists = analyzer.list_artists(limit=10)
print(artists)
```

## Pedagogical Applications

### Classroom Exercise 1: Genre Distribution

Students can compare genre distributions across different artists:

```python
from renoir import ArtistAnalyzer

analyzer = ArtistAnalyzer()

artists = ['pierre-auguste-renoir', 'claude-monet', 'vincent-van-gogh']
for artist in artists:
    works = analyzer.extract_artist_works(artist)
    genres = analyzer.analyze_genres(works)
    print(f"\n{artist}: {genres}")
```

### Classroom Exercise 2: Visual Style Analysis

Analyze and visualize an artist's style distribution:

```python
from renoir import ArtistAnalyzer

analyzer = ArtistAnalyzer()

# Create a comprehensive visual overview
analyzer.create_artist_overview('pablo-picasso')

# Or create specific visualizations
analyzer.plot_style_distribution('pablo-picasso')
analyzer.plot_genre_distribution('pablo-picasso')
```

### Classroom Exercise 3: Comparative Analysis

Compare multiple artists visually:

```python
from renoir import ArtistAnalyzer

analyzer = ArtistAnalyzer()

# Compare Impressionist masters
impressionist_artists = [
    'pierre-auguste-renoir',
    'claude-monet',
    'edgar-degas',
    'camille-pissarro'
]

analyzer.compare_artists_genres(impressionist_artists)
```

## Dataset Information

This tool uses the [WikiArt dataset](https://huggingface.co/datasets/huggan/wikiart) from HuggingFace, which contains:

- Over 81,000 artworks
- Works by 129 artists
- Rich metadata including genre, style, and artist information

## Educational Philosophy

`renoir` is built on these pedagogical principles:

1. **Simplicity first**: Clear, readable code that students can understand
2. **Cultural data**: Uses art history to teach data analysis concepts
3. **Extensible**: Students can fork and extend for their own projects
4. **Real datasets**: Works with actual cultural heritage data, not toy examples

## Requirements

### Core Requirements

- Python 3.8+
- datasets >= 2.0.0
- Pillow >= 8.0.0

### Visualization Requirements (Optional)

- matplotlib >= 3.5.0
- seaborn >= 0.11.0

Install with: `pip install 'renoir[visualization]'`

## Contributing

Contributions are welcome, especially:

- Additional pedagogical examples
- Classroom exercises and assignments
- Documentation improvements
- Bug fixes

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- WikiArt dataset creators
- HuggingFace Datasets library
- Students in computational design courses who inspired this tool

## Contact

For questions about using this tool in your classroom, please open an issue or contact [m.semoglou@tongji.edu.cn](mailto:m.semoglou@tongji.edu.cn).
