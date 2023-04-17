//so what i want to do is prepopulate value with implicated lines
//then get the implicated line numbers
//and make those highlighted


// const editor = CodeMirror(document.querySelector('#verilog-editor'), {
//     lineNumbers: true,
//     tabSize: 2,
//     value: "joshua"
//   });

  let allLines = document.querySelector('#all_lines').value;
  allLines = allLines.slice(1, -1)
  allLines = allLines.slice(1, -1);
  allLines = allLines.split(", ");
  for (let i = 0; i < allLines.length; i++) {
    allLines[i] = allLines[i].replace(/^'|'$/g, '');
  }

  var editor = CodeMirror(document.querySelector('#verilog-editor'), {
    lineNumbers: true,
    tabSize: 4,
    mode: "verilog",
  })

for (let i = 0; i < allLines.length; i++){
  editor.replaceRange(allLines[i] + "\n", { line: i, ch: 0 });
}


  const update = document.getElementsByClassName("update-code")[0];
  update.addEventListener("click", (e) => {
    e.preventDefault();
    let editor = document.getElementById("verilog-editor");
    let text = editor.innerText;
    console.log(text)

    fetch('/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({text: text})
    })
    .then(response => response.json())
    .then(data => console.log(data));
    // .catch(error => console.error(error));
  })