class DeprectorError(Exception):
    pass


class CollectError(DeprectorError):
    pass


class NoTestsCollected(CollectError):
    pass


class AnalyzeError(DeprectorError):
    pass
