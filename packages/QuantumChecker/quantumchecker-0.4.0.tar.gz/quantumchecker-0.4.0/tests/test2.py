import asyncio
from pprint import pprint
from QuantumCheck import HomeworkEvaluator

API_KEY = "AIzaSyDw76DEINpfBVgwIEZLShhy97tvWg7BmzY"

question = "Create a Power BI report with a bar chart.\nExplain DAX measures for sales analysis."
answer_path = "../tests/answer/test.pdf"

async def main():
    evaluator = HomeworkEvaluator()
    evaluation = await evaluator.evaluate_from_content(
        question_content=question,
        answer_path=answer_path,
        api_key=API_KEY,
        question_type="powerbi"
    )

    print(f"PowerBI | {answer_path}")
    print("✅ Evaluation result:")
    pprint(evaluation)
    print("-" * 40)

if __name__ == "__main__":
    asyncio.run(main())
