import requests
import json
import os
from google import genai
import dotenv
import markdown
import random
import re

dotenv.load_dotenv(dotenv_path='.env')



GEMINI_API_KEY = dotenv.get_key(key_to_get="GEMINI_API_KEY", dotenv_path='.env') 
print(GEMINI_API_KEY)
GEMINI_API_URL = "https://api.gemini.com/v1/completions"
client = genai.Client(api_key=GEMINI_API_KEY)


WORDPRESS_API_URL = "https://bitcurious.in/wp-json/wp/v2/posts" 
WORDPRESS_USER = "admin"  
WORDPRESS_PASSWORD = dotenv.get_key(key_to_get="WORDPRESS_PASSWORD", dotenv_path='.env') 
TOPICFILE = 'existing_topics.txt'

print(WORDPRESS_PASSWORD)

def clean_json_response(text):
    """Cleans and extracts JSON from AI-generated text."""
    # Remove any extra text before or after JSON
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        json_text = match.group(0)
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            print("Error: JSON response is malformed.")
            return None
    else:
        print("Error: No valid JSON found in response.")
        return None

def generate_blog_post(topic):
    """Generates a blog post using the Gemini API."""
    PROMPT_CONTENT_V1 = f"""
        Write a structured blog post on the topic: {topic}

        ## Format:
        - Use **Markdown** for headings and formatting.
        - Title: `# Blog Post Title`
        - Headings: `## Heading`
        - Subheadings: `### Subheading`
        - Include code snippets inside triple backticks (` ``` `) for syntax highlighting.
        - Use bullet points for lists.
        - End with a conclusion.
        - Make sure the response only contains ASCII-readable text, no special characters.

        ## Return Format:
        ```json
        {{
            "Title": "{topic}",
            "Content": "Full blog post in Markdown format"
        }}
        ```
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=PROMPT_CONTENT_V1,
    )

    text = response.text.strip()
    print("Raw AI Response:", text)

    return clean_json_response(text)

def get_categories():
    response = requests.get('https://bitcurious.in/wp-json/wp/v2/categories')
    return response.json()


def generate_ideas_for_blog(categories, existing_topics):
    ideas = []
    for category in categories:
        PROMPT_IDEAS_V1 = f"""
        Generate only 1 unique and engaging blog post idea related to {category["name"]}.
        Avoid repeating these topics: {existing_topics}.

        Each idea should be:
        - Relevant for 2024 and beyond.
        - Useful for programmers, cybersecurity experts, or DevOps professionals.
        - SEO-friendly.
        - Response should only contain ASCII-readable characters.
        - Category names are case-sensitive and should match exactly.
        - Unique, short, and catchy.

        ## Return Format:
        ```json
        {{
            "category": "{category["name"]}",
            "categoryId": "{category["id"]}",
            "idea": "idea title"
        }}
        ```
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=PROMPT_IDEAS_V1,
        )

        text = response.text.strip()
        print("Raw Idea Response:", text)

        idea_json = clean_json_response(text)
        if idea_json:
            ideas.append(idea_json)

    return ideas
def post_to_wordpress(title, content, category):
    """Posts the generated blog post to WordPress."""

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        'title': markdown.markdown(title),
        'content': markdown.markdown(content, extensions=['fenced_code', 'codehilite']),
        'categories': str(category),
        'status': 'publish'  
    }

    response = requests.post(
        WORDPRESS_API_URL,
        headers=headers,
        json=data,
        auth=(WORDPRESS_USER, WORDPRESS_PASSWORD)
    )
    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    topic = "What are closures?"
    keywords = "javascript, typescript, closures"  
    categories = get_categories()
    categories = random.sample(categories, 5)
    
    
    existing_topics = []
    if not os.path.exists(TOPICFILE):
        with open(TOPICFILE, 'w') as file:
            print("File created")
    with open(TOPICFILE, 'r') as file:
        existing_topics = [line.strip() for line in file]
    try:
        blog_post_ideas = generate_ideas_for_blog(categories=categories, existing_topics=existing_topics)
        print(blog_post_ideas)

        if not blog_post_ideas:
            print("Error: No blog ideas generated.")
            exit(1)  # Stop execution

        with open(TOPICFILE, 'a') as file:
            for ideas in blog_post_ideas:
                file.write(ideas['idea'] + "\n")

        for ideas in blog_post_ideas:
            blog_post_content = generate_blog_post(ideas["idea"])

            if not blog_post_content:
                print(f"Skipping {ideas['idea']} due to generation error.")
                continue  # Skip this iteration

            title = blog_post_content['Title']
            wordpress_response = post_to_wordpress(title, blog_post_content['Content'], ideas['categoryId'])
            print(f"Blog post published successfully! ID: {wordpress_response['id']}")

    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON error: {e}")
    except Exception as e:  
        print(f"Unexpected error: {e}")
