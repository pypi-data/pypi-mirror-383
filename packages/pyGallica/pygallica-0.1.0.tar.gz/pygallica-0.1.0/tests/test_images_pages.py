from httpx import Response

def test_get_thumbnail(client, router):
    ark = "ark:/12148/bpt6k000001"
    url = f"https://gallica.bnf.fr/iiif/{ark}/f1/full/200,/0/default.jpg"
    router.get(url).mock(return_value=Response(200, content=b"JPEGDATA"))
    img = client.get_thumbnail(ark, page=1, max_width=200)
    assert isinstance(img, bytes)
    assert img.startswith(b"JPEG")

def test_get_page_image(client, router):
    ark = "ark:/12148/bpt6k000001"
    url = f"https://gallica.bnf.fr/iiif/{ark}/f2/full/1000,/0/default.jpg"
    router.get(url).mock(return_value=Response(200, content=b"IMG"))
    data = client.get_page_image(ark, page=2, max_width=1000)
    assert data == b"IMG"
