import sys
from typing import Deque, Dict, Set, List, Tuple
from collections import deque

from networkx import DiGraph # type: ignore
from networkx.algorithms.components import strongly_connected_components # type: ignore
from networkx.algorithms.dag import topological_sort # type: ignore

from clingo.ast import parse_string, ProgramBuilder

from clingo import Function

from clingo.control import Control
from clingo.symbol import Symbol
from clingox.backend import SymbolicBackend
from clingox.program import Program,ProgramObserver
from clingox.pprint import pformat,PrettyPrinter

from clingo.application import Application, clingo_main
from clingox.program import Program, ProgramObserver, Rule


import networkx as nx
import matplotlib.pyplot as plt


Atom = int
Literal = int
RuleIndex = int
ctl = Control()


# Returns an ordered list of the rules that are connected
def _analyze(rules: List[Rule]) -> List[List[Rule]]:
    # Create a directed graph (DiGraph)
    G = nx.DiGraph()

    # build rule dependency graph
    occ: Dict[Atom, Set[RuleIndex]] = {}
    dep_graph = DiGraph()
    dep_graph2 = DiGraph()
    # print('enumerate(rules):',len(rules))
    for u, rule in enumerate(rules):
        # print('enumerate(rules) u:',u)
        # print('enumerate(rules) rule:',rule)
        dep_graph.add_node(u)        
        for lit in rule.body:
            occ.setdefault(abs(lit), set()).add(u)

    for u, rule in enumerate(rules):
        atm, = rule.head
        for v in occ.get(atm, []):
            dep_graph.add_edge(u, v)

    # PLOT THE GRAPH    
    # nx.draw(dep_graph, with_labels=True)
    # plt.show(block=True)
    sccs = list(strongly_connected_components(dep_graph))
    

    # build scc dependency graph
    # (this part only exists because the networkx library does not document the
    # order of components; in principle, the tarjan algorithm guarentees a
    # topological order)
    scc_rule: Dict[RuleIndex, RuleIndex] = {}
    scc_graph = DiGraph()
    for i, scc in enumerate(sccs):
        # print('SCC_0')
        scc_graph.add_node(i)

        for u in scc:
            # print('SCC_1')
            scc_rule[u] = i

    for i, scc in enumerate(sccs):
        for u in scc:
            # print('SCC_2')
            for v in dep_graph[u]:
                # print('SCC_3')
                j = scc_rule[u]
                if i != j:
                    scc_graph.add_edge(i, j)


    return [[rules[j] for j in sccs[i]] for i in topological_sort(scc_graph)]


def _well_founded(interpretation: Set[Literal], scc: List[Rule]) -> None:
    watches: Dict[Literal, List[RuleIndex]] = {}
    counters: Dict[RuleIndex, int] = {}
    todo: List[Literal] = []
    unfounded: List[Literal] = []
    need_source: Set[Atom] = set()
    has_source: Set[Atom] = set()
    can_source: Dict[Atom, List[RuleIndex]] = {}
    falses:  Set[Atom] = set()
    counters_source: Dict[RuleIndex, int] = dict()
    todo_source: Deque[Atom] = deque()
    is_source: Set[RuleIndex] = set()

    def is_true(*args):
        return all(lit in interpretation for lit in args)

    def is_false(*args):
        return any(-lit in interpretation for lit in args)

    # def red_plus(*prg,alltheheads):
        
    #     rule_notinheads = [atm.symbol for atm in prg.facts]
    #     return rule_heads



    def is_supported(lit):
        return not is_false(lit) and (lit < 0 or is_true(lit) or lit in has_source)

    def enqueue_source(idx: RuleIndex):
        atm, = scc[idx].head
        if counters_source[idx] == 0 and atm not in has_source:
            has_source.add(atm)
            is_source.add(idx)
            todo_source.append(atm)

    def enqueue_lit(lit: Literal):
        if lit not in interpretation:
            interpretation.add(lit)
            todo.append(lit)

    # initialize the above data structures
    
    for i, rule in enumerate(scc):
        atm, = rule.head
        head_var= rule.head
        body_var= rule.body

                

        if is_false(*rule.body) or is_true(atm):
            continue


        # initialize fact propagation
        count = 0
        for lit in rule.body:
            if not is_true(lit):
                count += 1
                watches.setdefault(lit, []).append(i)
        counters[i] = count
        if count == 0:
            enqueue_lit(atm)

        # initialize source propagation
        count = 0
        for lit in rule.body:
            if not is_supported(lit):
                count += 1
            if abs(lit) not in need_source:
                need_source.add(abs(lit))
                unfounded.append(-abs(lit))
        counters_source[i] = count
        enqueue_source(i)
        can_source.setdefault(atm, []).append(i)

    while todo or unfounded:
        # forward propagate facts
        idx = 0
        while idx < len(todo):
            lit = todo[idx]
            idx += 1
            for i in watches.get(lit, []):
                counters[i] -= 1
                if counters[i] == 0:
                    enqueue_lit(*scc[i].head)

        # remove sources
        idx = 0
        while idx < len(todo):
            lit = todo[idx]
            idx += 1
            # Note that in this case, the literal already lost its source earlier
            # and has already been made false at the end of the loop.
            if lit < 0 and lit in interpretation:
                continue
            for i in watches.get(-lit, []):
                counters_source[i] += 1
                if i in is_source:
                    atm, = scc[i].head
                    is_source.remove(i)
                    has_source.remove(atm)
                    if -atm not in interpretation:
                        todo.append(-atm)

        # initialize sources
        for lit in todo:
            for i in can_source.get(-lit, []):
                enqueue_source(i)

        # forward propagate sources
        while todo_source:
            atm = todo_source.popleft()
            for i in watches.get(atm, []):
                counters_source[i] -= 1
                enqueue_source(i)

        # set literals without sources to false
        if not unfounded:
            unfounded, todo = todo, unfounded
        todo.clear()
        for lit in unfounded:
            if lit < 0 and -lit in need_source and -lit not in has_source:
                enqueue_lit(lit)
        unfounded.clear()

def remove_literal(lit, rule):
    """
    Removes a literal from a rule's body.

    Args:
        lit (str): The literal to remove.
        rule (clingox.Rule): The rule to modify.

    Returns:
        clingox.Rule: The modified rule, or None if the literal was not found.
    """

    new_body = [at for at in rule.body if at.symbol != lit]
    if new_body:
        return Rule(rule.head, new_body)
    else:
        return None  # Literal not found in the rule


def check_literal(lit, rule):

    new_body = [at for at in rule.body if at.symbol != lit]
    if new_body:
        return False #Rule(rule.head, new_body)
    else:
        return True  # Literal not found in the rule

def well_founded(prg: Program) -> Tuple[List[Symbol], List[Symbol]]:
    '''
    Computes the well-founded model of the given program returning a pair of
    facts and unknown atoms.

    This function assumes that the program contains only normal rules.
    '''
    alltheheads: Set[Atom] = set()

    for rule in prg.rules:
        if len(rule.head) != 1 or rule.choice:
            raise RuntimeError('only normal rules are supported')
    if prg.weight_rules:
        raise RuntimeError('only normal rules are supported')

    alltheheads = [atm.symbol for atm in prg.facts]
    prg.output_atoms



    
    # analyze program and compute well-founded model
    interpretation: Set[Literal] = set()
    for scc in _analyze(prg.rules):
        for cc in scc:
            # print("strong connected comp:", PrettyPrinter(cc.body) )        
            _well_founded(interpretation, scc)
            # print('zzzzzzzzzz',prg.pretty_str)
            
   

    occ: Dict[Atom, Set[RuleIndex]] = {}
    dep_graph = DiGraph()


    for u, rule in  enumerate(prg.rules):
        atm, = rule.head
        for v in occ.get(atm, []):
            dep_graph.add_edge(u, v)

    # PLOT THE GRAPH    
    # nx.draw(dep_graph, with_labels=True)
    # plt.show(block=True)

    # compute facts
    fct = [atm.symbol for atm in prg.facts]
    fct.extend(prg.output_atoms[lit] for lit in interpretation if lit > 0 and lit in prg.output_atoms)


    # compute unknowns
    ukn = set()
    fls = set()
    for rule in prg.rules:
        atm, = rule.head
        # bd, = rule.body 
        
        falsess = any(lit not in interpretation for lit in rule.body)
        not_false = any(-lit in interpretation for lit in rule.body)

        
        # ORIGINAL
        if atm not in interpretation and not not_false and atm in prg.output_atoms:            
            ukn.add(prg.output_atoms[atm])
        

    return sorted(fct), sorted(ukn)


class LevelApp(Application):
    # def __init__(self):
        
        # self.program_name = "TEST"
        # self.version = "1.0"



    def main(self, ctl: Control, files):

        prg = Program()
        ctl.register_observer(ProgramObserver(prg))

        for f in files:
            ctl.load(f)
        if not files:
            ctl.load('-')

        ctl.ground([("base", [])])

        
        atoms = ctl.symbolic_atoms
        listc = ctl.symbolic_atoms.signatures
        full_atoms_list = [item[0] for item in listc]


        fct, ukn = well_founded(prg)

        facto_dirty = fct
        ukn_dirty = ukn
        fact_list = [item.name for item in facto_dirty]  # Access the 'name' attribute
        unk_list = [item.name for item in ukn_dirty]  # Access the 'name' attribute
        false_list = [item for item in full_atoms_list if item not in fact_list]
        false_list = [item for item in false_list if item not in unk_list]
        print('TRUE:',fact_list)
        print('UNKNOWN:',unk_list)
        print('FALSE:',false_list)

        # ctl.get_const

        # number_of_rules = 0
        # for rule in prg.rules:
        #     number_of_rules += 1

        # print(f"The list contains {number_of_rules} rules.")

        # happy = Function("happy")
        # rule = Rule(choice=False,head=happy, body=[]) 

        # testit= prg.rules
        # first_element = testit[0]

        # Print the first element
        # print('¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ first_element:',first_element)  # Output: apple
        

        # for rule in prg.rules:
        #         atm, = rule.head        
                # HACER UN LOOP COMPARANDO CADA REGLA RULE CON CADA ELEMENTO DE LA LISTA 
                # DE FACT UNK Y FALSE, SI SON IGUALES LOS ELEMENTOS, ENTONCES 
                # if check_literal(fact_list[0],rule):
                #     print('check_literal f',fact_list[0])
                # else:
                #     print('check_literal d',fact_list[0])

                # with ctl.backend() as backend:
                #     symbolic_backend = SymbolicBackend(backend)
                #     symbolic_backend.add_rule([a], [b], [c])
                #     atom_b = backend.add_atom(b)
                #     backend.add_rule([atom_b])



                # print(f"Rule: {format(rule[0])}")
                # head_symbols = [str(atom) for atom in rule.head]
                # body_symbols = [str(atom) for atom in rule.body]                
                # # head_symbols = [str(atom) for atom in rule.head.iter_terms()]
                # # body_symbols = [str(atom) for atom in rule.body.iter_terms()]
                # # print(f"Rule: {rule}")
                # print(f"  Head Symbols: {head_symbols}")
                # # print(f"  Body Symbols: {body_symbols}")
                # rul = Rule(choice=False,head=rule.head, body=rule.body)
                # print(rul.head)
                # print(f"Rule: {atm}")  # Output: happy <- 


                
                # print('<<<<<<<<<< atm_',atm)
                # # bd, = rule.body 
                
                
                # # ORIGINAL
                # if atm in prg.output_atoms:            
                #     print("if atm in prg.output_atoms:",atm)
        

            


sys.exit(clingo_main(LevelApp(), sys.argv[1:]))
