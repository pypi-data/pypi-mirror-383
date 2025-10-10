# windIO *JSON Schema for Humans* template

This directory contains a *JSON Schema for Humans* (JSFH) JavaScript/HTML template for rendering a JSON Schema within Sphinx documentation.

It is a modification of the [JSFH *js* template](https://github.com/coveooss/json-schema-for-humans/tree/main/json_schema_for_humans/templates/js) which mainly strips out `<head>` block (only applicable of stand along HTML pages) and the `<body>` keywords. The content of the `<head>` block is then add back in except for JSFH CSS styling which has been modified to work with the Sphinx template used. These modifications are mainly done the `base.html` Jinja template.

Besides these changes the following small changes has also been done:

1. The *Expand all* and *Collapse all* buttons has been added to the right of the `root` schema description
2. A flag has been added to config options to skip the `root` heading as Sphinx needs a heading in the `.rst` file to allow for indexing
3. The `units` entry is added below the description of the properties that defines `units`