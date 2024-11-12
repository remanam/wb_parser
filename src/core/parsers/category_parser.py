class CategoryParser:
    def __init__(self):
        self.session = requests.Session()

    def get_categories_from_url(self):
        try:
            response = self.session.get(url=CATEGORIES_URL)
            assert response.status_code == 200
            response = response.json()
        except:
            raise Exception("Не удалось получить категории")

        categories = []
        for item in response:

            # Добавляем корневую категорию
            categories.append(item)

            # Если есть ПОДКАТЕГОРИИ уровень 1
            if item.get("childs") is not None:
                childs_level1 = item.get("childs")

                # Добавляем подкатегории также
                for child1 in childs_level1:
                    categories.append(child1)

                    # Если есть ПОДКАТЕГОРИИ уровень 2
                    if child1.get("childs") is not None:
                        childs_level2 = child1.get("childs")

                        # Добавляем подкатегории также
                        for child2 in childs_level2:
                            categories.append(child2)

                            # Если есть ПОДКАТЕГОРИИ уровень 3
                            if child2.get("childs") is not None:
                                childs_level3 = child2.get("childs")

                                for child3 in childs_level3:
                                    categories.append(child3)

                                    # Если есть ПОДКАТЕГОРИИ уровень 4
                                    if child3.get("childs") is not None:
                                        childs_level4 = child3.get("childs")

                                        for child4 in childs_level4:
                                            categories.append(child4)

        return categories