__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import warnings
import os

warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 

from page_config import setup_page_config, create_main_header, initialize_session_state
from sidebar_components import create_sidebar
from scraping_handler import create_scraping_interface, handle_scraping, check_and_display_results
from content_tabs import create_content_tabs


def main():
    setup_page_config()
    initialize_session_state()
    create_main_header()
    create_sidebar()
    
    page_name, scrape_clicked = create_scraping_interface()
    handle_scraping(page_name, scrape_clicked)
    text_content, current_page = check_and_display_results()
    
    if text_content and current_page:
        create_content_tabs(text_content, current_page)


if __name__ == "__main__":
    main()
