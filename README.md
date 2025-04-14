# PDF Slide Condenser

This Python script helps consolidate similar slides in a PDF presentation by identifying and merging slides that have only minor differences between them.

## Requirements

- Python 3.7+
- poppler-utils (for pdf2image)

### Installing poppler-utils

- On macOS: `brew install poppler`
- On Ubuntu/Debian: `sudo apt-get install poppler-utils`
- On Windows: Download from [poppler releases](http://blog.alivate.com.au/poppler-windows/)

## Installation

1. Clone this repository
2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your input PDF file in the same directory as the script
2. Modify the `input_pdf` and `output_pdf` variables in the `main()` function of `pdf_condenser.py`
3. Run the script:
```bash
python pdf_condenser.py
```

The script will:
1. Convert the PDF pages to images
2. Compare consecutive slides for similarity
3. Create a new PDF with similar slides merged
4. Output the number of slides that were merged

## How it works

The script uses computer vision techniques to:
1. Convert PDF pages to images
2. Compare consecutive slides using structural similarity
3. Identify slides that are very similar (above a threshold of 0.95 by default)
4. Create a new PDF that skips the redundant slides

## Customization

You can adjust the similarity threshold in the `process_pdf()` method:
- Higher values (closer to 1.0) will only merge very similar slides
- Lower values will merge more slides but might combine slides that are too different

## Notes

- The script works best with presentation slides that have consistent layouts
- It's recommended to test with a copy of your original PDF first
- The script creates temporary files during processing but cleans them up automatically 