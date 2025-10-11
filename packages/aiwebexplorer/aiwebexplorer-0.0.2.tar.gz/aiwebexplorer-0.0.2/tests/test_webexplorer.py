from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Evaluator, EvaluatorContext

from aiwebexplorer.webexplorer import WebExplorer


async def wikipedia_extraction():
    case1 = Case(
        name="simple_extraction",
        inputs="During the first flight, at what second of the countdown, the The ground Launch Processing System handed control to the onboard computer? https://en.wikipedia.org/wiki/Space_Shuttle",  # noqa
        expected_output="The Ground Launch Processing System handed control over to the orbiter’s onboard computer (GPCS) at **t − 31 seconds** into the countdown. ",  # noqa
    )

    class Evaluator1(Evaluator):
        def evaluate(self, ctx: EvaluatorContext) -> float:
            output = ctx.output.content.lower()
            expected_output = ctx.expected_output.lower()
            if output == expected_output:
                return 1.0

            if (
                "t − 31 seconds"
                or "t-31 seconds"
                or "t- 31 seconds"
                or "t -31 seconds"
                or "t minus 31 seconds" in output
            ):
                return 0.8

            if "31 seconds" or "31 sec" in output:
                return 0.6

            if "31" in output:
                return 0.4

            return 0.0

    dataset = Dataset(cases=[case1], evaluators=[Evaluator1()])

    webexplorer = WebExplorer()
    report = await dataset.evaluate(webexplorer.arun)
    report.print(include_input=True, include_output=True)


async def amazon_extraction():
    case2 = Case(
        name="amazon_extraction",
        inputs="""
        Tell me the name, the description and the price of this product: https://www.amazon.com/Apple-iPhone-15-128GB-Black/dp/B0CMPMY9ZZ/
        Generate an exhaustive list of the product's features.
        """,
        expected_output="""
        Apple iPhone 15 (128GB) - Black
        """,
    )

    class Evaluator2(Evaluator):
        def evaluate(self, ctx: EvaluatorContext) -> float:
            output = ctx.output.content.lower()
            score = 0.0

            if "apple iphone 15" in output:
                score += 0.1

            if "apple a16 bionic" in output:
                score += 0.1

            if "8gb" in output:
                score += 0.1

            if "504" in output:
                score += 0.1

            if "128gb" in output:
                score += 0.1

            if "black" in output:
                score += 0.1

            if "renewed" in output:
                score += 0.01

            if "6.1 inches" in output:
                score += 0.01

            if "60 Hz" in output:
                score += 0.01

            if "super retina xdr" in output:
                score += 0.01

            return score

    dataset = Dataset(cases=[case2], evaluators=[Evaluator2()])

    webexplorer = WebExplorer(use_lightweight_fetch=False)
    report = await dataset.evaluate(webexplorer.arun)
    report.print(include_input=True, include_output=True)


if __name__ == "__main__":
    import asyncio

    def test():
        # asyncio.run(wikipedia_extraction())
        asyncio.run(amazon_extraction())

    test()
