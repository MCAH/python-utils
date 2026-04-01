# Lantern Slide Collection utilities

to make uploading images from the Lantern Slide Collection easier. all scripts intended to run on a single folder at a time. 

#### `ls.py`
general variables and functions for folder

#### `label-vis-ls.py`
runs google cloud OCR on images and generates CSV

#### `tabs-label-ls.py`
uses color label hierarchy to apply tabs labels to image metadata

#### `label-csv-ls.py`
writes CSV from image metadata

#### `csv-label-ls.py`
overwrites image metadata with CSV

#### `rename-raw-ls.py`
renames images with record IDs

#### `verso-tags-ls.py`
writes verso record ID to image metadata

#### `label-csv-mcid-tabs-ls.py`
generates CSV for inital upload to MCID - includes pathing and subjects but not further cataloging

#### `label-csv-mcid-cat-ls.py`
generates CSV for uploading additional cataloging to MCID - does not include subjects