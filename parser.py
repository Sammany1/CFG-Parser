from graphviz import Digraph

class CFGParser:
    def __init__(self, grammar_text):
        self.grammar = {}
        self.start_symbol = None
        self.parse_grammar(grammar_text)

    def parse_grammar(self, text):
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines:
            if '->' not in line:
                raise ValueError(f"Malformed grammar line: '{line}'. Each line must contain '->'.")
            left, right = line.split("->")
            left = left.strip()
            productions = []

            for r in right.split("|"):
                tokens = r.strip().split()
                if tokens == ["ε"]:
                    productions.append([])  # empty production
                else:
                    productions.append(tokens)

            if not self.start_symbol:
                self.start_symbol = left
            if left not in self.grammar:
                self.grammar[left] = []
            self.grammar[left].extend(productions)

    def derive(self, input_tokens):
        path = []
        success = self._match(self.start_symbol, input_tokens, 0, path)
        return success is not None, path if success is not None else []

    def _match(self, symbol, tokens, index, path):
        if symbol not in self.grammar:
            # Terminal symbol
            if index < len(tokens) and tokens[index] == symbol:
                return index + 1
            return None

        for production in self.grammar[symbol]:
            curr_index = index
            sub_path = []
            valid = True

            for sym in production:
                result = self._match(sym, tokens, curr_index, sub_path)
                if result is None:
                    valid = False
                    break
                curr_index = result

            if valid:
                path.append((symbol, production))
                path.extend(sub_path)
                return curr_index

        return None

    def generate_parse_tree(self, path):
        dot = Digraph()
        counter = [0]

        def add_node(parent, label):
            node_id = f"node{counter[0]}"
            dot.node(node_id, label)
            if parent:
                dot.edge(parent, node_id)
            counter[0] += 1
            return node_id

        def build_tree(parent, symbol_path):
            if not symbol_path:
                return
            left, right = symbol_path[0]
            node = add_node(parent, left)
            for sym in right:
                add_node(node, sym)
            build_tree(node, symbol_path[1:])

        build_tree(None, list(reversed(path)))
        return dot

    def get_derivation_steps(self, path):
        derivation = [self.start_symbol]

        for (nonterminal, production) in path:
            current = derivation[-1].split()

            for i, symbol in enumerate(current):
                if symbol == nonterminal:
                    if production:
                        current = current[:i] + production + current[i+1:]
                    else:
                        current = current[:i] + current[i+1:]
                    break

            derivation.append(" ".join(current) if current else "ε")

        return derivation
