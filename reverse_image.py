import requests
import uuid
import lxml
import lxml.html
import lxml.html.clean
import lxml.cssselect
import cssutils
import re
import logging
from util import cache

cssutils.log.setLevel(logging.FATAL)

@cache()
def get_results(local_image_path, bucket):
    image_url = _upload_to_s3(local_image_path, bucket)
    # fake the user agent so we actually get results
    user_agent = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'}
    r = requests.get("http://images.google.com/searchbyimage", params={'image_url': image_url}, headers=user_agent)

    html = lxml.html.document_fromstring(r.text)
    # we only want these parts of the results page
    selectors_to_keep = ["#ostyle", "#gstyle", "#cst style", "#cst style:nth-of-type(9)", "#_css0", "#topstuff .qb-bmqc", "#search", "#xfoot > script"]
    search_results = ""
    for selector in selectors_to_keep:
        sel = lxml.cssselect.CSSSelector(selector)
        matches = sel(html)
        if len(matches):
            # for each set of matches, just take the first one and clean it up
            search_results += _clean_html(matches[0])
    return search_results

def _upload_to_s3(local_image_path, bucket):
    k = bucket.new_key(str(uuid.uuid4()))
    k.set_contents_from_filename(local_image_path)
    # only hardcode metadata if we can guarantee the image type we're getting
    k.set_metadata('Content-Type', 'image/jpeg')
    k.make_public()
    url = k.generate_url(expires_in=300, query_auth=False, force_http=True)
    return url

def _clean_html(element):
    if element.tag == "style":
        css = cssutils.parseString(element.text_content())
        for rule in css:
            try:
                for sel in rule.selectorList:
                    # prefix all id and class selectors with google-
                    sel.selectorText = sel.selectorText.replace(".", ".google-")
                    sel.selectorText = sel.selectorText.replace("#", "#google-")
                    # add #resultsFrame in front of every selector (beware of comma-separated parts)
                    selectors = sel.selectorText.split(",")
                    selectors = ["#resultsFrame %s" % s.strip() for s in selectors]
                    sel.selectorText = ", ".join(selectors)
            except:
                pass
        return "<style>%s</style>" % css.cssText
    elif element.tag == "script":
        return lxml.html.tostring(element)
    else:
        # monkeypatch from http://stackoverflow.com/questions/15386605/lxml-cleaner-to-ignore-base64-image
        # this prevents lxml from removing the data:image
        new_pattern = '\s*(?:javascript:|jscript:|livescript:|vbscript:|data:[^(?:image/.+;base64)]+|about:|mocha:)'
        lxml.html.clean._javascript_scheme_re = re.compile(new_pattern, re.I)

        cleaner = lxml.html.clean.Cleaner()
        cleaner.style = False
        cleaner.safe_attrs_only = False
        clean = cleaner.clean_html(element)
        for e in clean.iter():
            # prefix all ids and classes with google-
            if 'id' in e.attrib:
                e.attrib['id'] = 'google-' + e.attrib['id']
            if 'class' in e.attrib:
                # beware of elements with multiple space-separated classes
                classes = e.attrib['class'].split(" ")
                classes = ["google-%s" % c.strip() for c in classes]
                e.attrib['class'] = " ".join(classes)
        return lxml.html.tostring(clean)
