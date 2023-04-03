from flask import Flask, render_template, send_file, request, redirect, url_for, g
import os, subprocess
import ast
import json
app = Flask(__name__)
#app.config["TEMPLATES_AUTO_RELOAD"] = True
import sqlite3 as sql
from datetime import datetime

#TO DELETE CONTENTS OF CONSENT FORM
# conn = sql.connect("memoization.db")
# cursor = conn.cursor()
# cursor.execute("DELETE FROM consent_form")
# conn.commit()
# conn.close()



#home page
@app.route("/")
def home():
    return render_template('home2.html')

@app.post("/consent")
def consent():
    name = request.form['name']
    date = request.form['date']
    timestamp = datetime.now()
    number = find_current_count()
    number += 1
    file_consent_form(number, name, date, timestamp)
    return redirect("/counter1")


@app.route('/counter1', methods = ["POST", "GET"])
def wadden_buggy1():
    if request.method == "POST":
        lines_to_write = request.get_json()["inputs"]
        write_file("/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/first_counter_overflow_wadden_buggy1.v", lines_to_write)
    all_lines, implicated_lines, fitness_score, syntax_error = run_cirfix("FIRST_COUNTER_OVERFLOW_WADDEN_BUGGY1", "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/first_counter_overflow_wadden_buggy1.v")
    line_tuple = implicated_tuple(all_lines, implicated_lines)
    
    if request.method == "POST":
        return redirect("/counter1")
    else:
        return render_template("buggy_code.html", 
        title = "/counter1", next = "/counter2", line_tuple = line_tuple, fitness_score = fitness_score, syntax_error = syntax_error)    


#kgoliya_buggy1
@app.route('/counter2', methods = ["POST", "GET"])
def kgoliya_buggy1():
    if request.method == "POST":
        lines_to_write = request.get_json()["inputs"]
        write_file("/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/first_counter_overflow_kgoliya_buggy1.v", lines_to_write)
    #here we are taking the source file and running cirfix on it to get implicated lines
    all_lines, implicated_lines, fitness_score, syntax_error = run_cirfix("FIRST_COUNTER_OVERFLOW_KGOLIYA_BUGGY1", "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/first_counter_overflow_kgoliya_buggy1.v")
    line_tuple = implicated_tuple(all_lines, implicated_lines)
    if request.method == "POST":
        return redirect(url_for("counter2"))
    else:
        return render_template("buggy_code.html", 
        title = "/counter2", next = "/finite_state_machine1", line_tuple = line_tuple, fitness_score = fitness_score, syntax_error = syntax_error)

#fsm_full_wadden_buggy1
@app.route('/finite_state_machine1', methods = ["POST", "GET"])
def fsm_full_wadden_buggy():
    if request.method == "POST":
        lines_to_write = request.get_json()["inputs"]
        write_file("/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/fsm_full_wadden_buggy1.v", lines_to_write)
    #here we are taking the source file and running cirfix on it to get implicated lines
    all_lines, implicated_lines, fitness_score, syntax_error = run_cirfix("FSM_FULL_WADDEN_BUGGY1", "/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/fsm_full_wadden_buggy1.v")
    line_tuple = implicated_tuple(all_lines, implicated_lines)
    if request.method == "POST":
        return redirect(url_for("finite_state_machine1"))
    else:
        return render_template("buggy_code.html", 
        title = "/finite_state_machine1", next = "/counter3", line_tuple = line_tuple, fitness_score = fitness_score, syntax_error = syntax_error)

#first_counter_overflow_wadden_buggy2
@app.route('/counter3', methods = ["POST", "GET"])
def wadden_buggy2():
    if request.method == "POST":
        lines_to_write = request.get_json()["inputs"]
        write_file("/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/fsm_full_wadden_buggy1.v", lines_to_write)
    #here we are taking the source file and running cirfix on it to get implicated lines
    all_lines, implicated_lines, fitness_score, syntax_error = run_cirfix("FIRST_COUNTER_OVERFLOW_WADDEN_BUGGY2", "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/first_counter_overflow_wadden_buggy2.v")
    line_tuple = implicated_tuple(all_lines, implicated_lines)
    if request.method == "POST":
        return redirect(url_for("counter3"))
    else:
        return render_template("buggy_code.html", 
        title = "/counter3", next = "/lshift_reg1", line_tuple = line_tuple, fitness_score = fitness_score, syntax_error = syntax_error)

#lshift_reg_wadden_buggy1
@app.route('/left_shift_register1', methods = ["POST", "GET"])
def lshift_reg():
    if request.method == "POST":
        lines_to_write = request.get_json()["inputs"]
        write_file("/home/jvelten/projects/verilog_repair/benchmarks/lshift_reg/lshift_reg_wadden_buggy1.v", lines_to_write)
    #here we are taking the source file and running cirfix on it to get implicated lines
    all_lines, implicated_lines, fitness_score, syntax_error = run_cirfix("LSHIFT_REG_WADDEN_BUGGY1", "/home/jvelten/projects/verilog_repair/benchmarks/lshift_reg/lshift_reg_wadden_buggy1.v")
    line_tuple = implicated_tuple(all_lines, implicated_lines)
    if request.method == "POST":
        return redirect(url_for("left_shift_register1"))
    else:
        return render_template("buggy_code.html", 
        title = "/left_shift_register1", next = "/end", line_tuple = line_tuple, fitness_score = fitness_score, syntax_error = syntax_error)


@app.get('/end')
def end():
    return render_template("end.html")


def write_file(source, all_lines):
    with open(source, 'w') as file:
        for line in all_lines:
            file.write(line + '\n')
    

def implicated_tuple(verilog_code, implicated_lines):
    line_tuple = []
    for i in range(len(implicated_lines)):
        implicated_lines[i] = implicated_lines[i].strip()
    for line in verilog_code:
        if line.strip() in implicated_lines and line != '\n':
            line_tuple.append([line, 1])
        else:
            line_tuple.append([line, 0])
    return line_tuple

    

def run_cirfix(bug, source):
    #now we get all the lines from the file
    with open(source) as f:
        all_lines = f.readlines()

    #if we've already seen this configuration of verilog code
    # if check_data(all_lines) == True:
    #     implicated_lines = fetch_implicated_lines(all_lines)
    #     output = [all_lines, implicated_lines]
        
        
    #     return output
    os.chdir("..")
    #also get fitness score
    #will be zero when theres compilation error 

    implicated_lines = subprocess.getoutput(f"python3 joshua.py {bug}")
    fitness_score = implicated_lines
    os.chdir("./verilog_web")
    try:
        imp_index = implicated_lines.index("IMPLICATED LINES:") + 17
        implicated_lines = implicated_lines[imp_index:]
        implicated_lines = implicated_lines.splitlines()
    except:
        implicated_lines = []
    
    try:
        fitness_index = fitness_score.index("Fitness = ")
        fitness_score = fitness_score[fitness_index + 10: fitness_index + 18]
    except:
        fitness_score == "0.000000"

    if fitness_score == "0.000000" and implicated_lines == []:
        syntax_error = True
    else:
        syntax_error = False
    # store_data(all_lines, implicated_lines)
    output = [all_lines, implicated_lines, fitness_score, syntax_error]
    return output



def store_data(all_lines, implicated_lines):
    conn = sql.connect('memoization.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO line_lookup (all_lines, implicated_lines) VALUES (?, ?)",
                   (str(all_lines), str(implicated_lines)))
    conn.commit()
    conn.close()

    return "Data stored successfully"

#returns true if matching config found
#returns false if not found
def check_data(all_lines):
    conn = sql.connect('memoization.db')
    cursor = conn.cursor()
    cursor.execute("SELECT implicated_lines FROM line_lookup WHERE all_lines=?", (str(all_lines),))
    result = cursor.fetchone()
    if result:
        return True
    return False

def fetch_implicated_lines(all_lines):
    conn = sql.connect('memoization.db')
    cursor = conn.cursor()
    key = str(all_lines)
    query = "SELECT implicated_lines FROM line_lookup WHERE all_lines = ?"
    cursor.execute(query, (key,))
    result = cursor.fetchone()
    implicated_lines = eval(result[0])
    return implicated_lines

def find_current_count():
    conn = sql.connect('memoization.db')
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(number) FROM consent_form")
    number = cursor.fetchone()[0]
    print("PRINTING NUMBER")
    print(number)
    print("END")
    if number is not None:
        result = number
    else:
        result = 0
    cursor.close()
    conn.close()
    return result

def file_consent_form(number, name, date, timestamp):
    conn = sql.connect('memoization.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO consent_form (number, name, date, timestamp) VALUES (?, ?, ?, ?)",
                   (number, str(name), str(date), str(timestamp)))
    conn.commit()
    conn.close()