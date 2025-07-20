class CodeOptimizer:
    """代码优化器"""
    def __init__(self):
        self.optimizations = []
        
    def register_optimization(self, optimization):
        """注册优化策略"""
        self.optimizations.append(optimization)
        
    def optimize_code(self, code: str) -> str:
        """优化生成的代码"""
        for opt in self.optimizations:
            code = opt.apply(code)
        return code 