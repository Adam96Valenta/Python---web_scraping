from script import ScraperHeureka
import time

start_time = time.time()
scraper = ScraperHeureka('https://graficke-karty.heureka.cz/')
driver = scraper.open_driver()
scraper.open_more_pages()
products_list = scraper.get_products_list()
df = scraper.get_all_products(products_list[0:2])
scraper.save_df_to_csv(df, 'Table.csv')
print("--- %s seconds ---" % (time.time() - start_time))

