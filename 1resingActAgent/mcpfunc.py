from serpapi import SerpApiClient
import os
import dotenv
dotenv.load_dotenv()

def search(query:str) -> str:
    print(f"Searching for: {query}")
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            raise ValueError("SERPAPI_API_KEY not found in environment variables.")
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "gl": "DE",
            "hl": "en"
        }
        client = SerpApiClient(params)
        results = client.get_dict()
        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]
        if "organic_results" in results and results["organic_results"]:
            # 如果没有直接答案，则返回前三个有机结果的摘要
            snippets = [
                f"[{i+1}] {res.get('title', '')}\n{res.get('snippet', '')}"
                for i, res in enumerate(results["organic_results"][:3])
            ]
            return "\n\n".join(snippets)
        return "No relevant information found."
    except Exception as e:
        print(f"Error during search: {e}")
        return "Error occurred during search."
        
