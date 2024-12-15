import requests
import webbrowser

# Константы API
WIKIPEDIA_API_URL = "https://ru.wikipedia.org/w/api.php"

class WikipediaAPI:
    """
    Класс для взаимодействия с API Wikipedia.
    """
    def __init__(self, api_url=WIKIPEDIA_API_URL):
        self.api_url = api_url

    def search_articles(self, query):
        """
        Выполняет запрос к API Wikipedia для поиска статей по запросу.
        Возвращает список найденных заголовков статей.
        """
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "utf8": 1,
        }

        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()

            search_results = data.get("query", {}).get("search", [])
            return [result['title'] for result in search_results]
        except requests.RequestException as e:
            print(f"Ошибка при запросе к Википедии: {e}")
            return []

    def get_article_url(self, title):
        """
        Получает полный URL статьи по её заголовку.
        """
        params = {
            "action": "query",
            "prop": "info",
            "inprop": "url",
            "titles": title,
            "format": "json",
            "utf8": 1,
        }

        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()

            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if page_id != "-1":  # Страница существует
                    return page_data.get("fullurl")
            return None
        except requests.RequestException as e:
            print(f"Ошибка при запросе к Википедии: {e}")
            return None


class WikipediaSearch:
    """
    Класс для поиска статей и отображения результатов.
    """
    def __init__(self, api_client):
        self.api_client = api_client

    def perform_search(self, query):
        """
        Выполняет поиск статей и выводит результаты на консоль.
        Возвращает список заголовков найденных статей.
        """
        search_results = self.api_client.search_articles(query)

        if not search_results:
            print("Результаты не найдены.")
            return []

        print(f"\nНайдено {len(search_results)} результатов:")
        for i, title in enumerate(search_results[:10], start=1):
            print(f"{i}. {title}")

        return search_results[:10]

    def open_article(self, titles):
        """
        Открывает статью в браузере по выбору пользователя.
        """
        while True:
            choice = input("\nВведите номер статьи для открытия (или 'back' для нового поиска): ").strip()
            if choice.lower() == 'back':
                return

            if choice.isdigit() and 1 <= int(choice) <= len(titles):
                selected_title = titles[int(choice) - 1]
                article_url = self.api_client.get_article_url(selected_title)

                if article_url:
                    print(f"Открываем статью '{selected_title}' в браузере...")
                    webbrowser.open(article_url)
                else:
                    print(f"Не удалось найти URL для статьи '{selected_title}'.")
                break
            else:
                print("Неверный ввод. Введите корректный номер статьи или 'back'.")


class WikipediaApp:
    """
    Основной класс приложения для взаимодействия с пользователем.
    """
    def __init__(self):
        self.api_client = WikipediaAPI()
        self.search_client = WikipediaSearch(self.api_client)

    def run(self):
        """
        Запускает приложение и обрабатывает пользовательский ввод.
        """
        print("Поиск по Википедии.")
        while True:
            query = input("\nВведите поисковый запрос (или 'exit' для выхода): ").strip()
            if query.lower() == 'exit':
                print("Завершение работы.")
                break

            titles = self.search_client.perform_search(query)
            if titles:
                self.search_client.open_article(titles)


if __name__ == "__main__":
    try:
        app = WikipediaApp()
        app.run()
    except KeyboardInterrupt:
        print("\nЗавершение работы по команде пользователя.")
