from src.reporters.summary import run


class TestSummary:
    def test_summary_outputs(self):
        result = run()
        assert result == 0
