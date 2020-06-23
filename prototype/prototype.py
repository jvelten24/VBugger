import sys, inspect
import os
from optparse import OptionParser
import copy
import random

# genprog: Class Rep: you need to write your own class 
# the next line can be removed after installation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyverilog.vparser.parser import parse, NodeNumbering
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
import pyverilog.vparser.ast as vast

AST_CLASSES = []

for name, obj in inspect.getmembers(vast):
    if inspect.isclass(obj):
        AST_CLASSES.append(obj)

"""
Valid mutation operators supported by the algorithm.
"""
VALID_MUTATIONS = ["swap_plus_minus", "increment_identifier", "decrement_identifier", "increment_rhand_eq", "decrement_rhand_eq",
    "flip_if_cond", "flip_all_sens_edge", "flip_random_sens_edge", "increment_cond_vals", "decrement_cond_vals", "change_identifier_name"]

"""
Valid mutation operators supported by the algorithm.
"""
MUTATIONS_TARGETS = ["BlockingSubstitution", "NonblockingSubstitution", "IfStatement", "SensList", "Eq", "Cond", "Identifier"]

"""
Valid targets for the delete and insert operators.
"""
DELETE_TARGETS = ["IfStatement", "Block", "NonblockingSubstitution", "BlockingSubstitution", "ForStatement", "Always", "Decl", "Case", "CaseStatement", "DelayStatement", "Localparam", "Wire", "Assign"]
INSERT_TARGETS = ["IfStatement", "NonblockingSubstitution", "BlockingSubstitution", "ForStatement", "Always", "Case", "CaseStatement", "DelayStatement", "Localparam", "Assign"]

WRITE_TO_FILE = True

AST_BY_GEN = {}

"""
Returns a set of line numbers as potential targets for mutations.
"""
class CandidateCollector(ASTCodeGenerator):
    def __init__(self):
        self.my_candidates = set()
        self.my_identifiers = set()

    def visit(self, ast):
        if ast.__class__.__name__ in MUTATIONS_TARGETS:
            self.my_candidates.add(ast.lineno)
        if ast.__class__.__name__ in [ 'Port', 'Input', 'Wire' ]:
            self.my_identifiers.add(ast.name)

        for c in ast.children():
            self.visit(c)

class Mutate(ASTCodeGenerator):

    def __init__(self, identifiers):
        self.mutation = "null"
        self.mutateAt = -1
        self.identifiers = identifiers

    def set_mutation(self, mutation, lineno):
        self.mutation = mutation
        self.mutateAt = lineno
    
    def reset_mutation(self):
        self.mutation = "null"
        self.mutateAt = -1

    def visit(self, ast):

        if self.mutation == "swap_plus_minus":
            # TODO: change to include blocking substitution as well?
            if ast.__class__.__name__ == 'NonblockingSubstitution' and ast.right.var:
                if ast.right.var.__class__.__name__ == "Plus" and ast.right.var.lineno == self.mutateAt:
                    new_child = vast.Minus(ast.right.var.left, ast.right.var.right)
                    print("Changing %s on line %s to %s" % (ast.right.var, ast.right.var.lineno, new_child))
                    ast.right.var = new_child
                elif ast.right.var.__class__.__name__ == "Minus" and ast.right.var.lineno == self.mutateAt:
                    new_child = vast.Plus(ast.right.var.left, ast.right.var.right, ast.right.var.lineno)
                    print("Changing %s on line %s to %s" % (ast.right.var, ast.right.var.lineno, new_child))
                    ast.right.var = new_child

        elif self.mutation == "increment_identifier":
            if ast.__class__.__name__ == 'NonblockingSubstitution':
                my_lvalue = ast.left.var
                my_rvalue = ast.right.var
                if my_lvalue.__class__.__name__ == 'Identifier' and my_rvalue.__class__.__name__ == 'IntConst' and my_rvalue.lineno == self.mutateAt:
                    incrementedVal = my_rvalue.value + " + 1"
                    print("Updating %s on line %d from %s to %s" % (my_lvalue.name, my_rvalue.lineno, my_rvalue.value, incrementedVal))
                    my_rvalue.value = incrementedVal
                elif my_lvalue.__class__.__name__ == 'Identifier' and my_rvalue.__class__.__name__ in ['Plus', 'Minus', 'Times', 'Divide', 'Mod']  and my_rvalue.lineno == self.mutateAt:
                    new_child = vast.Plus(my_rvalue, vast.IntConst(1))
                    print("Changing %s on line %s to %s" % (my_rvalue, ast.right.var.lineno, new_child))
                    ast.right.var = new_child

        elif self.mutation == "decrement_identifier":
            if ast.__class__.__name__ == 'NonblockingSubstitution':
                my_lvalue = ast.left.var
                my_rvalue = ast.right.var
                if my_lvalue.__class__.__name__ == 'Identifier' and my_rvalue.__class__.__name__ == 'IntConst' and my_rvalue.lineno == self.mutateAt:
                    decrementedVal = my_rvalue.value + " - 1"
                    print("Updating %s on line %d from %s to %s" % (my_lvalue.name, my_rvalue.lineno, my_rvalue.value, decrementedVal))
                    my_rvalue.value = decrementedVal
                elif my_lvalue.__class__.__name__ == 'Identifier' and my_rvalue.__class__.__name__ in ['Plus', 'Minus', 'Times', 'Divide', 'Mod']  and my_rvalue.lineno == self.mutateAt:
                    new_child = vast.Minus(my_rvalue, vast.IntConst(1))
                    print("Changing %s on line %s to %s" % (my_rvalue, ast.right.var.lineno, new_child))
                    ast.right.var = new_child

        elif self.mutation == "increment_rhand_eq":
            if ast.__class__.__name__ == 'Eq':
                if ast.right.__class__.__name__ == 'IntConst' and ast.right.lineno == self.mutateAt:
                    incrementedVal = ast.right.value + " + 1"
                    print("Changing %s on line %s to %s" % (ast.right, ast.right.lineno, incrementedVal))
                    ast.right.value = incrementedVal

        elif self.mutation == "decrement_rhand_eq":
            if ast.__class__.__name__ == 'Eq':
                if ast.right.__class__.__name__ == 'IntConst' and ast.right.lineno == self.mutateAt:
                    decrementedVal = ast.right.value + " - 1"
                    print("Changing %s on line %s to %s" % (ast.right, ast.right.lineno, decrementedVal))
                    ast.right.value = decrementedVal

        elif self.mutation == "flip_if_cond":
            if ast.__class__.__name__ == 'IfStatement' and ast.lineno == self.mutateAt:
                if ast.cond.__class__.__name__ == "Eq":
                    new_cond = vast.NotEq(ast.cond.left, ast.cond.right, ast.lineno)
                    print("Changing %s on line %s to %s" % (ast.cond, ast.lineno, new_cond))
                    ast.cond = new_cond

        elif self.mutation == "flip_all_sens_edge":
            if ast.__class__.__name__ == 'SensList' and ast.lineno == self.mutateAt:
                for sens in ast.list:
                    newType = random.choice(("posedge", "negedge", "level", "all"))
                    print("Changing sens %s type on line %s from %s to %s" % (sens.sig, ast.lineno, sens.type, newType))
                    sens.type = newType

        elif self.mutation == "flip_random_sens_edge":
            if ast.__class__.__name__ == 'SensList' and ast.lineno == self.mutateAt:
                sens = random.choice(ast.list)
                newType = random.choice(("posedge", "negedge", "level", "all"))
                print("Changing sens %s type on line %s from %s to %s" % (sens.sig, ast.lineno, sens.type, newType))
                sens.type = newType

        elif self.mutation == "increment_cond_vals":
            if ast.__class__.__name__ == "Cond" and ast.lineno == self.mutateAt:
                p = random.random()
                if p > 0.5 and ast.true_value.__class__.__name__ == "IntConst":
                    incrementedVal = ast.true_value.value + " + 1"
                    print("Changing the true value %s on line %s to %s" % (ast.true_value, ast.true_value.lineno, incrementedVal))
                    ast.true_value.value = incrementedVal
                elif ast.false_value.__class__.__name__ == "IntConst":
                    incrementedVal = ast.false_value.value + " + 1"
                    print("Changing the false value %s on line %s to %s" % (ast.false_value, ast.false_value.lineno, incrementedVal))
                    ast.false_value.value = incrementedVal

        elif self.mutation == "decrement_cond_vals":
            if ast.__class__.__name__ == "Cond" and ast.lineno == self.mutateAt:
                p = random.random()
                if p > 0.5 and ast.true_value.__class__.__name__ == "IntConst":
                    decrementedVal = ast.true_value.value + " - 1"
                    print("Changing the true value %s on line %s to %s" % (ast.true_value, ast.true_value.lineno, decrementedVal))
                    ast.true_value.value = decrementedVal
                elif ast.false_value.__class__.__name__ == "IntConst":
                    decrementedVal = ast.false_value.value + " - 1"
                    print("Changing the false value %s on line %s to %s" % (ast.false_value, ast.false_value.lineno, decrementedVal))
                    ast.false_value.value = decrementedVal
        
        elif self.mutation == "change_identifier_name":
            if ast.__class__.__name__ == "Identifier" and ast.lineno == self.mutateAt:
                newName = random.choice(self.identifiers)
                print("Changing the identifier name at line %s from %s to %s" % (ast.lineno, ast.name, newName))
                ast.name = newName

        elif self.mutation not in VALID_MUTATIONS or self.mutateAt == -1:
            print("Not a valid mutation: %s at line %d" % (self.mutation, self.mutateAt))


        for c in ast.children():
            self.visit(c)

class MutationOp(ASTCodeGenerator):

    def __init__(self):
        self.ast_from_text = None
        self.node_for_insert = None
        self.node_from_ast = None
        self.deletable_nodes = []
        self.insertable_nodes = []
        self.stmt_nodes = []

    def make_ast_from_text(self, new_expression):
        tmp = open("tmp.txt", 'w+')
        tmp.write("module tmp ();\n")
        tmp.write("initial begin\n" + new_expression + "\nend\n")
        tmp.write("endmodule\n")
        tmp.close()
        new_ast = parse(["tmp.txt"])[0]
        os.remove("tmp.txt")

        def sub_visit(ast):
            if ast.__class__.__name__ == "Block":
                self.ast_from_text = ast.statements[0]
            
            for c in ast.children():
                sub_visit(c)

        sub_visit(new_ast)

    """ 
    Replace node_x with new_expresssion in the AST.
    """
    def replace_with_expression(self, ast, old_node_id, new_expression):
        attr = vars(ast)
        for key in attr: # loop through all attributes of this AST
            if attr[key].__class__ in AST_CLASSES: # for each attribute that is also an AST
                if attr[key].node_id == old_node_id:
                    self.get_ast_replacement(attr[key], new_expression)
                    attr[key] = self.ast_from_text
                    self.ast_from_text = None # reset self.ast_from_text for the next mutation
            elif attr[key].__class__ in [list, tuple]: # for attributes that are lists or tuples
                for i in range(len(attr[key])): # loop through each AST in that list or tuple
                    tmp = attr[key][i]
                    if tmp.__class__ in AST_CLASSES and tmp.node_id == old_node_id:
                        self.get_ast_replacement(tmp, new_expression)
                        attr[key][i] = self.ast_from_text
                        self.ast_from_text = None # reset self.ast_from_text for the next mutation

        for c in ast.children():
            if c: self.replace_with_expression(c, old_node_id, new_expression)
    
    def get_ast_replacement(self, old, expression):
        self.make_ast_from_text(expression)
        new_ast = self.ast_from_text

        def fix_lineno(a):
            a.lineno = old.lineno
            
            for c1 in a.children():
                if c1: fix_lineno(c1)

        fix_lineno(self.ast_from_text) # fix the line numbers to match the line being replaced

    """ 
    Replace node_x with node_y in the AST.
    """
    def replace_with_node(self, ast, old_node_id, new_node):
        attr = vars(ast)
        for key in attr: # loop through all attributes of this AST
            if attr[key].__class__ in AST_CLASSES: # for each attribute that is also an AST
                if attr[key].node_id == old_node_id:
                    attr[key] = new_node
            elif attr[key].__class__ in [list, tuple]: # for attributes that are lists or tuples
                for i in range(len(attr[key])): # loop through each AST in that list or tuple
                    tmp = attr[key][i]
                    if tmp.__class__ in AST_CLASSES and tmp.node_id == old_node_id:
                        attr[key][i] = new_node

        for c in ast.children():
            if c: self.replace_with_node(c, old_node_id, new_node)
        
    def get_node_from_ast(self, ast, node_id):
        if ast.node_id == node_id:
            self.node_from_ast = ast
        
        for c in ast.children():
            if c: self.get_node_from_ast(c, node_id)
    
    """
    Delete the node with the node_id provided, if such a node exists.
    """
    def delete_node(self, ast, node_id):
        attr = vars(ast)
        for key in attr: # loop through all attributes of this AST
            if attr[key].__class__ in AST_CLASSES: # for each attribute that is also an AST
                if attr[key].node_id == node_id:
                    attr[key] = None
            elif attr[key].__class__ in [list, tuple]: # for attributes that are lists or tuples
                for i in range(len(attr[key])): # loop through each AST in that list or tuple
                    tmp = attr[key][i]
                    if tmp.__class__ in AST_CLASSES and tmp.node_id == node_id:
                        attr[key][i] = None

        for c in ast.children():
            if c: self.delete_node(c, node_id)
    
    def get_deletable_nodes(self, ast):
        if ast.__class__.__name__ in DELETE_TARGETS:
            self.deletable_nodes.append(ast.node_id)

        for c in ast.children():
            if c: self.get_deletable_nodes(c) 

    def get_insertable_nodes(self, ast):
        if ast.__class__.__name__ in INSERT_TARGETS:
            self.insertable_nodes.append(ast.node_id)

        for c in ast.children():
            if c: self.get_insertable_nodes(c) 

    def get_nodes_in_block_stmt(self, ast):
        if ast.__class__.__name__ == "Block":
            for c in ast.statements:
                self.stmt_nodes.append(c.node_id)
        
        for c in ast.children():
            if c: self.get_nodes_in_block_stmt(c) 
    
    """
    Insert node with node_id after node with after_id.
    """
    # BUG: if node_id is a parent of after_id, we get infinite recursion. e.g. id 41 and 53 for first_counter_overflow.
    def insert_node(self, ast, node_id, after_id): # orig_ast keeps pointer to the root node to be used for get_node_for_insert
        if self.node_for_insert == None:
            self.get_node_for_insert(ast, node_id)

        if ast.__class__.__name__ == "Block":
            insert_point = -1
            for i in range(len(ast.statements)):
                stmt = ast.statements[i]
                if stmt.node_id == after_id:
                    insert_point = i + 1
                    break
            if insert_point != -1:
                print(ast.statements)
                ast.statements.insert(insert_point, copy.deepcopy(self.node_for_insert))
                self.node_for_insert = None # reset the node for insert for the next mutation operation
                print(ast.statements)

        for c in ast.children():
            if c: self.insert_node(c, node_id, after_id)
    
    def get_node_for_insert(self, ast, node_id):
        if ast.node_id == node_id:
            self.node_for_insert = ast

        for c in ast.children():
            if c: self.get_node_for_insert(c, node_id)

def main():
    INFO = "Verilog code parser"
    USAGE = "Usage: python example_parser.py file ..."

    def showVersion():
        print(INFO)
        print(USAGE)
        sys.exit()

    optparser = OptionParser()
    optparser.add_option("-v","--version",action="store_true",dest="showversion",
                         default=False,help="Show the version")
    optparser.add_option("-I","--include",dest="include",action="append",
                         default=[],help="Include path")
    optparser.add_option("-D",dest="define",action="append",
                         default=[],help="Macro Definition")
    (options, args) = optparser.parse_args()

    filelist = args
    if options.showversion:
        showVersion()

    for f in filelist:
        if not os.path.exists(f): raise IOError("file not found: " + f)

    if len(filelist) == 0:
        showVersion()

    codegen = ASTCodeGenerator()
    numbering = NodeNumbering()


    # parse the files (in filelist) to ASTs (PyVerilog ast)
    ast, directives = parse(filelist,
                            preprocess_include=options.include,
                            preprocess_define=options.define)

    ast.show()
    print(codegen.visit(ast))
    print("\n")

    AST_BY_GEN[0] = copy.deepcopy(ast)

    mutation_op = MutationOp()

    # replace node_x in current generation by node_y from the previous generation
    # mutation_op.get_node_from_ast(AST_BY_GEN[0], 41)
    # mutation_op.replace_with_node(ast, 74, mutation_op.node_from_ast)
    # mutation_op.node_from_ast = None
    # numbering.visit(ast)
    # ast.show()
    # print(codegen.visit(ast))

    # mutation_op.replace_with_expression(ast, 41, "1'b0;")
    # numbering.visit(ast)
    # ast.show()
    # print(codegen.visit(ast))

    # mutation_op.get_deletable_nodes(ast)
    # nodeid = random.choice(mutation_op.deletable_nodes)
    # print("Deleting node with id %s\n" % nodeid)
    # mutation_op.delete_node(ast, nodeid)
    # numbering.visit(ast)
    # mutation_op.deletable_nodes = []
    # ast.show()
    # print(codegen.visit(ast))

    mutation_op.get_insertable_nodes(ast)
    mutation_op.get_nodes_in_block_stmt(ast)
    after_id = random.choice(mutation_op.stmt_nodes) 
    node_id = random.choice(mutation_op.insertable_nodes)
    print("Inserting node with id %s after node with id %s\n" % (node_id, after_id))
    mutation_op.insert_node(ast, node_id, after_id)
    numbering.visit(ast)
    mutation_op.insertable_nodes = []
    ast.show()
    print(codegen.visit(ast))

    # candidatecollector = CandidateCollector()
    # candidatecollector.visit(ast)

    # mutation_op = Mutate(list(candidatecollector.my_identifiers))

    # try:
    #     dirName = os.getcwd()+"/repair_candidates"
    #     os.mkdir(dirName)
    #     print("Directory " , dirName ,  " created ") 
    # except:
    #     print("Directory " , dirName ,  " already exists")

    # depth_edits = 1
    # try_all_mutations(mutation_op, list(candidatecollector.my_candidates), codegen, ast, depth_edits)

    # try_random_mutations(mutation_op, list(candidatecollector.my_candidates), codegen, ast, 1000)

def try_all_mutations(mutation_op, candidates, codegen, ast, depth, uniq=set()):
    for choice in VALID_MUTATIONS:
        for line in candidates:
            mutation_op.set_mutation(choice, line)
            tmp = copy.deepcopy(ast)
            mutation_op.visit(tmp)
            mutation_op.reset_mutation()
            if tmp != ast: # if the mutation was successful
                uniq.add(tmp)
                if depth > 1:
                    try_all_mutations(mutation_op, candidates, codegen, tmp, depth - 1)

    if depth == 1:
        for tmp in uniq:
            print(codegen.visit(tmp))
            print("#################\n")
        print("A total of %d mutations were performed." % (len(uniq)))


def try_random_mutations(mutation_op, candidates, codegen, ast, maxIters):
    uniq = set()
    for i in range(maxIters):
        # choose a random mutation and line; might not be a valid mutation
        choice = random.choice(VALID_MUTATIONS)
        line = random.choice(candidates)
        mutation_op.set_mutation(choice, line)
        tmp = copy.deepcopy(ast)
        mutation_op.visit(tmp)
        mutation_op.reset_mutation()
        if tmp != ast: # if the mutation was successful and/or resulted in a different ast
            uniq.add(tmp)
    
    # cand_num = 0
    # for tmp in uniq:
    #     rslt = codegen.visit(tmp)
    #     print(rslt)
    #     print("#################\n")
    #     if WRITE_TO_FILE:
    #         outf = open("./repair_candidates/candidate_"+str(cand_num)+".v","w+")
    #         outf.write(str(rslt))
    #         outf.close()
    #     cand_num += 1

    print("A total of %d mutations were successful out of %d attempted mutations." % (len(uniq), maxIters))

if __name__ == '__main__':
    main()
