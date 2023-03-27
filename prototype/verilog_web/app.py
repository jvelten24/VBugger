from flask import Flask, render_template, send_file, request, redirect, url_for, g
import os, subprocess
import ast
import json
app = Flask(__name__)
#app.config["TEMPLATES_AUTO_RELOAD"] = True
import sqlite3 as sql



#home page
@app.route("/")
def home():
    return render_template('home.html')


@app.route('/wadden_buggy1', methods = ["POST", "GET"])
def wadden_buggy1():
    if request.method == "POST":
        lines_to_write = request.get_json()["inputs"]
        write_file("/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/first_counter_overflow_wadden_buggy1.v", lines_to_write)
    all_lines, implicated_lines = run_cirfix("FIRST_COUNTER_OVERFLOW_WADDEN_BUGGY1", "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/first_counter_overflow_wadden_buggy1.v")
    line_tuple = implicated_tuple(all_lines, implicated_lines)
    
    if request.method == "POST":
        return redirect(url_for("wadden_buggy1"))
    else:
        return render_template("buggy_code.html", 
        title = "/wadden_buggy1", next = "/kgoliya_buggy1", line_tuple = line_tuple)    

@app.get('/kgoliya_buggy1')
def kgoliya_buggy1():
    #here we are taking the source file and running cirfix on it to get implicated lines
    all_lines, implicated_lines = run_cirfix("FIRST_COUNTER_OVERFLOW_KGOLIYA_BUGGY1", "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/first_counter_overflow_kgoliya_buggy1.v")
    line_tuple = implicated_tuple(all_lines, implicated_lines)
    return render_template("buggy_code.html", 
    title = "/kgoliya_buggy1", next = "/fsm_full_wadden_buggy1", line_tuple = line_tuple)

@app.post('/kgoliya_buggy1')
def kgoliya_buggy1_post():
    lines_to_write = request.get_json()["inputs"]
    write_file("/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/first_counter_overflow_kgoliya_buggy1.v", lines_to_write)
    all_lines, implicated_lines = run_cirfix("FIRST_COUNTER_OVERFLOW_KGOLIYA_BUGGY1", "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/first_counter_overflow_kgoliya_buggy1.v")
    line_tuple = implicated_tuple(all_lines, implicated_lines)
    return render_template("buggy_code.html", 
    title = "/kgoliya_buggy1", next = "/fsm_full_wadden_buggy1", line_tuple = line_tuple)


@app.get('/fsm_full_wadden_buggy1')
def fsm_full_wadden_buggy():
    #here we are taking the source file and running cirfix on it to get implicated lines
    all_lines, implicated_lines = run_cirfix("FSM_FULL_WADDEN_BUGGY1", "/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/fsm_full_wadden_buggy1.v")
    line_tuple = implicated_tuple(all_lines, implicated_lines)
    return render_template("buggy_code.html", 
    title = "/fsm_full_wadden_buggy1", next = "/wadden_buggy2", line_tuple = line_tuple)

@app.post('/fsm_full_wadden_buggy1')
def fsm_full_wadden_buggy_post():
    lines_to_write = request.get_json()["inputs"]
    write_file("/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/fsm_full_wadden_buggy1.v", lines_to_write)
    #here we are taking the source file and running cirfix on it to get implicated lines
    all_lines, implicated_lines = run_cirfix("FSM_FULL_WADDEN_BUGGY1", "/home/jvelten/projects/verilog_repair/benchmarks/fsm_full/fsm_full_wadden_buggy1.v")
    line_tuple = implicated_tuple(all_lines, implicated_lines)
    return render_template("buggy_code.html", 
    title = "/fsm_full_wadden_buggy1", next = "/wadden_buggy2", line_tuple = line_tuple)

@app.get('/wadden_buggy2')
def wadden_buggy2():
    #here we are taking the source file and running cirfix on it to get implicated lines
    all_lines, implicated_lines = run_cirfix("FIRST_COUNTER_OVERFLOW_WADDEN_BUGGY2", "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/first_counter_overflow_wadden_buggy2.v")
    line_tuple = implicated_tuple(all_lines, implicated_lines)
    return render_template("buggy_code.html", 
    title = "/wadden_buggy2", next = "/lshift_reg_wadden_buggy1", line_tuple = line_tuple)

@app.post('/wadden_buggy2')
def wadden_buggy2_post():
    lines_to_write = request.get_json()["inputs"]
    write_file("/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/first_counter_overflow_wadden_buggy2.v", lines_to_write)
    #here we are taking the source file and running cirfix on it to get implicated lines
    all_lines, implicated_lines = run_cirfix("FIRST_COUNTER_OVERFLOW_WADDEN_BUGGY2", "/home/jvelten/projects/verilog_repair/benchmarks/first_counter_overflow/first_counter_overflow_wadden_buggy2.v")
    line_tuple = implicated_tuple(all_lines, implicated_lines)
    return render_template("buggy_code.html", 
    title = "/wadden_buggy2", next = "/lshift_reg_wadden_buggy1", line_tuple = line_tuple)

@app.get('/lshift_reg_wadden_buggy1')
def lshift_reg():
    #here we are taking the source file and running cirfix on it to get implicated lines
    all_lines, implicated_lines = run_cirfix("LSHIFT_REG_WADDEN_BUGGY1", "/home/jvelten/projects/verilog_repair/benchmarks/lshift_reg/lshift_reg_wadden_buggy1.v")
    line_tuple = implicated_tuple(all_lines, implicated_lines)
    return render_template("buggy_code.html", 
    title = "/lshift_reg", next = "/end", line_tuple = line_tuple)

@app.post('/lshift_reg_wadden_buggy1')
def lshift_reg_post():
    lines_to_write = request.get_json()["inputs"]
    write_file("/home/jvelten/projects/verilog_repair/benchmarks/lshift_reg/lshift_reg_wadden_buggy1.v", lines_to_write)
    #here we are taking the source file and running cirfix on it to get implicated lines
    all_lines, implicated_lines = run_cirfix("LSHIFT_REG_WADDEN_BUGGY1", "/home/jvelten/projects/verilog_repair/benchmarks/lshift_reg/lshift_reg_wadden_buggy1.v")
    line_tuple = implicated_tuple(all_lines, implicated_lines)
    return render_template("buggy_code.html", 
    title = "/lshift_reg", next = "/end", line_tuple = line_tuple)

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
            line_tuple.append((line, 1))
        else:
            line_tuple.append((line, 0))
    return line_tuple

    

def run_cirfix(bug, source):
    #now we get all the lines from the file
    with open(source) as f:
        all_lines = f.readlines()

    #if we've already seen this configuration of verilog code
    if check_data(all_lines) == True:
        implicated_lines = fetch_implicated_lines(all_lines)
        output = [all_lines, implicated_lines]
        print("check_data returns true")
        print(output)
        
        return output
    os.chdir("..")
    implicated_lines = subprocess.getoutput(f"python3 joshua.py {bug}")
    os.chdir("./verilog_web")
    try:
        imp_index = implicated_lines.index("IMPLICATED LINES:") + 17
        implicated_lines = implicated_lines[imp_index:]
        implicated_lines = implicated_lines.splitlines()
    except:
        implicated_lines = []
    store_data(all_lines, implicated_lines)
    output = [all_lines, implicated_lines]
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