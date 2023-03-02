import itertools

memory = {}


class CallbackData:
    new_id = itertools.count()

    def __init__(self, prefix, action=None, zone_id=None, record_id=None):
        self.id = next(CallbackData.new_id)
        self.prefix = prefix
        self.action = action
        self.zone_id = zone_id
        self.record_id = record_id

        memory[str(self.id)] = {"action": action,
                                "zone_id": zone_id,
                                "record_id": record_id}

    def __call__(self) -> str:
        return "_".join([self.prefix, str(self.id)])

    @staticmethod
    def get_from_memory(memory_id):
        raw = memory[str(memory_id)]
        action = raw['action']
        zone_id = raw['zone_id']
        record_id = raw['record_id']

        return {"action": action,
                "zone_id": zone_id,
                "record_id": record_id}
