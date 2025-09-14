def build_sources(responses):
	sources = []
	for idx, r in enumerate(responses, start=1):
		sources.append({
			"id": f"S{idx}",
			"author": r.get("author", "unknown"),
			"permalink": r.get("permalink", ""),
			"text": r.get("text", "")
		})
	return sources

def format_citation_list(sources):
	lines = []
	for s in sources:
		lines.append(f"[{s['id']}] {s['author']}: {s['permalink']}")
	return "\n".join(lines)

def summarize_with_claude_citations(responses, api_key=None, max_tokens=512):
	sources = build_sources(responses)
	if api_key is None:
		api_key = os.getenv("ANTHROPIC_API_KEY")
	if not api_key:
		raise ValueError("Claude API key not provided. Set ANTHROPIC_API_KEY env variable or pass as argument.")
	all_text = "\n".join([f"[{s['id']}] {s['text']}" for s in sources if s['text']])
	if not all_text.strip():
		return "No content to summarize.", sources
	prompt = (
		"Summarize the following Reddit thread. Use inline citations like [S1], [S2] after statements that are supported by a specific source. "
		"Be concise, neutral, and avoid speculation. At the end, I will provide a citation list for each source.\n\n"
		"Thread content:\n" + all_text
	)
	client = anthropic.Anthropic(api_key=api_key)
	preferred_models = ["claude-3-opus-latest", "claude-3-sonnet-latest", "claude-3-haiku-latest"]
	last_error = None
	for m in preferred_models:
		try:
			message = client.messages.create(
				model=m,
				max_tokens=max_tokens,
				system="You are an expert Reddit thread summarizer.",
				messages=[{"role": "user", "content": prompt}]
			)
			content_piece = message.content[0]
			return content_piece.text if hasattr(content_piece, 'text') else str(content_piece), sources
		except anthropic.APIStatusError as e:
			last_error = f"Model {m} failed ({e.status_code}): {e}"
			if e.status_code == 401:
				return "Authentication failed (401). Verify ANTHROPIC_API_KEY is correct and active.", sources
		except Exception as e:
			last_error = f"Model {m} unexpected error: {e}"
	return f"All model attempts failed. Last error: {last_error}", sources
import requests
from bs4 import BeautifulSoup

def fetch_reddit_thread(url):
	"""
	Fetches the main post and top-level comments from a Reddit thread URL.
	Returns:
		main_post (dict): {'text': ..., 'author': ...}
		comments (list of dict): [{'text': ..., 'author': ...}, ...]
	"""
	if url.endswith('/'):
		url = url[:-1]
	json_url = url + '.json'
	headers = {'User-Agent': 'Mozilla/5.0'}
	response = requests.get(json_url, headers=headers)
	data = response.json()

	# Main post
	post_data = data[0]['data']['children'][0]['data']
	main_post = {
		'text': post_data.get('selftext', '') or post_data.get('title', ''),
		'author': post_data.get('author', '')
	}

	# Top-level comments
	comments = []
	for child in data[1]['data']['children']:
		if child['kind'] == 't1':
			comment_data = child['data']
			body = comment_data.get('body', '')
			score = comment_data.get('score', 0)
			# Filter: must be at least 25 chars, not deleted, and either top 10 by score or contains critical keywords
			critical_keywords = ['not true', 'wrong', 'evidence', 'proof', 'critical', 'important', 'disagree', 'agree', 'fact', 'source']
			is_critical = any(kw in body.lower() for kw in critical_keywords)
			if body and len(body) > 25 and body.lower() not in ('[deleted]', '[removed]'):
				comments.append({
					'text': body,
					'author': comment_data.get('author', ''),
					'permalink': "https://www.reddit.com" + comment_data.get('permalink', ''),
					'score': score,
					'is_critical': is_critical
				})
	# Keep only top 10 by score and all marked critical
	comments_sorted = sorted(comments, key=lambda x: x['score'], reverse=True)
	top_comments = comments_sorted[:10]
	critical_comments = [c for c in comments if c['is_critical'] and c not in top_comments]
	filtered_comments = top_comments + critical_comments
	return main_post, filtered_comments

def summarize_reddit_link(url, api_key = None):
	"""
	Fetches a Reddit thread and summarizes the main post and comments separately using Claude.
	Returns:
		summary_main (str): Paragraph summary of main post.
		summary_comments (str): Paragraph summary of comments.
	"""
	main_post, comments = fetch_reddit_thread(url)
	# Summarize main post
	summary_main = summarize_with_claude([main_post], api_key=api_key) if main_post['text'] else "No main post found."
	# Summarize comments
	summary_comments = summarize_with_claude(comments, api_key=api_key) if comments else "No comments found."
	return summary_main, summary_comments
# Claude API summarization
import os
import anthropic
from typing import Tuple

def validate_claude_key(api_key: str) -> Tuple[bool, str]:
	"""Lightweight validation of Claude API key by hitting a minimal request.
	Returns (is_valid, message)."""
	try:
		client = anthropic.Anthropic(api_key=api_key)
		# Minimal test: ask for a tiny completion
		test_msg = client.messages.create(
			model="claude-3-opus-20240229",
			max_tokens=5,
			messages=[{"role": "user", "content": "ping"}]
		)
		return True, "Key valid"
	except anthropic.APIStatusError as e:
		if e.status_code == 401:
			return False, "Authentication failed (401). Check key value or if revoked."
		return False, f"API status error {e.status_code}: {e}"
	except Exception as e:
		return False, f"Unexpected error validating key: {e}"

def summarize_with_claude(responses, api_key=None, model="claude-opus-4-1-20250805", max_tokens=512):
	"""
	Summarizes Reddit responses using Anthropic Claude API.
	Args:
		responses (list of dict): Each dict contains 'text', 'author', 'permalink', etc.
		api_key (str): Claude API key. If None, will use ANTHROPIC_API_KEY env variable.
		model (str): Claude model name.
		max_tokens (int): Maximum tokens in summary.
	Returns:
		summary (str): Rich summary from Claude.
	"""
	if api_key is None:
		api_key = os.getenv("ANTHROPIC_API_KEY")
	if not api_key:
		raise ValueError("Claude API key not provided. Set ANTHROPIC_API_KEY env variable or pass as argument.")
	# Aggregate text & guard against empty
	all_text = "\n".join([resp.get('text', '') for resp in responses if resp.get('text')])
	if not all_text.strip():
		return "No content to summarize."

	base_prompt = (
		"You are creating a concise yet information-rich summary for a Reddit thread. "
		"Output 1 cohesive paragraph if input is short; otherwise 2 paragraphs: (1) core issue/context, (2) major viewpoints / consensus / disagreements. "
		"Use neutral tone, weave in authors only when it adds clarity. Avoid fluff.\n\n" 
		"Thread content:\n" + all_text
	)
	client = anthropic.Anthropic(api_key=api_key)
	preferred_models = [model, "claude-3-opus-latest", "claude-3-sonnet-latest", "claude-3-haiku-latest"]
	last_error = None
	for m in preferred_models:
		try:
			message = client.messages.create(
				model=m,
				max_tokens=max_tokens,
				system="You are an expert Reddit thread summarizer.",
				messages=[{"role": "user", "content": base_prompt}]
			)
			content_piece = message.content[0]
			return content_piece.text if hasattr(content_piece, 'text') else str(content_piece)
		except anthropic.APIStatusError as e:
			last_error = f"Model {m} failed ({e.status_code}): {e}"
			if e.status_code == 401:
				return "Authentication failed (401). Verify ANTHROPIC_API_KEY is correct and active."
		except Exception as e:
			last_error = f"Model {m} unexpected error: {e}"
	return f"All model attempts failed. Last error: {last_error}"

# ...existing code...

if __name__ == "__main__":
	url = "https://www.reddit.com/r/PublicFreakout/comments/1ndrgqk/suspicious_figure_seen_running_across_roof_of_the/"
	# --- Simple citation-enabled summary ---
	print("\n=== Claude Summarization with Simple Citations ===")
	try:
		main_post, comments = fetch_reddit_thread(url)
		responses = [main_post] + comments
		summary, sources = summarize_with_claude_citations(responses)
		print("\nSummary:\n", summary)
		print("\nCitations:\n", format_citation_list(sources))
	except Exception as e:
		print(f"Claude summarization error: {e}")
	# for testing purposes, replace the following url with another Reddit thread if desired
	url = "https://www.reddit.com/r/PublicFreakout/comments/1ndrgqk/suspicious_figure_seen_running_across_roof_of_the/" 
	print("=== Claude Summarization ===")
	try:
		summary_main, summary_comments = summarize_reddit_link(url)
		print("Main Post Summary:\n", summary_main)
		print("\nComments Summary:\n", summary_comments)
	except Exception as e:
		print(f"Claude summarization error: {e}")
