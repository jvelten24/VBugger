import sys, inspect, subprocess
from optparse import OptionParser
import os
import copy
import random
import time 
from datetime import datetime
import math
from collections import deque
from pyverilog.vparser.parser import parse, NodeNumbering
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
from pyverilog.vparser.plyparser import ParseError
import pyverilog.vparser.ast as vast
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fitness
import contextlib

AST_CLASSES = []

GENOME_FITNESS_CACHE = {}


"""
So the goal with this script is to take the verilog source file and return a fitness score as well as 
the implicated lines. Basically take CirFix and only keep the essential fitness and fault localization
components. 
"""

SRC_FILE = TEST_BENCH = PROJ_DIR = EVAL_SCRIPT = ORACLE = None
ORIG_FILE = ""
FITNESS_MODE = "outputwires"
FAULT_LOC = True
CONTROL_FLOW = True
LIMIT_TRANSITIVE_DEPENDENCY_SET = False
POPSIZE = 200
FITNESS_EVAL_TIMES = []
TB_ID = None
TIME_NOW = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
IMPLICATED_LINES_DICT = dict()

#dictionary for the various files
#used as replacement for repair.conf

FIRST_COUNTER_OVERFLOW_WADDEN_BUGGY1 = {
    'src_file': "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/first_counter_overflow_wadden_buggy1.v",
    'test_bench': "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/first_counter_tb_t3.v",
    'eval_script': "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/run.sh",
    'orig_file': "first_counter_overflow.v",
    'proj_dir': "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/",
    'oracle': "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/oracle.txt"
}

FIRST_COUNTER_OVERFLOW_KGOLIYA_BUGGY1 = {
    'src_file': "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/first_counter_overflow_kgoliya_buggy1.v",
    'test_bench': "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/first_counter_tb_t3.v",
    'eval_script': "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/run.sh",
    'orig_file': "first_counter_overflow.v",
    'proj_dir': "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/",
    'oracle': "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/oracle.txt"
}

FSM_FULL_WADDEN_BUGGY1 = {
    'src_file': "/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/fsm_full_wadden_buggy1.v",
    'test_bench': "/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/fsm_full_tb_t1.v",
    'eval_script': "/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/run.sh",
    'orig_file': "fsm_full.v",
    'proj_dir': "/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/",
    'oracle': "/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/oracle.txt"
}

FIRST_COUNTER_OVERFLOW_WADDEN_BUGGY2 = {
    'src_file': "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/first_counter_overflow_wadden_buggy2.v",
    'test_bench': "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/first_counter_tb_t3.v",
    'eval_script': "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/run.sh",
    'orig_file': "first_counter_overflow.v",
    "proj_dir": "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/",
    "oracle": "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/oracle.txt"
}

LSHIFT_REG_WADDEN_BUGGY1 = {
    'src_file': "/home/jvelten/projects/verilog_repair/benchmarks/lshift_reg/lshift_reg_wadden_buggy1.v",
    'test_bench': "/home/jvelten/projects/verilog_repair/benchmarks/lshift_reg/lshift_reg_tb_t1.v",
    'eval_script': "/home/jvelten/projects/verilog_repair/benchmarks/lshift_reg/run.sh",
    'orig_file': "lshift_reg.v",
    'proj_dir': "/home/jvelten/projects/verilog_repair/benchmarks/lshift_reg/",
    'oracle': "/home/jvelten/projects/verilog_repair/benchmarks/lshift_reg/oracle.txt"
}


DECODER_WADDEN_BUGGY1 = {
    'src_file': "/home/jvelten/projects/verilog_repair/benchmarks/decoder_3_to_8/decoder_3_to_8_wadden_buggy1.v",
    'test_bench': "/home/jvelten/projects/verilog_repair/benchmarks/decoder_3_to_8/decoder_3_to_8_tb_t1.v",
    'eval_script': "/home/jvelten/projects/verilog_repair/benchmarks/decoder_3_to_8/run.sh",
    'orig_file': "decoder_3_to_8.v",
    'proj_dir': "/home/jvelten/projects/verilog_repair/benchmarks/decoder_3_to_8/",
    'oracle': "/home/jvelten/projects/verilog_repair/benchmarks/decoder_3_to_8/oracle.txt"
}

DECODER_WADDEN_BUGGY2 = {
    'src_file': "/home/jvelten/projects/verilog_repair/benchmarks/decoder_3_to_8/decoder_3_to_8_wadden_buggy2.v",
    'test_bench': "/home/jvelten/projects/verilog_repair/benchmarks/decoder_3_to_8/decoder_3_to_8_tb_t1.v",
    'eval_script': "/home/jvelten/projects/verilog_repair/benchmarks/decoder_3_to_8/run.sh",
    'orig_file': "decoder_3_to_8.v",
    'proj_dir': "/home/jvelten/projects/verilog_repair/benchmarks/decoder_3_to_8/",
    'oracle': "/home/jvelten/projects/verilog_repair/benchmarks/decoder_3_to_8/oracle.txt"
}

FLIP_FLOP_WADDEN_BUGGY1 = {
    'src_file': "/home/jvelten/projects/verilog_repair/benchmarks/flip_flop/tff_wadden_buggy1.v",
    'test_bench': "/home/jvelten/projects/verilog_repair/benchmarks/flip_flop/tff_tb.v",
    'eval_script': "/home/jvelten/projects/verilog_repair/benchmarks/flip_flop/run.sh",
    'orig_file': "tff.v",
    'proj_dir': "/home/jvelten/projects/verilog_repair/benchmarks/flip_flop",
    'oracle': '/home/jvelten/projects/verilog_repair/benchmarks/flip_flop/oracle.txt'
}

FLIP_FLOP_WADDEN_BUGGY2 = {
    'src_file': "/home/jvelten/projects/verilog_repair/benchmarks/flip_flop/tff_wadden_buggy2.v",
    'test_bench': "/home/jvelten/projects/verilog_repair/benchmarks/flip_flop/tff_tb.v",
    'eval_script': "/home/jvelten/projects/verilog_repair/benchmarks/flip_flop/run.sh",
    'orig_file': "tff.v",
    'proj_dir': "/home/jvelten/projects/verilog_repair/benchmarks/flip_flop",
    'oracle': '/home/jvelten/projects/verilog_repair/benchmarks/flip_flop/oracle.txt'
}

FSM_FULL_WADDEN_BUGGY2 = {
    'src_file': '/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/fsm_full_wadden_buggy2.v',
    'test_bench': '/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/fsm_full_tb_t1.v',
    'eval_script': '/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/run.sh',
    'orig_file': 'fsm_full.v',
    'proj_dir': '/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/',
    'oracle': '/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/oracle.txt'
}

FSM_FULL_SSSCRAZY_BUGGY1 = {
    'src_file': '/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/fsm_full_ssscrazy_buggy1.v',
    'test_bench': '/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/fsm_full_tb_t1.v',
    'eval_script': '/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/run.sh',
    'orig_file': 'fsm_full.v',
    'proj_dir': '/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/',
    'oracle': '/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/oracle.txt'
}

FSM_FULL_SSSCRAZY_BUGGY2 = {
    'src_file': '/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/fsm_full_ssscrazy_buggy2.v',
    'test_bench': '/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/fsm_full_tb_t1.v',
    'eval_script': '/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/run.sh',
    'orig_file': 'fsm_full.v',
    'proj_dir': '/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/',
    'oracle': '/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/oracle.txt'
}

MUX_WADDEN_BUGGY1 = {
    'src_file': '/home/jvelten/projects/verilog_repair/benchmarks/mux_4_1/mux_4_1_wadden_buggy1.v',
    'test_bench': '/home/jvelten/projects/verilog_repair/benchmarks/mux_4_1/mux_4_1_tb.v',
    'eval_script': '/home/jvelten/projects/verilog_repair/benchmarks/mux_4_1/run.sh',
    'orig_file': 'mux_4_1.v',
    'proj_dir': '/home/jvelten/projects/verilog_repair/benchmarks/mux_4_1/',
    'oracle': '/home/jvelten/projects/verilog_repair/benchmarks/mux_4_1/oracle_new.txt'
}


MUX_WADDEN_BUGGY2 = {
    'src_file': '/home/jvelten/projects/verilog_repair/benchmarks/mux_4_1/mux_4_1_wadden_buggy2.v',
    'test_bench': '/home/jvelten/projects/verilog_repair/benchmarks/mux_4_1/mux_4_1_tb.v',
    'eval_script': '/home/jvelten/projects/verilog_repair/benchmarks/mux_4_1/run.sh',
    'orig_file': 'mux_4_1.v',
    'proj_dir': '/home/jvelten/projects/verilog_repair/benchmarks/mux_4_1/',
    'oracle': '/home/jvelten/projects/verilog_repair/benchmarks/mux_4_1/oracle_new.txt'
}



#we will be using this inside of main to get access to all the absolute paths
#to the files we need
conf = {
    "FIRST_COUNTER_OVERFLOW_WADDEN_BUGGY1": FIRST_COUNTER_OVERFLOW_WADDEN_BUGGY1,
    "FIRST_COUNTER_OVERFLOW_KGOLIYA_BUGGY1": FIRST_COUNTER_OVERFLOW_KGOLIYA_BUGGY1,
    "FSM_FULL_WADDEN_BUGGY1": FSM_FULL_WADDEN_BUGGY1,
    "FIRST_COUNTER_OVERFLOW_WADDEN_BUGGY2": FIRST_COUNTER_OVERFLOW_WADDEN_BUGGY2,
    "LSHIFT_REG_WADDEN_BUGGY1": LSHIFT_REG_WADDEN_BUGGY1 ,
    "DECODER_WADDEN_BUGGY1": DECODER_WADDEN_BUGGY1,
    "DECODER_WADDEN_BUGGY2": DECODER_WADDEN_BUGGY2,
    "FLIP_FLOP_WADDEN_BUGGY1": FLIP_FLOP_WADDEN_BUGGY1,
    "FLIP_FLOP_WADDEN_BUGGY2": FLIP_FLOP_WADDEN_BUGGY2,
    "FSM_FULL_WADDEN_BUGGY2": FSM_FULL_WADDEN_BUGGY2,
    "FSM_FULL_SSSCRAZY_BUGGY1": FSM_FULL_SSSCRAZY_BUGGY1,
    "FSM_FULL_SSSCRAZY_BUGGY2": FSM_FULL_SSSCRAZY_BUGGY2,
    "MUX_WADDEN_BUGGY1": MUX_WADDEN_BUGGY1,
    "MUX_WADDEN_BUGGY2": MUX_WADDEN_BUGGY2
}




POPSIZE = 5000
RESTARTS = 1
REPLACEMENT_RATE = 0.4
INSERTION_RATE = 0.3
DELETION_RATE = 0.3
CROSSOVER_RATE = 0.3
MUTATION_RATE = 0.7
FITNESS_MODE = "outputwires"
GENS = 8


filelist = [SRC_FILE, TEST_BENCH]


class MutationOp(ASTCodeGenerator):

    def __init__(self, popsize, fault_loc, control_flow):
        self.numbering = NodeNumbering()
        self.popsize = popsize
        self.fault_loc = fault_loc
        self.control_flow = control_flow
        # temporary variables used for storing data for the mutation operators
        self.fault_loc_set = set()
        self.new_vars_in_fault_loc = dict()
        self.wires_brought_in = dict()
        self.implicated_lines = set() # contains the line number implicated by FL
        # self.stoplist = set()
        self.tmp_node = None 
        self.deletable_nodes = []
        self.insertable_nodes = []
        self.replaceable_nodes = []
        self.node_class_to_replace = None
        self.nodes_by_class = []
        self.stmt_nodes = []
        self.max_node_id = -1

    """ 
    Replaces the node corresponding to old_node_id with new_node.
    """
    def replace_with_node(self, ast, old_node_id, new_node):
        attr = vars(ast)
        for key in attr: # loop through all attributes of this AST
            if attr[key].__class__ in AST_CLASSES: # for each attribute that is also an AST
                if attr[key].node_id == old_node_id:
                    attr[key] = copy.deepcopy(new_node)
                    return
            elif attr[key].__class__ in [list, tuple]: # for attributes that are lists or tuples
                for i in range(len(attr[key])): # loop through each AST in that list or tuple
                    tmp = attr[key][i]
                    if tmp.__class__ in AST_CLASSES and tmp.node_id == old_node_id:
                        attr[key][i] = copy.deepcopy(new_node)
                        return

        for c in ast.children():
            if c: self.replace_with_node(c, old_node_id, new_node)
    
    """
    Deletes the node with the node_id provided, if such a node exists.
    """
    def delete_node(self, ast, node_id):
        attr = vars(ast)
        for key in attr: # loop through all attributes of this AST
            if attr[key].__class__ in AST_CLASSES: # for each attribute that is also an AST
                if attr[key].node_id == node_id and attr[key].__class__.__name__ in DELETE_TARGETS:
                    attr[key] = None
            elif attr[key].__class__ in [list, tuple]: # for attributes that are lists or tuples
                for i in range(len(attr[key])): # loop through each AST in that list or tuple
                    tmp = attr[key][i]
                    if tmp.__class__ in AST_CLASSES and tmp.node_id == node_id and tmp.__class__.__name__ in DELETE_TARGETS:
                        attr[key][i] = None

        for c in ast.children():
            if c: self.delete_node(c, node_id)
    
    """
    Inserts node with node_id after node with after_id.
    """
    def insert_stmt_node(self, ast, node, after_id): 
        if ast.__class__.__name__ == "Block":
            if after_id == ast.node_id:
                # node.show()
                # input("...")
                ast.statements.insert(0, copy.deepcopy(node))
                return
            else:
                insert_point = -1
                for i in range(len(ast.statements)):
                    stmt = ast.statements[i]
                    if stmt and stmt.node_id == after_id:
                        insert_point = i + 1
                        break
                if insert_point != -1:
                    # print(ast.statements)
                    ast.statements.insert(insert_point, copy.deepcopy(node))
                    # print(ast.statements)
                    return

        for c in ast.children():
            if c: self.insert_stmt_node(c, node, after_id)
    
    """
    Gets the node matching the node_id provided, if one exists, by storing it in the temporary node variable.
    Used by the insert and replace operators.
    """    
    def get_node_from_ast(self, ast, node_id):
        if ast.node_id == node_id:
            self.tmp_node = ast
        
        for c in ast.children():
            if c: self.get_node_from_ast(c, node_id)

    """ 
    Gets all the line numbers for the code implicated by the FL.
    """    
    def collect_lines_for_fl(self, ast):
        if ast.node_id in self.fault_loc_set:
            self.implicated_lines.add(ast.lineno)
        
        for c in ast.children():
            if c: self.collect_lines_for_fl(c)



    #this gets implicated lines as per the source code's file
    #in the repository, not as per the src_code object
    # def get_implicated_lines(self, ast):
    #     lines = []
    #     q = deque()
    #     q.append(ast)
    #     while q:
    #         node = q.popleft()
    #         if node.node_id in self.fault_loc_set:
    #             lines.append(node.lineno)
    #         else:
    #             for c in node.children():
    #                 q.append(c)
    #     return lines


    def get_implicated_lines(self, ast):
        #if a node is in the fault loc set add its line to the 
        #list of implicated lines
        if ast.node_id in self.fault_loc_set:
            self.implicated_lines.add(ast.lineno)
            for c in ast.children():
                self.implicated_lines.add(c.lineno)
        #also if any of its children are in the
        #fault loc set add it to implicated lines
        for c in ast.children():
            if c and c.node_id in self.fault_loc_set:
                self.implicated_lines.add(ast.lineno)
            if c:
                #then recursively call this function on all children
                self.get_implicated_lines(c)




    #this is working now
    def print_implicated_lines(self, lines, source_code):
        with open(SRC_FILE) as f:
            src_code_text = f.readlines()
            for lineNum in lines:
                #src_code_text is zero indexed, lineNum isn't
                print(src_code_text[lineNum - 1])

    def implicated_lines_string(self, lines, source_code):
        implicated_string = ""
        with open(SRC_FILE) as f:
            src_code_text = f.readlines()
            for lineNum in lines:
                #src_code_text is zero indexed, lineNum isn't
                implicated_string += f"\n{src_code_text[lineNum - 1]}"
        return implicated_string
                
    
    """
    Gets a list of all nodes that can be deleted.
    """
    def get_deletable_nodes(self, ast):
        # with fault localization, make sure that any node being deleted is also in DELETE_TARGETS 
        if self.fault_loc and len(self.fault_loc_set) > 0:
            if ast.node_id in self.fault_loc_set and ast.__class__.__name__ in DELETE_TARGETS:
                self.deletable_nodes.append(ast.node_id)
        else:
            if ast.__class__.__name__ in DELETE_TARGETS:
                self.deletable_nodes.append(ast.node_id)

        for c in ast.children():
            if c: self.get_deletable_nodes(c) 

    """
    Gets a list of all nodes that can be inserted into to a begin ... end block.
    """
    def get_insertable_nodes(self, ast):
        # with fault localization, make sure that any node being used is also in INSERT_TARGETS (to avoid inserting, e.g., overflow+1 into a block statement)
        if self.fault_loc and len(self.fault_loc_set) > 0: 
            if ast.node_id in self.fault_loc_set and ast.__class__.__name__ in INSERT_TARGETS:
                self.insertable_nodes.append(ast.node_id)
        else:        
            if ast.__class__.__name__ in INSERT_TARGETS:
                self.insertable_nodes.append(ast.node_id)

        for c in ast.children():
            if c: self.get_insertable_nodes(c) 
    
    """
    Gets the class of the node being replaced in a replace operation. 
    This class is used to find potential sources for the replacement.
    """
    def get_node_to_replace_class(self, ast, node_id):
        if ast.node_id == node_id:
            self.node_class_to_replace = ast.__class__

        for c in ast.children():
            if c: self.get_node_to_replace_class(c, node_id)
    
    """
    Gets all nodes that compatible to be replaced with a node of the given class type. 
    These nodes are potential sources for replace operations.
    """
    def get_replaceable_nodes_by_class(self, ast, node_type):
        if ast.__class__ in REPLACE_TARGETS[node_type]:
            self.replaceable_nodes.append(ast.node_id)

        for c in ast.children():
            if c: self.get_replaceable_nodes_by_class(c, node_type)
    
    """
    Gets all nodes that are of the given class type. 
    These nodes are used for applying mutation templates.
    """
    # TODO: do this only for fault loc set?
    def get_nodes_by_class(self, ast, node_type):
        if ast.__class__.__name__ == node_type:
            self.nodes_by_class.append(ast.node_id)

        for c in ast.children():
            if c: self.get_nodes_by_class(c, node_type)

    """
    Gets all nodes that are found within a begin ... end block. 
    These nodes are potential destinations for insert operations.
    """
    def get_nodes_in_block_stmt(self, ast):
        if ast.__class__.__name__ == "Block":
            if len(ast.statements) == 0: # if empty block, return the node id for the block (so that a node can be inserted into the empty block)
                self.stmt_nodes.append(ast.node_id)
            else:
                for c in ast.statements:
                    if c: self.stmt_nodes.append(c.node_id)
        
        for c in ast.children():
            if c: self.get_nodes_in_block_stmt(c)

    """
    Control dependency analysis of the given program branch.
    """
    def analyze_program_branch(self, ast, cond_list, mismatch_set, uniq_headers):
        if ast:
            if ast.__class__.__name__ == "Identifier" and (ast.name in mismatch_set or ast.name in tuple(self.new_vars_in_fault_loc.values())):
                for cond in cond_list:
                    if cond: self.add_node_and_children_to_fault_loc(cond, mismatch_set, uniq_headers, ast)

            for c in ast.children():
                self.analyze_program_branch(c, cond_list, mismatch_set, uniq_headers)

    """
    Add node and its immediate children to the fault loc set.    
    """
    def add_node_and_children_to_fault_loc(self, ast, mismatch_set, uniq_headers, parent=None):
        # if ast.__class__.__name__ == "Identifier" and ast.name in self.stoplist: return
        self.fault_loc_set.add(ast.node_id)
        if parent and parent.__class__.__name__ == "Identifier" and parent.name not in self.wires_brought_in: self.wires_brought_in[parent.name] = set()
        if ast.__class__.__name__ == "Identifier" and ast.name not in mismatch_set and ast.name not in uniq_headers: # and ast.name not in self.stoplist: 
            if not LIMIT_TRANSITIVE_DEPENDENCY_SET or len(self.wires_brought_in[parent.name]) < DEPENDENCY_SET_MAX:
                self.wires_brought_in[parent.name].add(ast.name)
                self.new_vars_in_fault_loc[ast.node_id] = ast.name
            # else:
            #     self.stoplist.add(ast.name)
        for c in ast.children():
            if c:
                self.fault_loc_set.add(c.node_id) 
                # add all children identifiers to depedency set
                if c.__class__.__name__ == "Identifier" and c.name not in mismatch_set and c.name not in uniq_headers: # and c.name not in self.stoplist: 
                    if not LIMIT_TRANSITIVE_DEPENDENCY_SET or len(self.wires_brought_in[parent.name]) < DEPENDENCY_SET_MAX: 
                        self.wires_brought_in[parent.name].add(c.name)
                        self.new_vars_in_fault_loc[c.node_id] = c.name
                    # else:
                    #     self.stoplist.add(c.name)

    """
    Given a set of output wires that mismatch with the oracle, get a list of node IDs that are potential fault localization targets.
    """
    # TODO: add decl to fault loc targets?
    def get_fault_loc_targets(self, ast, mismatch_set, uniq_headers, parent=None, include_all_subnodes=False):
        # data dependency analysis
        # if ast.__class__.__name__ == "Identifier" and ast.name in self.stoplist: return
        if ast.__class__.__name__ in ["BlockingSubstitution", "NonblockingSubstitution", "Assign"]: # for assignment statements =, <=
            if ast.left and ast.left.__class__.__name__ == "Lvalue" and ast.left.var:
                if ast.left.var.__class__.__name__ == "Identifier" and ast.left.var.name in mismatch_set: # single assignment
                    include_all_subnodes = True
                    parent = ast.left.var
                    if parent and not parent.name in self.wires_brought_in: self.wires_brought_in[parent.name] = set()
                    self.add_node_and_children_to_fault_loc(ast, mismatch_set, uniq_headers, parent)
                elif ast.left.var.__class__.__name__ == "LConcat": # l-concat / multiple assignments
                    for v in ast.left.var.list: 
                        if v.__class__.__name__ == "Identifier" and v.name in mismatch_set:
                            if not v.name in self.wires_brought_in: self.wires_brought_in[v.name] = set()
                            include_all_subnodes = True
                            parent = v
                            self.add_node_and_children_to_fault_loc(ast, mismatch_set, uniq_headers, parent)
        
        # control dependency analysis        
        elif self.control_flow and ast.__class__.__name__ == "IfStatement":
            self.analyze_program_branch(ast.true_statement, [ast.cond], mismatch_set, uniq_headers)
            self.analyze_program_branch(ast.false_statement, [ast.cond], mismatch_set, uniq_headers)
        elif self.control_flow and ast.__class__.__name__ == "CaseStatement":
            for c in ast.caselist: 
                if c: 
                    cond_list = [ast.comp]
                    if c.cond: 
                        for tmp_var in c.cond: cond_list.append(tmp_var)
                    self.analyze_program_branch(c.statement, cond_list, mismatch_set, uniq_headers)
        elif self.control_flow and ast.__class__.__name__ == "ForStatement":
            cond_list = []
            if ast.pre: cond_list.append(ast.pre)
            if ast.cond: cond_list.append(ast.cond)
            if ast.post: cond_list.append(ast.post)
            self.analyze_program_branch(ast.statement, cond_list, mismatch_set, uniq_headers)


        if include_all_subnodes: # recurisvely ensure all children of a fault loc target are also included in the fault loc set
            self.fault_loc_set.add(ast.node_id)
            if ast.__class__.__name__ == "Identifier" and ast.name not in mismatch_set and ast.name not in uniq_headers: # and ast.name not in self.stoplist:
                if parent and parent.__class__.__name__ == "Identifier":
                    if not LIMIT_TRANSITIVE_DEPENDENCY_SET or len(self.wires_brought_in[parent.name]) < DEPENDENCY_SET_MAX: 
                        self.wires_brought_in[parent.name].add(ast.name)
                        self.new_vars_in_fault_loc[ast.node_id] = ast.name
                    # else:
                    #     self.stoplist.add(ast.name)

        for c in ast.children():
            if c: self.get_fault_loc_targets(c, mismatch_set, uniq_headers, parent, include_all_subnodes)

        # TODO: for sdram_controller, control_flow + limit gives smaller fl set than no control_flow + limit. why? is this a bug?
    

def calc_candidate_fitness(fileName):
    if os.path.exists("output_%s.txt" % TB_ID): os.remove("output_%s.txt" % TB_ID)

    #print("Running VCS simulation")
    #os.system("cat %s" % fileName)

    t_start = time.time()

    if "/" in fileName: fileName = fileName.split("/")[-1] # get the filename only if full path specified

    # TODO: The test bench is currently hard coded in eval_script. Do we want to change that?
    os.system("bash %s %s %s %s" % (EVAL_SCRIPT, ORIG_FILE, fileName, PROJ_DIR))
    


    f = open(ORACLE, "r")
    oracle_lines = f.readlines()
    f.close()

    f = open("output_%s.txt" % TB_ID, "r")
    sim_lines = f.readlines()
    f.close()

    # weighting = "static"
    # f = open("weights.txt", "r")
    # weights = f.readlines()
    # f.close()

    #ff, total_possible = fitness.calculate_fitness(oracle_lines, sim_lines, weights, weighting)
    if FITNESS_MODE == "outputwires":
        ff, total_possible = fitness.calculate_fitness(oracle_lines, sim_lines, None, "")
        
        normalized_ff = ff/total_possible
        if normalized_ff < 0: normalized_ff = 0
        print("FITNESS = %f" % normalized_ff)
        # if os.path.exists("output_%s.txt" % TB_ID): os.remove("output_%s.txt" % TB_ID) # Do we need to do this here? Does it make a difference?
        t_finish = time.time()

        return normalized_ff, t_finish - t_start

def strip_bits(bits):
    for i in range(len(bits)):
        bits[i] = bits[i].strip()
    return bits

def get_output_mismatch():
    f = open(ORACLE, "r")
    oracle = f.readlines()
    f.close()

    f = open("output_%s.txt" % TB_ID, "r")
    sim = f.readlines()
    f.close()

    diff_bits = []

    headers = strip_bits(oracle[0].split(","))

    if len(oracle) != len(sim): # if the output and oracle are not the same length, all output wires are defined to be mismatched
        diff_bits = headers[1:] # don't include time...
    else:
        for i in range(1, len(oracle)):
            clk = oracle[i].split(",")[0]
            tmp_oracle = strip_bits(oracle[i].split(",")[1:])
            tmp_sim = strip_bits(sim[i].split(",")[1:])
            
            for b in range(len(tmp_oracle)):
                if tmp_oracle[b] != tmp_sim[b]:
                    diff_bits.append(headers[b+1]) # offset by 1 since clk is also a header and is not an actual output
   
    res = set()

    for i in range(len(diff_bits)):
        tmp = diff_bits[i]
        if "[" in tmp:      
            res.add(tmp.split("[")[0])
        else:
            res.add(tmp)

    uniq_headers = set()
    for i in range(len(headers)):
        tmp = headers[i]
        if "[" in tmp:      
            uniq_headers.add(tmp.split("[")[0])
        else:
            uniq_headers.add(tmp)
        
    return res, uniq_headers


def main():
    start_time = time.time()
    optparser = OptionParser()
    optparser.add_option("-v","--version",action="store_true",dest="showversion",
                         default=False,help="Show the version")
    optparser.add_option("-I","--include",dest="include",action="append",
                         default=[],help="Include path")
    optparser.add_option("-D",dest="define",action="append",
                         default=[],help="Macro Definition")
    (options, args) = optparser.parse_args()
    #sys.argv[1] should be the name of the verilog file
    #for example, FIRST_COUNTER_OVERFLOW_WADDEN_BUGGY1
    #we are updating the global variables here
    global SRC_FILE
    SRC_FILE = conf[sys.argv[1]]['src_file']
    global TEST_BENCH
    TEST_BENCH = conf[sys.argv[1]]['test_bench']
    global EVAL_SCRIPT
    EVAL_SCRIPT = conf[sys.argv[1]]['eval_script']
    global ORIG_FILE
    ORIG_FILE = conf[sys.argv[1]]['orig_file']
    global PROJ_DIR
    PROJ_DIR = conf[sys.argv[1]]['proj_dir']
    global ORACLE
    ORACLE = conf[sys.argv[1]]['oracle']


    filelist = [SRC_FILE, TEST_BENCH]
    for f in filelist:
        if not os.path.exists(f): raise IOError("file not found: " + f)
    global TB_ID
    TB_ID = TEST_BENCH.split("/")[-1].replace(".v","")
    
    codegen = ASTCodeGenerator()
    ast, directives = parse([SRC_FILE],
                            preprocess_include=PROJ_DIR.split(","),
                            preprocess_define=options.define)

    LOG = False
    CODE_FROM_PATCHLIST = False
    MINIMIZE_ONLY = False

    src_code = codegen.visit(ast)
    #so keys will be strings of lines from the file
    #values will be string of implicated lines
    #so when we have a string of lines, we check if its in dictionary
    #if it is, we return the value
    #if not, then we add it to dictionary, run cirfix, then add implicated lines
    #as the value
    
    

    mutation_op = MutationOp(POPSIZE, FAULT_LOC, CONTROL_FLOW)

    with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
        orig_fitness, sim_time = calc_candidate_fitness(SRC_FILE)
    global FITNESS_EVAL_TIMES
    FITNESS_EVAL_TIMES.append(sim_time)

    GENOME_FITNESS_CACHE[str([])] = orig_fitness
    print("Original program fitness = %f" % orig_fitness)
    print("FINAL STATEMENTS:")
    print("Fitness = %f" % orig_fitness)
    print("IMPLICATED LINES:")
    mismatch_set, uniq_headers = get_output_mismatch()
    mutation_op.get_fault_loc_targets(ast, mismatch_set, uniq_headers)
    mutation_op.collect_lines_for_fl(ast)
    mutation_op.get_implicated_lines(ast)
    mutation_op.print_implicated_lines(mutation_op.implicated_lines, src_code)




    

#run fault localization and fitness function

if __name__ == '__main__':
    main()
