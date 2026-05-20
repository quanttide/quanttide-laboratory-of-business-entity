from src.reporters.abstraction import run


class TestAbstraction:
    def test_all_ontologies_pass_abstraction(self):
        result = run()
        assert result == 0
