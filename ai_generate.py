import dotenv
import openai

dotenv.load_dotenv()

PROMPT_IDEAS_V1 = """
Generate 5 unique and highly engaging blog post ideas related to {category}

Avoid repeating these topics: {existing_topics}.

Each idea should be:
- Relevant for 2024 and beyond
- Easy to write without requiring real-time news updates
- Useful for programmers, cybersecurity experts, computer geeks, or DevOps professionals
- Search engine optimized (SEO-friendly)
- Response should contain only ascii readable characters, no other special characters are allowed
- Category names are case-sensitive and should be an exact match

Return the response as a JSON object formatted like this:
{{
  "category": "{category}",
  "ideas": [
    "Blog Idea 1",
    "Blog Idea 2",
    "Blog Idea 3",
    ...
  ]
}}
"""