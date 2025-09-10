
from lib.mongo_connect import MongoDB
import logging
from tqdm import tqdm
from eurosport.update_results import request_and_return_html
log = logging.getLogger(__name__)

if __name__ == "__main__":
    db = MongoDB()
    try:
        result_dict = db.get_matches_url_by_ids_dict()
        print(result_dict)

        html_data_dict = {}
        for key,value in tqdm(result_dict.items()):
            html_data_dict[key] = request_and_return_html(value)

        db.update_matches_html(html_data_dict)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        raise e
    finally:
        db.close()