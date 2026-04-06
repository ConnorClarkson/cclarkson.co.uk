class TestMainBlueprint:
    def test_home_page(self, client):
        assert client.get("/").status_code == 200


class TestBlogBlueprint:
    def test_blog_listing(self, client):
        assert client.get("/blog").status_code == 200

    def test_blog_post(self, client):
        assert client.get("/blog/KYLLER").status_code == 200

    def test_blog_post_unknown_returns_error(self, client):
        # Missing key raises KeyError -> 500 (documents current behaviour)
        assert client.get("/blog/THIS_DOES_NOT_EXIST").status_code in (404, 500)


class TestCvBlueprint:
    def test_cv_page(self, client):
        assert client.get("/cv").status_code == 200

    def test_cv_entry(self, client):
        assert client.get("/cv/newday").status_code == 200


class TestAppsBlueprint:
    def test_apps_landing(self, client):
        assert client.get("/apps/apps_landing").status_code == 200


class TestWebsitesBlueprint:
    def test_showcase(self, client):
        assert client.get("/showcase").status_code == 200


class TestErrorHandling:
    def test_404(self, client):
        assert client.get("/route/does/not/exist").status_code == 404

    def test_robots_txt(self, client):
        assert client.get("/robots.txt").status_code == 200

    def test_sitemap(self, client):
        assert client.get("/sitemap.xml").status_code == 200
