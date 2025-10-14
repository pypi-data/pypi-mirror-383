import json

from django.utils.encoding import smart_str

from django_tomselect2.cache import cache
from django_tomselect2.forms import ModelTomSelectWidget
from tests.testapp.forms import (
    AlbumModelTomSelectWidgetForm,
    ArtistCustomTitleWidget,
    CityForm,
)
from tests.testapp.models import Genre

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


class TestAutoResponseView:
    def test_get(self, client, artists):
        artist = artists[0]
        form = AlbumModelTomSelectWidgetForm()
        assert form.as_p()
        field_id = form.fields["artist"].widget.field_id
        url = reverse("django_tomselect2:auto-json")
        response = client.get(url, {"field_id": field_id, "term": artist.title})
        assert response.status_code == 200
        data = json.loads(response.content.decode("utf-8"))
        assert data["results"]
        assert {"id": artist.pk, "text": smart_str(artist)} in data["results"]

    def test_no_field_id(self, client, artists):
        artist = artists[0]
        url = reverse("django_tomselect2:auto-json")
        response = client.get(url, {"term": artist.title})
        assert response.status_code == 404

    def test_wrong_field_id(self, client, artists):
        artist = artists[0]
        url = reverse("django_tomselect2:auto-json")
        response = client.get(url, {"field_id": 123, "term": artist.title})
        assert response.status_code == 404

    def test_field_id_not_found(self, client, artists):
        artist = artists[0]
        field_id = "not-exists"
        url = reverse("django_tomselect2:auto-json")
        response = client.get(url, {"field_id": field_id, "term": artist.title})
        assert response.status_code == 404

    def test_pagination(self, genres, client):
        url = reverse("django_tomselect2:auto-json")
        widget = ModelTomSelectWidget(
            max_results=10, model=Genre, search_fields=["title__icontains"]
        )
        widget.render("name", None)
        field_id = widget.field_id

        response = client.get(url, {"field_id": field_id, "term": ""})
        assert response.status_code == 200
        data = json.loads(response.content.decode("utf-8"))
        assert data["more"] is True

        response = client.get(url, {"field_id": field_id, "term": "", "page": 1000})
        assert response.status_code == 404

        response = client.get(url, {"field_id": field_id, "term": "", "page": "last"})
        assert response.status_code == 200
        data = json.loads(response.content.decode("utf-8"))
        assert data["more"] is False

    def test_label_from_instance(self, artists, client):
        url = reverse("django_tomselect2:auto-json")

        form = AlbumModelTomSelectWidgetForm()
        form.fields["artist"].widget = ArtistCustomTitleWidget()
        assert form.as_p()
        field_id = form.fields["artist"].widget.field_id

        artist = artists[0]
        response = client.get(url, {"field_id": field_id, "term": artist.title})
        assert response.status_code == 200

        data = json.loads(response.content.decode("utf-8"))
        assert data["results"]
        assert {"id": artist.pk, "text": smart_str(artist.title.upper())} in data[
            "results"
        ]

    def test_result_from_instance(self, cities, client):
        url = reverse("django_tomselect2:auto-json")

        form = CityForm()
        assert form.as_p()
        field_id = form.fields["city"].widget.field_id
        city = cities[0]
        response = client.get(url, {"field_id": field_id, "term": city.name})
        assert response.status_code == 200
        data = json.loads(response.content.decode("utf-8"))
        assert data["results"]
        assert {
            "id": city.pk,
            "text": smart_str(city),
            "country": smart_str(city.country),
        } in data["results"]

    def test_url_check(self, client, artists):
        artist = artists[0]
        form = AlbumModelTomSelectWidgetForm()
        assert form.as_p()
        field_id = form.fields["artist"].widget.field_id
        cache_key = form.fields["artist"].widget._get_cache_key()
        widget_dict = cache.get(cache_key)
        widget_dict["url"] = "yet/another/url"
        cache.set(cache_key, widget_dict)
        url = reverse("django_tomselect2:auto-json")
        response = client.get(url, {"field_id": field_id, "term": artist.title})
        assert response.status_code == 404
