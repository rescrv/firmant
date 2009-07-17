try:
    from lxml import etree
except ImportError: # pragma: no cover
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree
    except ImportError:
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree
                except ImportError:
                    raise

def add_text_subelement(root, name, text):
    new = etree.SubElement(root, name)
    new.text = text
