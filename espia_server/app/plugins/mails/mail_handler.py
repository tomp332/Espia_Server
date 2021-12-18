import requests

from espia_server.app.utils import config, uploads_path, block

_MAILGUN_CONFIG = config['mailgun']


def send_mail(session_id: str) -> None:
    """
    Send json results to mail
    """
    response = requests.post(
        f"https://api.mailgun.net/v3/{_MAILGUN_CONFIG.get('MAILGUN_DOMAIN')}/messages",
        auth=("api", _MAILGUN_CONFIG.get('API_KEY')),
        files=[("attachment", open(f"{uploads_path}/{session_id}/final_results.json"))],
        data={"from": f"User <{_MAILGUN_CONFIG.get('MAILGUN_USER')}@{_MAILGUN_CONFIG.get('MAILGUN_DOMAIN')}>",
              "to": [_MAILGUN_CONFIG.get('DESTINATION_EMAIL')],
              "subject": "Results",
              "text": f"Your results from {session_id} are ready"})
    response.status_code == 200 and print(block + f"[+] Successfully sent mail for {session_id} results")
