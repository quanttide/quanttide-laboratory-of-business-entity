from src.validators.validate import run


class TestValidate:
    def test_validate_passes(self):
        result = run()
        assert result == 0
