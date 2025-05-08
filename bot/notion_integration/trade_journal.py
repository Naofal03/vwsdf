import requests

def log_trade_to_notion(api_key, database_id, trade_data):
    url = f"https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "Trade": {"title": [{"text": {"content": trade_data['trade']}}]},
            "Result": {"rich_text": [{"text": {"content": trade_data['result']}}]},
        },
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code