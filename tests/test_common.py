from wtw import __version__


def test_default(client):
    response = client.get('/')
    assert response.get_json() == {'version': __version__}
