from abstracts.AAdapter import AAdapter
import json

class JsonAdapter(AAdapter[object, str]):
    @staticmethod
    def Encode(input:object) -> str:
        return json.dumps(input)
    @staticmethod
    def Decode(input:str) -> object:
        return json.loads(input)
