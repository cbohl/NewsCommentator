import re

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase

FORBIDDEN_PHRASES = [
    "In conclusion,",
    "It is important to note,",
    "As an AI,",
    "It's worth noting,",
    "Let's delve into,",
    "In today's world,",
    "This raises questions about",
    "This highlights",
    "In the grand tapestry of history",
]

# Regex for lines that start with bullet/list markers
_LIST_PATTERN = re.compile(r"^\s*(?:[-*•]\s+|\d+\.\s+)", re.MULTILINE)


class WordCountMetric(BaseMetric):
    """Fail if comment exceeds 150 words."""

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.score = None
        self.reason = None
        self.success = None
        self.score_breakdown = None
        self.evaluation_cost = 0

    def measure(self, test_case: LLMTestCase) -> float:
        count = len(test_case.actual_output.split())
        self.score = 1.0 if count <= 150 else 0.0
        self.reason = f"Word count: {count}/150"
        self.success = self.score >= self.threshold
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.score is not None and self.score >= self.threshold

    @property
    def __name__(self):
        return "WordCount"


class ForbiddenPhraseMetric(BaseMetric):
    """Fail if comment contains any forbidden phrase from system_rules.md."""

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.score = None
        self.reason = None
        self.success = None
        self.score_breakdown = None
        self.evaluation_cost = 0

    def measure(self, test_case: LLMTestCase) -> float:
        text = test_case.actual_output
        found = [p for p in FORBIDDEN_PHRASES if p.lower() in text.lower()]
        if found:
            self.score = 0.0
            self.reason = f"Forbidden phrases found: {found}"
        else:
            self.score = 1.0
            self.reason = "No forbidden phrases"
        self.success = self.score >= self.threshold
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.score is not None and self.score >= self.threshold

    @property
    def __name__(self):
        return "ForbiddenPhrase"


class NoBulletPointsMetric(BaseMetric):
    """Fail if comment contains bullet points or numbered lists."""

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.score = None
        self.reason = None
        self.success = None
        self.score_breakdown = None
        self.evaluation_cost = 0

    def measure(self, test_case: LLMTestCase) -> float:
        matches = _LIST_PATTERN.findall(test_case.actual_output)
        if matches:
            self.score = 0.0
            self.reason = f"List markers found: {[m.strip() for m in matches[:3]]}"
        else:
            self.score = 1.0
            self.reason = "No list formatting"
        self.success = self.score >= self.threshold
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.score is not None and self.score >= self.threshold

    @property
    def __name__(self):
        return "NoBulletPoints"


class ToolUsageRateMetric(BaseMetric):
    """Fail if a persona used their tool on fewer than 50% of articles."""

    def __init__(self, total: int, used: int, threshold: float = 0.5):
        self.threshold = threshold
        self.total = total
        self.used = used
        self.score = None
        self.reason = None
        self.success = None
        self.score_breakdown = None
        self.evaluation_cost = 0

    def measure(self, test_case: LLMTestCase) -> float:
        rate = self.used / self.total if self.total > 0 else 0.0
        self.score = 1.0 if rate >= self.threshold else 0.0
        self.reason = f"Tool usage: {self.used}/{self.total} = {rate:.0%}"
        self.success = self.score >= self.threshold
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.score is not None and self.score >= self.threshold

    @property
    def __name__(self):
        return "ToolUsageRate"
