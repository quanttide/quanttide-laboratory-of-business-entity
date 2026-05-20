from pathlib import Path
from src.config import DATA_DIR
from src.loader import load_all_domains


class TestLoader:
    def test_load_all_domains(self):
        domains = load_all_domains(DATA_DIR)
        assert len(domains) == 4
        names = {d[1].id for d in domains}
        assert names == {"biz-ops", "doc-std", "hr", "org-gov"}

    def test_each_domain_has_required_files(self):
        for d, domain, ontologies, instances, relations in load_all_domains(DATA_DIR):
            assert len(ontologies) >= 1
            assert len(instances) >= 1
