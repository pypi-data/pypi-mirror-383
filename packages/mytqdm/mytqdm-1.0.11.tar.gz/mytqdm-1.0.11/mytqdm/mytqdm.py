from typing import Optional, Any, Iterable
from tqdm import tqdm
import requests
import logging

class mytqdm(tqdm):
    
    PROGRESS_URL = "https://mytqdm.app/api/v1/p"
    
    def __init__(
        self,
        iterable: Optional[Iterable[Any]] = None,
        *,
        api_key: str = None,
        title: Optional[str] = None,
        **kwargs: Any
    ):
        self.api_key = api_key
        self.title = title
        super().__init__(iterable=iterable, **kwargs)
        
    def update(self, n: int = 1) -> bool:
        displayed = super().update(n)
        current = self.n
        total = self.total    
        if displayed:
            headers = {
                "Authorization": f"X-API-Key {self.api_key}",
                "Accept": "application/json",
            }
            payload = {
                "title": self.title,
                "current": current,
                "total": total,
            }
            try:
                resp = requests.post(self.PROGRESS_URL, json=payload, headers=headers, timeout=10)
                if resp.ok:
                    logging.debug("mytqdm state successfully updated.")
                else:
                    logging.warning(f"Got non-ok response from mytqdm {resp.status_code}")
            except requests.exceptions.Timeout:
                logging.error("The request to mytqdm.app timed out (connect or read).")
            except requests.exceptions.RequestException as e:
                logging.error(f"An error occured when updating mytqdm state: {e}")

        return displayed
