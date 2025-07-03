# Convertool (new)

## Usage

```
Usage: convertool [OPTIONS] COMMAND [ARGS]...

  Convert files either by themselves or by following the instructions in a
  digiarch database.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  digiarch    Convert files from digiarch
  standalone  Convert single files.
```

### convertool digiarch

```
Usage: convertool digiarch [OPTIONS] AVID_DIR
                           {original:master|master:access|master:statutory}
                           [QUERY]

  Convert files contained in a digiarch database.

  To convert original files to master files, use the "original:master" TARGET.

  To convert master files to access files, use the "master:access" TARGET.

  To convert master files to statutory files, use the "master:statutory"
  TARGET.

  The QUERY argument allows to restrict which files will be converted. For
  details on its usage see the "digiarch edit" command.

  To restrict the tools that should be used for conversion, use the --tool-
  ignore and --tool-include options. The former will skip files whose tools
  are in the list, the second will skip files whose tools are not in the list.

  Use the --timeout option to override the converters' timeout, set to 0 to
  disable timeouts altogether.

  Use the --verbose option to print the standard output from the converters.
  The output (standard or error) is always printed in case of an error.

  Use the --dry-run option to list files that would be converted without
  performing any action.

Options:
  --tool-ignore TOOL   Exclude specific tools.  [multiple]
  --tool-include TOOL  Include only specific tools.  [multiple]
  --timeout SECONDS    Override converters' timeout.  [x>=0]
  --dry-run            Show changes without committing them.
  --verbose            Show all outputs from converters.
  --help               Show this message and exit.
```

### convertool standalone

```
Usage: convertool standalone [OPTIONS] TOOL OUTPUT DESTINATION FILE...

  Convert FILEs to OUTPUT with the given TOOL.

  The converted FILEs will be placed in the DESTINATION directory. To maintain
  the relative paths of the files, use the --root option to set their common
  parent directory.

  To pass options to the given converter tool, use the --option option with a
  KEY and VALUE. Values can only be strings.

  Use the --timeout option to override the converters' timeout, set to 0 to
  disable timeouts altogether.

  Use the --verbose option to print the standard output from the converters.
  The output (standard or error) is always printed in case of an error.

Options:
  -o, --option <KEY VALUE>  Pass options to the converter.
  --timeout SECONDS         Override converters' timeout.  [x>=0]
  --verbose                 Show all outputs from converters.
  --root DIRECTORY          Set a root for the given files to keep the
                            relative paths in the output.
  --help                    Show this message and exit.
```

## Tools

| Tool         | Output             | Explanation                                                                    | Extension |
|--------------|--------------------|--------------------------------------------------------------------------------|-----------|
| audio        | mp3                | Convert audio/video to MP3                                                     | .mp3      |
| audio        | wav                | Convert audio/video to WAV                                                     | .wav      |
| cad          | dxf                | Convert CAD file (DWG, DXF, etc.) to DXF                                       | .dxf      |
| cad          | pdf                | Convert CAD file (DWG, DXF, etc.) to PDF                                       | .pdf      |
| cad          | svg                | Convert CAD file (DWG, DXF, etc.) to SVG                                       | .svg      |
| document     | odt                | Convert a document file (Word, LibreOffice, etc.) to ODT                       | .odt      |
| document     | html               | Convert a document file (Word, LibreOffice, etc.) to HTML                      | .html     |
| document     | pdf                | Convert a document file (Word, LibreOffice, etc.) to PDF                       | .pdf      |
| document     | jp2                | Convert a document file (Word, LibreOffice, etc.) to JPEG2000                  | .jp2      |
| document     | jpg                | Convert a document file (Word, LibreOffice, etc.) to JPEG                      | .jpg      |
| document     | png                | Convert a document file (Word, LibreOffice, etc.) to PNG                       | .png      |
| document     | tiff               | Convert a document file (Word, LibreOffice, etc.) to TIFF                      | .tiff     |
| gis          | gml                | Convert GIS file with its auxiliaries to GMLv3                                 | .gml      |
| html         | pdf                | Convert HTML to PDF                                                            | .pdf      |
| html         | jp2                | Convert HTML to JPEG2000 images (one per page)                                 | .jp2      |
| html         | jpg                | Convert HTML to JPEG images (one per page)                                     | .jpg      |
| html         | png                | Convert HTML to PNG images (one per page)                                      | .png      |
| html         | tiff               | Convert HTML to TIFF image (multipage)                                         | .tiff     |
| image        | jp2                | Convert image to JPEG2000                                                      | .jp2      |
| image        | jpg                | Convert image to JPEG                                                          | .jpg      |
| image        | pdf                | Convert image to PDF                                                           | .pdf      |
| image        | png                | Convert image to PNG                                                           | .png      |
| image        | tiff               | Convert image to TIFF                                                          | .tiff     |
| msg          | html               | Convert an MSG file to HTML                                                    | .html     |
| msg          | txt                | Convert an MSG file to TXT                                                     | .txt      |
| msg          | pdf                | Convert an MSG file to TXT                                                     | .pdf      |
| msg          | jp2                | Convert an MSG file to JPEG2000                                                | .jp2      |
| msg          | jpg                | Convert an MSG file to JPEG                                                    | .jpg      |
| msg          | png                | Convert an MSG file to PNG                                                     | .png      |
| msg          | tiff               | Convert an MSG file to TIFF                                                    | .tiff     |
| pdf          | pdfa-1             | Convert PDF to PDF/A-1b                                                        | .pdf      |
| pdf          | pdfa-2             | Convert PDF to PDF/A-2b                                                        | .pdf      |
| pdf          | pdfa-3             | Convert PDF to PDF/A-3b                                                        | .pdf      |
| pdf          | jp2                | Convert PDF to JPEG2000 images (one per page)                                  | .jp2      |
| pdf          | jpg                | Convert PDF to JPEG images (one per page)                                      | .jpg      |
| pdf          | png                | Convert PDF to PNG images (one per page)                                       | .png      |
| pdf          | tiff               | Convert PDF to TIFF image (multipage)                                          | .tiff     |
| presentation | odp                | Convert a presentation file (PowerPoint, LibreOffice, etc.) to ODP             | .odp      |
| presentation | html               | Convert a presentation file (PowerPoint, LibreOffice, etc.) to HTML            | .html     |
| presentation | pdf                | Convert a presentation file (PowerPoint, LibreOffice, etc.) to PDF             | .pdf      |
| spreadsheet  | ods                | Convert a spreadsheet file (Excel, LibreOffice, etc.) to ODS                   | .ods      |
| spreadsheet  | html               | Convert a spreadsheet file (Excel, LibreOffice, etc.) to HTML                  | .html     |
| spreadsheet  | pdf                | Convert a spreadsheet file (Excel, LibreOffice, etc.) to PDF                   | .pdf      |
| msword       | pdf                | Convert a document file with Microsoft Word to PDF                             | .pdf      |
| msword       | pdfa               | Convert a document file with Microsoft Word to PDF/A                           | .pdf      |
| msword       | odt                | Convert a document file with Microsoft Word to ODT                             | .odt      |
| msexcel      | pdf                | Convert a spreadsheet file with Microsoft Excel to PDF                         | .pdf      |
| msexcel      | ods                | Convert a spreadsheet file with Microsoft Excel to ODS                         | .ods      |
| msexcel      | html               | Convert a spreadsheet file with Microsoft Excel to HTML                        | .html     |
| mspowerpoint | pdf                | Convert a presentation file with Microsoft PowerPoint to PDF                   | .pdf      |
| mspowerpoint | odp                | Convert a presentation file with Microsoft PowerPoint to ODP                   | .odp      |
| sas          | csv                | Convert a sas7bdat file to CSV                                                 | .csv      |
| sas          | tsv                | Convert a sas7bdat file to TSV                                                 | .tsv      |
| text         | jp2                | Convert text file to a JPEG2000 image                                          | .jp2      |
| text         | jpg                | Convert text file to a JPEG image                                              | .jpg      |
| text         | png                | Convert text file to a PNG image                                               | .png      |
| text         | tiff               | Convert text file to a TIFF image                                              | .tiff     |
| tnef         | html               | Convert a TNEF file to HTML                                                    | .html     |
| tnef         | txt                | Convert a TNEF file to TXT                                                     | .txt      |
| video        | h264               | Convert video to mp4 (H.264 video, AAC audio)                                  | .mp4      |
| video        | h264-mpg           | Convert video to mp4 (H.264 video, AAC audio) with mpg extension               | .mpg      |
| video        | h265               | Convert video to mp4 (H.265 video, AAC audio)                                  | .mp4      |
| video        | mpeg               | Convert video to mpeg2 (mpeg2 video, mp3 audio)                                | .mpg      |
| xslt         | html               | Convert an XML file to HTML using an XSLT stylesheet                           | .html     |
| xslt         | xml                | Convert an XML file to XML using an XSLT stylesheet                            | .xml      |
| xslt         | pdf                | Convert an XML file to PDF using an XSLT stylesheet                            | .pdf      |
| xslt         | jp2                | Convert an XML file to JPEG2000 images (one per page) using an XSLT stylesheet | .jp2      |
| xslt         | jpg                | Convert an XML file to JPEG images (one per page) using an XSLT stylesheet     | .jpg      |
| xslt         | png                | Convert an XML file to PNG images (one per page) using an XSLT stylesheet      | .png      |
| xslt         | tiff               | Convert an XML file to TIFF image (multipage) using an XSLT stylesheet         | .tiff     |
| medcom       | html               | Convert a MedCom XML file to HTML                                              | .html     |
| medcom       | xml                | Convert a MedCom XML file to XML                                               | .xml      |
| medcom       | pdf                | Convert a MedCom XML file to PDF                                               | .pdf      |
| medcom       | jp2                | Convert a MedCom XML file to JPEG2000 images (one per page)                    | .jp2      |
| medcom       | jpg                | Convert a MedCom XML file to JPEG images (one per page)                        | .jpg      |
| medcom       | png                | Convert a MedCom XML file to PNG images (one per page)                         | .png      |
| medcom       | tiff               | Convert a MedCom XML file to TIFF image (multipage)                            | .tiff     |
| zipfile      | -                  | Extract a single file from a ZIP                                               | *         |
| template     | text               | Create a TXT template with custom text                                         | .txt      |
| template     | empty              | Create a TXT template for an empty file                                        | .txt      |
| template     | password-protected | Create a TXT template for a password-protected file                            | .txt      |
| template     | corrupted          | Create a TXT template for a corrupted file                                     | .txt      |
| template     | duplicate          | Create a TXT template for a duplicate file                                     | .txt      |
| template     | not-preservable    | Create a TXT template for a not-preservable file                               | .txt      |
| template     | not-convertable    | Create a TXT template for a not-convertable file                               | .txt      |
| template     | extracted-archive  | Create a TXT template for a extracted-archive file                             | .txt      |
| symphovert   | odt                | Check if the file exists as an ODT file in the output directory                | .odt      |
| symphovert   | ods                | Check if the file exists as an ODS file in the output directory                | .ods      |
| symphovert   | odp                | Check if the file exists as an ODP file in the output directory                | .odp      |

## Dependencies

| Tool         | OS      | Program              |
|--------------|---------|----------------------|
| audio        |         | ffmpeg               |
| cad          | Windows | ABViewer             |
| document     |         | libreoffice, convert |
| gis          | Linux   | ogr2ogr              |
| html         |         | chromium, convert    |
| image        |         | convert              |
| medcom       |         | xmlstarlet, chromium |
| msg          |         | convert              |
| msexcel      | Windows | docto                |
| mspowerpoint | Windows | docto                |
| msword       | Windows | docto                |
| pdf          |         | convert              |
| pdf-large    |         | convert              |
| presentation |         | libreoffice          |
| spreadsheet  |         | libreoffice          |
| text         |         | convert              |
| video        |         | ffmpeg               |
| xslt         |         | xmlstarlet, chromium |