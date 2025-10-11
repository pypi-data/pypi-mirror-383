from ..metric.reformulation import create_reformulations
from ..metric.ter_computation import compute_scores

from ..config import get_api_key, require_api_key

class Scorer:
    def __init__(self, df, version, api_key=None):
        self.version = version
        self.api_key = api_key or get_api_key(self.model["api"])
        self.df = df
            
    def reformulation(self):
        api_key = self.api_key or require_api_key(self.model["api"])
        self.df = create_reformulations(self.df, self.version, api_key)
        return
    
    def scoring(self):
        self.df = compute_scores(self.df, self.version)
        return
    
    def save(self, path):
        self.df.to_csv(path, index=False)
        return