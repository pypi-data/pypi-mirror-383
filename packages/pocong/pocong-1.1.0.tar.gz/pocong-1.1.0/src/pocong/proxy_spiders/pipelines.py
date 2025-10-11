collected_items = []


class Pipelines:
    def process_item(self, item, spider):
        collected_items.append(dict(item))
        return item
