from abc import ABC, abstractmethod

from foxypack.answers import AnswersStatistics, AnswersAnalysis


class FoxyStat(ABC):
    @abstractmethod
    def get_stat(self, answers_analysis: AnswersAnalysis) -> AnswersStatistics | None:
        pass

    @abstractmethod
    async def get_stat_async(
        self, answers_analysis: AnswersAnalysis
    ) -> AnswersStatistics | None:
        pass
