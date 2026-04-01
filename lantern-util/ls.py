# CSV headers
workingheader = ['filename', 'type', 's1 LS', 's2 LS', 's3 LS', 's4 LS', 's5 LS', 's6 LS', 's7 LS', 'subheading', 'manufacturer', 'source', 'OCR', 'transcription', 'title', 'location', 'verso', 'attribute']

tabsheader = ['Record ID', 's1 LS', 's2 LS', 's3 LS', 's4 LS', 's5 LS', 's6 LS', 's7 LS', 'Subheading', 'Manufacturer', 'Source Collection', 'Slide Attribute', 'Digitized Date', 'Media Source', 'Collection', 'Media Type', 'Storage Location', 'Media', 'Thumbnail', 'Verso Media', 'Verso Thumbnail', 'MCAH Project/Trip', 'OCR Description', 'ALW Complete']

catheader = ['Record ID', 'Media Title', 'Location', 'Manufacturer', 'Source Collection', 'Label Transcription']

# color tags
red, green, yellow, blue, white, verso, verso2, reshoot, reference, loan = 'Red', 'Green tab', 'Yellow', 'Blue', 'Purple', 'Green', 'Verso2', 'Reshoot', 'Reference', 'Loan'

# functions
	# ocr
def exceptions(word, **kwargs):
	keeplist = ['II', 'III', 'IV', 'VI', 'VII', 'VIII', 'IX', 'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX']
	
	if word.upper() in (keeplist):
		return word.upper()