import nougat

pdf_path = '/Users/subrat_roy/Documents/LLM/try/daddddy.pdf'
math_expressions = nougat.extract(pdf_path)

for expression in math_expressions:
    print(expression)
