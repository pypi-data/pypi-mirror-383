from lark import Transformer, Token
class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent
    def define(self, name, value):
        self.vars[name] = value
    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Error (sin): Variable '{name}' not defined.")
    def set(self, name, value):
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent:
            self.parent.set(name, value)
            return
        raise NameError(f"Error (sin): Cannot assign to undefined variable '{name}'.")
class SinInterpreter(Transformer):
    def __init__(self):
        super().__init__()
        self.env = Environment()
        self.should_exit_block = False
    def NUMBER(self, token):
        return int(token.value)    
    def STRING(self, token):
        return token.value.strip('"')
    def get_value(self, item):        
        if isinstance(item, Token) and item.type == 'NAME':
            return self.env.get(item.value)
        return item

    def sum(self, items):
        
        items = [self.get_value(item) for item in items]
        result = items[0]
        for op, operand in zip(items[1::2], items[2::2]):
            if op == '+': result += operand
            elif op == '-': result -= operand
        return result

    def product(self, items):       
        items = [self.get_value(item) for item in items]
        result = items[0]
        for op, operand in zip(items[1::2], items[2::2]):
            if op == '*': result *= operand
            elif op == '/': result /= operand
        return result
    def var_decl(self, items):
        name = items[0].value
        value = self.get_value(items[1]) 
        self.env.define(name, value)
    def assignment(self, items):
        name = items[0].value
        value = self.get_value(items[1])
        self.env.set(name, value)

    def print_stmt(self, items):
        print(self.get_value(items[0]))

    def block(self, statements):
        old_env = self.env
        self.env = Environment(old_env)
        
        for statement in statements:
            if isinstance(statement, str):
                continue
            
            if self.should_exit_block:
                break
            
            statement

        self.env = old_env
        return None

    def if_stmt(self, items):
        condition_result = items[0]
        true_block = items[1]
        false_block = items[2] if len(items) > 2 else None

        if self.get_value(condition_result):
            true_block
        elif false_block:
            false_block
        
        return None

    def condition(self, items):
        left = self.get_value(items[0])
        
        if len(items) == 1:
            return bool(left)
        
        comparator_op = items[1]
        right = self.get_value(items[2])
        
        if comparator_op == '==': return left == right
        if comparator_op == '!=': return left != right
        if comparator_op == '<': return left < right
        if comparator_op == '>': return left > right
        if comparator_op == '<=': return left <= right
        if comparator_op == '>=': return left >= right
        
        return False

    def start(self, statements):
        for statement in statements:
             if isinstance(statement, str):
                continue
             statement
        return self.env
