from research_os.classify import classify_one
from research_os.models import Result


def _r(url: str) -> Result:
    r = Result(title="t", url=url, snippet="s")
    r.domain = url.split("//", 1)[1].split("/", 1)[0].removeprefix("www.")
    return r


def test_known_primary_domains():
    assert classify_one(_r("https://arxiv.org/abs/2401.1"))[0] == "primary"
    assert classify_one(_r("https://github.com/org/repo"))[0] == "primary"


def test_tld_pattern_primary_and_secondary():
    assert classify_one(_r("https://nasa.gov/mission"))[0] == "primary"
    cls, sig = classify_one(_r("https://cs.stanford.edu/paper"))
    assert cls == "high_trust_secondary" and sig == "domain_pattern"


def test_community_and_default():
    assert classify_one(_r("https://reddit.com/r/tennis/x"))[0] == "community"
    cls, sig = classify_one(_r("https://some-unknown-blog.example/post"))
    assert cls == "aggregator" and sig == "default"
