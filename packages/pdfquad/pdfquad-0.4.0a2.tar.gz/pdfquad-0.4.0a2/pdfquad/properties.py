#! /usr/bin/env python3

"""PDF Quality Assessment for Digitisation batches

Johan van der Knijff

Copyright 2024, KB/National Library of the Netherlands

PDF properties extraction module

"""
import sys
import os
import io
import logging
import base64
from lxml import etree
import pymupdf
import PIL
from PIL import ImageCms
from . import jpegquality


def dictionaryToElt(name, dictionary):
    """Create Element object from dictionary"""
    elt = etree.Element(name)
    for key, value in dictionary.items():
        child = etree.Element(key)
        child.text = str(value)
        elt.append(child)
    return elt


def getBPC(image):
    """Return Bits per Component as a function of mode and components values"""
    mode_to_bpp = {"1": 1,
                   "L": 8,
                   "P": 8,
                   "RGB": 24,
                   "RGBA": 32,
                   "CMYK": 32,
                   "YCbCr": 24,
                   "LAB": 24,
                   "HSV": 24,
                   "I": 32,
                   "F": 32}

    bitsPerPixel = mode_to_bpp[image.mode]
    noComponents = len(image.getbands())

    if noComponents != 0  and isinstance(bitsPerPixel, int):
        bpc = int(bitsPerPixel/noComponents)
    else:
        bpc = -9999

    return bpc


def getProperties(PDF):
    """Extract properties and return result as Element object"""

    # Create element object to store all properties
    propertiesElt = etree.Element("properties")

    # Element to store exceptions at file level
    exceptionsFileElt = etree.Element("exceptions")

    # Create and fill descriptive elements
    fPathElt = etree.Element("filePath")
    fPathElt.text = PDF
    fSizeElt = etree.Element("fileSize")
    fSizeElt.text = str(os.path.getsize(PDF))

    # Add to properies element
    propertiesElt.append(fPathElt)
    propertiesElt.append(fSizeElt)

    # Parse PDF and check for open password
    openPasswordElt = etree.Element("openPassword")
    try:
        doc = pymupdf.open(PDF)
        rc = doc.authenticate("whatever")
        if rc == 0:
            openPasswordElt.text = str(True)
            propertiesElt.append(openPasswordElt)
            logging.warning("PDF has open password")
            return propertiesElt
        else:
            openPasswordElt.text = str(False)
            propertiesElt.append(openPasswordElt)
    except Exception  as e:
        ex = etree.SubElement(exceptionsFileElt,'exception')
        ex.text = str(e)
        propertiesElt.append(exceptionsFileElt)
        logging.warning(("while opening PDF: {}").format(str(e)))
        return propertiesElt

    # Page count
    pages = doc.page_count

    # Document metadata. PyMuPDF's doc.metadata method only returns the fields
    # that are defined in the PDF spec, so instead we use a more low-level approach
    # that extracts all fields 

    metadata = {}

    # Read Info key from document trailer, which contains xref reference to document
    # information dictionary, which holds the metadata
    _ , trailerInfo = doc.xref_get_key(-1, "Info")
    try:
        infoXref = int(trailerInfo.split()[0])
        infoKeys = doc.xref_get_keys(infoXref)
        for key in infoKeys:
            _ , value = doc.xref_get_key(infoXref, key)
            metadata[key] = value
    except:
        pass

    # Add "format" and "encryption" entries from previously 
    # used doc.metadata method
    try:
        metadata["format"] = doc.metadata["format"]
    except KeyError:
        pass
    try:
        metadata["encryption"] = doc.metadata["encryption"]
    except KeyError:
        pass

    # Convert to element
    metadataElt = dictionaryToElt('meta', metadata)

    # Read pageMode from document catalog (if it exists)
    # pageMode is needed for the thumbnail check
    catXref = doc.pdf_catalog()
    pageMode = doc.xref_get_key(catXref, "PageMode")
    pageModeElt = etree.Element("PageMode")
    if pageMode[0] == 'null':
        pageModeElt.text = "undefined"
    else:
        pageModeElt.text = pageMode[1]

    # Check if document is linearized (AKA fast web view/access)
    linearizedElt = etree.Element("isLinearized")
    isLinearized = doc.is_fast_webaccess
    if isLinearized:
        linearizedElt.text = str(True)
    else:
        linearizedElt.text = str(False)

    # Check for digital signatures
    # signatureFlag. No signatures for value -1; other values (1,3) indicate signatures.
    signatureFlag = doc.get_sigflags()
    signatureElt = etree.Element("signatureFlag")
    signatureElt.text = str(signatureFlag)

    # Element object for storing annotation types
    annotsElt =  etree.Element("annotations")

    # JavaScript element
    javaScriptElt = etree.Element("containsJavaScript")
    javaScriptElt.text = str(False)

    # Iterate over all objects and check for annotations and JavaScript.
    # This doesn't work for Watermark annotations that are wrapped inside
    # stream objects, so these are dealt with separately at the page level.
    try:
        xreflen = doc.xref_length()
        for xref in range(1, xreflen):
            type = doc.xref_get_key(xref, "Type")[1]
            subtype = doc.xref_get_key(xref, "Subtype")[1]
            js = doc.xref_get_key(xref, "JS")
            if type =="/Annot":
                annotElt = etree.SubElement(annotsElt,'annotation')
                annotElt.text = subtype
            if js != ("null", "null"):
                javaScriptElt.text = str(True)
    except Exception as e:
        ex = etree.SubElement(exceptionsFileElt,'exception')
        ex.text = str(e)
        logging.warning(("while iterating over PDF objects: {}").format(str(e)))

    # Check for optional content layers
    optionalContentElt = etree.Element("containsOptionalContent")
    optionalContentElt.text = str(False)
    optionalContent = doc.layer_ui_configs()
    if len(optionalContent) != 0:
        optionalContentElt.text = str(True)


    # Wrapper element for pages output
    pagesElt = etree.Element("pages")

    pageNo = 1
    for page in doc:
        pageElt = getPageProperties(doc, page, pageNo)
        # Add page element to pages element
        pagesElt.append(pageElt)
        pageNo += 1

    # Add all remaining elements to properties element
    propertiesElt.append(metadataElt)
    propertiesElt.append(pageModeElt)
    propertiesElt.append(linearizedElt)
    propertiesElt.append(signatureElt)
    propertiesElt.append(optionalContentElt)
    propertiesElt.append (javaScriptElt)
    noPagesElt = etree.Element("noPages")
    noPagesElt.text = str(pages)
    propertiesElt.append(noPagesElt)
    propertiesElt.append(pagesElt)
    propertiesElt.append(annotsElt)
    propertiesElt.append(exceptionsFileElt)

    return propertiesElt


def getPageProperties(doc, page, pageNo):
    """Extract properties for one page and return result as Element object"""

    # Create element object to store all page level properties
    pageElt = etree.Element("page")
    pageElt.attrib["number"] = str(pageNo)

    # Iterate over all images on this page
    images = page.get_images(full=False)
    for image in images:
        imageElt = getImageProperties(doc, image, pageNo)
        # Add image element to page element
        pageElt.append(imageElt)

    # Check for watermark annotations, which somehow are exclude from document-level check
    # Source: https://github.com/pymupdf/PyMuPDF/discussions/1855#discussioncomment-3324039

    # Element object for storing annotation types
    annotsElt =  etree.Element("annotations")
    page.clean_contents()

    xref = page.get_contents()[0]  # get xref of resulting /Contents object
    cont = bytearray(page.read_contents())  # read the contents source as a (modifyable) bytearray
    if cont.find(b"/Subtype/Watermark") > 0:  # this will confirm a marked-content watermark is present
        annotElt = etree.SubElement(annotsElt,'annotation')
        annotElt.text = "/Watermark"

    pageElt.append(annotsElt)

    # Element with number of text characters
    textLengthElt = etree.Element("textLength")
    text = page.get_text()
    textLengthElt.text = str(len(text))
    pageElt.append(textLengthElt)

    return pageElt


def getImageProperties(doc, image, pageNo):
    """Extract image properties and return result as Element object"""

    # Create element object to store all image level properties
    imageElt = etree.Element("image")

    # Extract dictionary-level properties
    propsDictElt = getImageDictProperties(image, pageNo)

    # Check xref and filter values
    # TODO: in case of multiple Filter values, e.g.:
    #  /Filter [ /ASCII85Decode /DCTDecode ]
    # PyMuPDF only returns the first one, which means
    # check on DCTDecode value will fail! 
    xref = int(propsDictElt.find('xref').text)
    filter = propsDictElt.find('filter').text

    # Get raw stream data
    streamRaw = doc.xref_stream_raw(xref)

    # Decode stream if necessary (TODO: perhaps add support for
    # AsciiHexDecode, LZWDecode and FlateDecode filters?)
    if filter == "ASCII85Decode":
        stream = base64.a85decode(streamRaw, adobe=True)
    else:
        stream = streamRaw

    # Extract stream properties
    propsStreamElt = getImageStreamProperties(stream, pageNo)

    # Add properties to image element
    imageElt.append(propsDictElt)
    imageElt.append(propsStreamElt)

    return imageElt


def getImageDictProperties(image, pageNo):
    """Extract image dictionary properties and return result as Element object"""

    # Store properties at PDF object dictionary level to a dictionary
    propsDict = {}
    propsDict['xref'] = image[0]
    #propsDict['smask'] = image[1]
    propsDict['width'] = image[2]
    propsDict['height'] = image[3]
    propsDict['bpc'] = image[4]
    propsDict['colorspace'] = image[5]
    propsDict['altcolorspace'] = image[6]
    #propsDict['name'] = image[7]
    propsDict['filter'] = image[8]

    # Dictionary to element object
    propsDictElt = dictionaryToElt('dict', propsDict)

    return propsDictElt


def getImageStreamProperties(stream, pageNo):
    """Extract image stream properties and return result as Element object"""

    # Dictionary for storing stream properties
    propsStream = {}
    # Element for storing stream-level exceptions
    exceptionsStreamElt = etree.Element("exceptions")

    try:
        im = PIL.Image.open(io.BytesIO(stream))
        im.load()
    except Exception as e:
        ex = etree.SubElement(exceptionsStreamElt,'exception')
        ex.text = str(e)
        propsStreamElt = dictionaryToElt('stream', propsStream)
        propsStreamElt.append(exceptionsStreamElt)
        logging.warning(("page {} while reading image stream: {}").format(str(pageNo), str(e)))
        return propsStreamElt

    propsStream['format'] = im.format
    width = im.size[0]
    height = im.size[1]
    propsStream['width'] = width
    propsStream['height'] = height
    propsStream['mode'] = im.mode
    noComponents = len(im.getbands())
    propsStream['components']= noComponents
    bitsPerComponent = getBPC(im)
    propsStream['bpc'] = bitsPerComponent

    if im.format == "JPEG":
        try:
            # Estimate JPEG quality using least squares matching
            # against standard quantization tables
            quality, rmsError, nse = jpegquality.computeJPEGQuality(im)
            propsStream['JPEGQuality'] = quality
            propsStream['NSE_JPEGQuality'] = nse
        except Exception as e:
            ex = etree.SubElement(exceptionsStreamElt,'exception')
            ex.text = str(e)
            logging.warning(("page {} while estimating JPEG quality from image stream: {}").format(str(pageNo), str(e)))

    for key, value in im.info.items():
        if isinstance(value, bytes):
            propsStream[key] = 'bytestream'
        elif key == 'dpi' and isinstance(value, tuple):
            propsStream['ppi_x'] = value[0]
            propsStream['ppi_y'] = value[1]
        elif key == 'jfif_density' and isinstance(value, tuple):
            propsStream['jfif_density_x'] = value[0]
            propsStream['jfif_density_y'] = value[1]
        elif isinstance(value, tuple):
            # Skip any other properties that return tuples
            pass
        else:
            propsStream[key] = value

    # ICC profile name and description
    iccFlag = False
    try:
        icc = im.info['icc_profile']
        iccFlag = True
    except KeyError:
        pass

    if iccFlag:
        try:
            iccProfile = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            propsStream['icc_profile_name'] = ImageCms.getProfileName(iccProfile).strip()
            propsStream['icc_profile_description'] = ImageCms.getProfileDescription(iccProfile).strip()
        except Exception as e:
            ex = etree.SubElement(exceptionsStreamElt,'exception')
            ex.text = str(e)
            logging.warning(("page {} while extracting ICC profile properties from image stream: {}").format(str(pageNo), str(e)))

    propsStreamElt = dictionaryToElt('stream', propsStream)
    propsStreamElt.append(exceptionsStreamElt)

    return propsStreamElt
