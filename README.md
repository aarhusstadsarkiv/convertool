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

| Tool                 | Output             | Explanation                                                      | Extension |
|----------------------|--------------------|------------------------------------------------------------------|-----------|
| audio                | flac               |                                                                  | .flac     |
| audio                | mp3                |                                                                  | .mp3      |
| audio                | wav                |                                                                  | .wav      |
| cad / emf            | dxf                |                                                                  | .dxf      |
| cad / emf            | jp2                |                                                                  | .jp2      |
| cad / emf            | jpeg               |                                                                  | .jpg      |
| cad / emf            | jpg                |                                                                  | .jpg      |
| cad / emf            | pdf                |                                                                  | .pdf      |
| cad / emf            | png                |                                                                  | .png      |
| cad / emf            | svg                |                                                                  | .svg      |
| cad / emf            | tif                |                                                                  | .tif      |
| cad / emf            | tiff               |                                                                  | .tif      |
| copy                 | copy               |                                                                  | .copy     |
| document             | html               |                                                                  | .html     |
| document             | jp2                |                                                                  | .jp2      |
| document             | jpeg               |                                                                  | .jpg      |
| document             | jpg                |                                                                  | .jpg      |
| document             | odt                |                                                                  | .odt      |
| document             | pdf                |                                                                  | .pdf      |
| document             | png                |                                                                  | .png      |
| document             | tif                |                                                                  | .tif      |
| document             | tiff               |                                                                  | .tif      |
| eml                  | html               |                                                                  | .html     |
| eml                  | jp2                |                                                                  | .jp2      |
| eml                  | jpeg               |                                                                  | .jpg      |
| eml                  | jpg                |                                                                  | .jpg      |
| eml                  | pdf                |                                                                  | .pdf      |
| eml                  | png                |                                                                  | .png      |
| eml                  | tif                |                                                                  | .tif      |
| eml                  | tiff               |                                                                  | .tif      |
| eml                  | txt                |                                                                  | .txt      |
| gis                  | geojson            |                                                                  | .geojson  |
| gis                  | gml                |                                                                  | .gml      |
| gis                  | gml3               |                                                                  | .gml3     |
| gis                  | shp                |                                                                  | .shp      |
| html / browser       | jp2                |                                                                  | .jp2      |
| html / browser       | jpeg               |                                                                  | .jpg      |
| html / browser       | jpg                |                                                                  | .jpg      |
| html / browser       | pdf                |                                                                  | .pdf      |
| html / browser       | png                |                                                                  | .png      |
| html / browser       | tif                |                                                                  | .tif      |
| html / browser       | tiff               |                                                                  | .tif      |
| image                | jp2                |                                                                  | .jp2      |
| image                | jpeg               |                                                                  | .jpg      |
| image                | jpg                |                                                                  | .jpg      |
| image                | png                |                                                                  | .png      |
| image                | tif                |                                                                  | .tif      |
| image                | tiff               |                                                                  | .tif      |
| ipynb                | html               |                                                                  | .html     |
| ipynb                | jp2                |                                                                  | .jp2      |
| ipynb                | jpeg               |                                                                  | .jpg      |
| ipynb                | jpg                |                                                                  | .jpg      |
| ipynb                | pdf                |                                                                  | .pdf      |
| ipynb                | png                |                                                                  | .png      |
| ipynb                | tif                |                                                                  | .tif      |
| ipynb                | tiff               |                                                                  | .tif      |
| mdi                  | pdf                |                                                                  | .pdf      |
| mdi                  | tif                |                                                                  | .tif      |
| mdi                  | tiff               |                                                                  | .tif      |
| medcom               | html               |                                                                  | .html     |
| medcom               | jp2                |                                                                  | .jp2      |
| medcom               | jpeg               |                                                                  | .jpg      |
| medcom               | jpg                |                                                                  | .jpg      |
| medcom               | pdf                |                                                                  | .pdf      |
| medcom               | png                |                                                                  | .png      |
| medcom               | tif                |                                                                  | .tif      |
| medcom               | tiff               |                                                                  | .tif      |
| msexcel              | html               |                                                                  | .html     |
| msexcel              | ods                |                                                                  | .ods      |
| msexcel              | pdf                |                                                                  | .pdf      |
| msg                  | html               |                                                                  | .html     |
| msg                  | jp2                |                                                                  | .jp2      |
| msg                  | jpeg               |                                                                  | .jpg      |
| msg                  | jpg                |                                                                  | .jpg      |
| msg                  | pdf                |                                                                  | .pdf      |
| msg                  | png                |                                                                  | .png      |
| msg                  | tif                |                                                                  | .tif      |
| msg                  | tiff               |                                                                  | .tif      |
| msg                  | txt                |                                                                  | .txt      |
| mspowerpoint         | odp                |                                                                  | .odp      |
| mspowerpoint         | pdf                |                                                                  | .pdf      |
| msword               | odt                |                                                                  | .odt      |
| msword               | pdf                |                                                                  | .pdf      |
| msword               | pdfa               | Convert PDF to PDF/A                                             | .pdf      |
| pdf                  | jp2                |                                                                  | .jp2      |
| pdf                  | jpeg               |                                                                  | .jpg      |
| pdf                  | jpg                |                                                                  | .jpg      |
| pdf                  | pdfa-1             | Convert PDF to PDF/A-1b                                          | .pdf      |
| pdf                  | pdfa-2             | Convert PDF to PDF/A-2b                                          | .pdf      |
| pdf                  | pdfa-3             | Convert PDF to PDF/A-3b                                          | .pdf      |
| pdf                  | png                |                                                                  | .png      |
| pdf                  | tif                |                                                                  | .tif      |
| pdf                  | tiff               |                                                                  | .tif      |
| presentation         | html               |                                                                  | .html     |
| presentation         | odp                |                                                                  | .odp      |
| presentation         | pdf                |                                                                  | .pdf      |
| sas                  | csv                |                                                                  | .csv      |
| sas                  | html               |                                                                  | .html     |
| sas                  | ods                |                                                                  | .ods      |
| sas                  | pdf                |                                                                  | .pdf      |
| sas                  | tsv                |                                                                  | .tsv      |
| spreadsheet          | html               |                                                                  | .html     |
| spreadsheet          | ods                |                                                                  | .ods      |
| spreadsheet          | pdf                |                                                                  | .pdf      |
| symphovert           | odp                | Convert Lotus files using IBM Symphony                           | .odp      |
| symphovert           | ods                | Convert Lotus files using IBM Symphony                           | .ods      |
| symphovert           | odt                | Convert Lotus files using IBM Symphony                           | .odt      |
| template             | corrupted          |                                                                  | .txt      |
| template             | duplicate          |                                                                  | .txt      |
| template             | empty              |                                                                  | .txt      |
| template             | extracted-archive  |                                                                  | .txt      |
| template             | not-convertable    |                                                                  | .txt      |
| template             | not-preservable    |                                                                  | .txt      |
| template             | password-protected |                                                                  | .txt      |
| template             | temporary-file     |                                                                  | .txt      |
| template             | text               |                                                                  | .txt      |
| template             | unidentified       |                                                                  | .txt      |
| text                 | txt                | Convert text file txt with UTF-8 encoding and x-fmt/111 as PUID  | .txt      |
| text / text-to-image | jp2                |                                                                  | .jp2      |
| text / text-to-image | jpeg               |                                                                  | .jpg      |
| text / text-to-image | jpg                |                                                                  | .jpg      |
| text / text-to-image | png                |                                                                  | .png      |
| text / text-to-image | tif                |                                                                  | .tif      |
| text / text-to-image | tiff               |                                                                  | .tif      |
| tnef                 | html               |                                                                  | .html     |
| tnef                 | txt                |                                                                  | .txt      |
| video                | h264               | Convert video to MP4 (H.264 video, AAC audio)                    | .mp4      |
| video                | h264-mpg           | Convert video to MP4 (H.264 video, AAC audio) with mpg extension | .mpg      |
| video                | h265               | Convert video to MP4 (H.265 video, AAC audio)                    | .mp4      |
| video                | mpeg               | Convert video to MPEG2 (MPEG2 video, MP3 audio)                  | .mpg      |
| xslt                 | html               |                                                                  | .html     |
| xslt                 | jp2                |                                                                  | .jp2      |
| xslt                 | jpeg               |                                                                  | .jpg      |
| xslt                 | jpg                |                                                                  | .jpg      |
| xslt                 | pdf                |                                                                  | .pdf      |
| xslt                 | png                |                                                                  | .png      |
| xslt                 | tif                |                                                                  | .tif      |
| xslt                 | tiff               |                                                                  | .tif      |
| xslt                 | xml                |                                                                  | .xml      |
| zipfile              | -                  | Extract a specific file from a ZIP container.                    | -         |

## Dependencies

| Tool                 | Output   | OS      | Program                                     |
|----------------------|----------|---------|---------------------------------------------|
| audio                | flac     |         | ffmpeg                                      |
| audio                | mp3      |         | ffmpeg                                      |
| audio                | wav      |         | ffmpeg                                      |
| cad / emf            | dxf      | Windows | abviewer                                    |
| cad / emf            | jp2      | Windows | abviewer, imagemagick, nconvert             |
| cad / emf            | jpeg     | Windows | abviewer, imagemagick, nconvert             |
| cad / emf            | jpg      | Windows | abviewer, imagemagick, nconvert             |
| cad / emf            | pdf      | Windows | abviewer                                    |
| cad / emf            | png      | Windows | abviewer, imagemagick, nconvert             |
| cad / emf            | svg      | Windows | abviewer                                    |
| document             | html     |         | libreoffice                                 |
| document             | jp2      |         | imagemagick, libreoffice, nconvert          |
| document             | jpeg     |         | imagemagick, libreoffice, nconvert          |
| document             | jpg      |         | imagemagick, libreoffice, nconvert          |
| document             | odt      |         | libreoffice                                 |
| document             | pdf      |         | libreoffice                                 |
| document             | png      |         | imagemagick, libreoffice, nconvert          |
| eml                  | jp2      |         | chromium, imagemagick, nconvert             |
| eml                  | jpeg     |         | chromium, imagemagick, nconvert             |
| eml                  | jpg      |         | chromium, imagemagick, nconvert             |
| eml                  | pdf      |         | chromium                                    |
| eml                  | png      |         | chromium, imagemagick, nconvert             |
| gis                  | geojson  | Linux   | ogr2ogr                                     |
| gis                  | gml      | Linux   | ogr2ogr                                     |
| gis                  | gml3     | Linux   | ogr2ogr                                     |
| gis                  | shp      | Linux   | ogr2ogr                                     |
| html / browser       | jp2      |         | chromium, imagemagick, nconvert             |
| html / browser       | jpeg     |         | chromium, imagemagick, nconvert             |
| html / browser       | jpg      |         | chromium, imagemagick, nconvert             |
| html / browser       | pdf      |         | chromium                                    |
| html / browser       | png      |         | chromium, imagemagick, nconvert             |
| image                | jp2      |         | imagemagick, nconvert                       |
| image                | jpeg     |         | imagemagick, nconvert                       |
| image                | jpg      |         | imagemagick, nconvert                       |
| image                | png      |         | imagemagick, nconvert                       |
| image                | tif      |         | imagemagick, nconvert                       |
| image                | tiff     |         | imagemagick, nconvert                       |
| ipynb                | jp2      |         | chromium, imagemagick, nconvert             |
| ipynb                | jpeg     |         | chromium, imagemagick, nconvert             |
| ipynb                | jpg      |         | chromium, imagemagick, nconvert             |
| ipynb                | pdf      |         | chromium                                    |
| ipynb                | png      |         | chromium, imagemagick, nconvert             |
| mdi                  | pdf      | Windows | imagemagick, mdi2tif, nconvert              |
| mdi                  | tif      | Windows | mdi2tif                                     |
| mdi                  | tiff     | Windows | mdi2tif                                     |
| medcom               | html     |         | xmlstarlet                                  |
| medcom               | jp2      |         | chromium, imagemagick, nconvert, xmlstarlet |
| medcom               | jpeg     |         | chromium, imagemagick, nconvert, xmlstarlet |
| medcom               | jpg      |         | chromium, imagemagick, nconvert, xmlstarlet |
| medcom               | pdf      |         | chromium, xmlstarlet                        |
| medcom               | png      |         | chromium, imagemagick, nconvert, xmlstarlet |
| msexcel              | html     | Windows | docto                                       |
| msexcel              | ods      | Windows | docto                                       |
| msexcel              | pdf      | Windows | docto                                       |
| msg                  | jp2      |         | imagemagick, nconvert                       |
| msg                  | jpeg     |         | imagemagick, nconvert                       |
| msg                  | jpg      |         | imagemagick, nconvert                       |
| msg                  | pdf      |         | imagemagick, nconvert                       |
| msg                  | png      |         | imagemagick, nconvert                       |
| mspowerpoint         | odp      | Windows | docto                                       |
| mspowerpoint         | pdf      | Windows | docto                                       |
| msword               | odt      | Windows | docto                                       |
| msword               | pdf      | Windows | docto                                       |
| msword               | pdfa     | Windows | docto                                       |
| pdf                  | jp2      |         | imagemagick, nconvert                       |
| pdf                  | jpeg     |         | imagemagick, nconvert                       |
| pdf                  | jpg      |         | imagemagick, nconvert                       |
| pdf                  | pdfa-1   |         | ghostscript                                 |
| pdf                  | pdfa-2   |         | ghostscript                                 |
| pdf                  | pdfa-3   |         | ghostscript                                 |
| pdf                  | png      |         | imagemagick, nconvert                       |
| pdf                  | tif      |         | pdftoppm, tiffcp                            |
| pdf                  | tiff     |         | pdftoppm, tiffcp                            |
| presentation         | html     |         | libreoffice                                 |
| presentation         | odp      |         | libreoffice                                 |
| presentation         | pdf      |         | libreoffice                                 |
| sas                  | html     |         | libreoffice                                 |
| sas                  | ods      |         | libreoffice                                 |
| sas                  | pdf      |         | libreoffice                                 |
| spreadsheet          | html     |         | libreoffice                                 |
| spreadsheet          | ods      |         | libreoffice                                 |
| spreadsheet          | pdf      |         | libreoffice                                 |
| symphovert           | odp      | Windows | symphony                                    |
| symphovert           | ods      | Windows | symphony                                    |
| symphovert           | odt      | Windows | symphony                                    |
| text / text-to-image | jp2      |         | imagemagick, libreoffice, nconvert          |
| text / text-to-image | jpeg     |         | imagemagick, libreoffice, nconvert          |
| text / text-to-image | jpg      |         | imagemagick, libreoffice, nconvert          |
| text / text-to-image | png      |         | imagemagick, libreoffice, nconvert          |
| video                | h264     |         | ffmpeg                                      |
| video                | h264-mpg |         | ffmpeg                                      |
| video                | h265     |         | ffmpeg                                      |
| video                | mpeg2    |         | ffmpeg                                      |
| xslt                 | html     |         | xmlstarlet                                  |
| xslt                 | jp2      |         | chromium, imagemagick, nconvert, xmlstarlet |
| xslt                 | jpeg     |         | chromium, imagemagick, nconvert, xmlstarlet |
| xslt                 | jpg      |         | chromium, imagemagick, nconvert, xmlstarlet |
| xslt                 | pdf      |         | chromium, xmlstarlet                        |
| xslt                 | png      |         | chromium, imagemagick, nconvert, xmlstarlet |
| xslt                 | xml      |         | xmlstarlet                                  |