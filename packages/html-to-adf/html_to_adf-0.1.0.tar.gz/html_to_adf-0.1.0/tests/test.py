# test.py
from html_to_adf import import_html_to_str, convert_html_to_adf, export_document

html_text = import_html_to_str("test.html")

# If you were going to send this in an API request format, you would want to structure the ADF around a 'body {}'
# Adding True to: convert_html_to_adf(html_text, True) will wrap the entire contents of the dict in a 'body {}' for your ease of use.
resulting_adf_document: dict = convert_html_to_adf(html_text)

print(resulting_adf_document)
export_document(resulting_adf_document)
