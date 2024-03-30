# pdf-eco-print
Save Paper by printing efficiently.

## Result
- Creates a bundled book.
- 2 pages are made to fit in a single side of an A4 sheet.
- A single A4 paper will have 4 pages of the PDF printed. 2 in front and 2 in back.
- Finally, the printed papers can be folded at the center and it will become a booklet.

## Usage
- Printer Used: Brother DCP-T426W
- The printer prints the pages in reverse order so that all the pages after the print will be in the expected order.
    - Eg., If there are 2 pages to be printed, the printer prints the second page first and then the first page.
      The final ordering will be the first page and then the second page because the first page was printed last by
      the printer.
- In order to get the pages in the expected order towards the end. Do the following,
    1. Print merged-x-back.pdf first. Ordering is already reversed in the PDF.
    2. Take all the printed papers and put them exactly in the tray as they are. No need to turn, shuffle or reverse.
    3. Print merged-x-front.pdf.
