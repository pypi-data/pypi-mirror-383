from pyGallica.parser import parse_sru_xml

SRU_SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<searchRetrieveResponse xmlns="http://www.loc.gov/zing/srw/">
  <version>1.2</version>
  <numberOfRecords>2</numberOfRecords>
  <records>
    <record>
      <recordSchema>dc</recordSchema>
      <recordPacking>xml</recordPacking>
      <recordData>
        <oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
                   xmlns:dc="http://purl.org/dc/elements/1.1/">
          <dc:title>Carte de Paris</dc:title>
          <dc:identifier>ark:/12148/btv1b1234567z</dc:identifier>
          <dc:type>image</dc:type>
          <dc:date>1900</dc:date>
          <dc:language>fre</dc:language>
          <dc:subject>Paris</dc:subject>
        </oai_dc:dc>
      </recordData>
    </record>
    <record>
      <recordSchema>dc</recordSchema>
      <recordData>
        <oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
                   xmlns:dc="http://purl.org/dc/elements/1.1/">
          <dc:title>Vue de Paris</dc:title>
          <dc:identifier>https://gallica.bnf.fr/ark:/12148/btv1b7654321q</dc:identifier>
          <dc:type>image</dc:type>
        </oai_dc:dc>
      </recordData>
    </record>
  </records>
  <nextRecordPosition>3</nextRecordPosition>
</searchRetrieveResponse>
"""

def test_parse_sru_xml_records_and_meta():
    records, meta = parse_sru_xml(SRU_SAMPLE)
    assert meta["numberOfRecords"] == 2
    assert meta["nextRecordPosition"] == 3
    assert len(records) == 2

    r0 = records[0]
    assert r0.ark.startswith("ark:/12148/")
    assert r0.title == "Carte de Paris"
    assert r0.type == "image"
    assert r0.language == "fre"
    assert r0.ark_url.startswith("https://gallica.bnf.fr/ark:/12148/")

    r1 = records[1]
    assert r1.ark.startswith("ark:/12148/")
    assert r1.title == "Vue de Paris"
    assert r1.ark_url == "https://gallica.bnf.fr/ark:/12148/btv1b7654321q"
