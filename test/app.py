import domapi
from flask import Flask

app = Flask(__name__)

document = domapi.make_document_from_str(
	open(f"html/index.html", 'r').read()
)

document._exec_js_dom_func(
	open("js/index.js", 'r')
		.read()
			.split("////")[0]
)

heading = document.getElementById("myheading")
divs = document.getElementsByTagName('div')

divs[0].children[0].innerText = f"'{heading.innerText}' - Copied over from heading!"
divs[0].children[1].innerText = "cool"
p1, p2, *_ = divs[0].children

p1.className+=" my-other-text-class"

attr = document.createAttribute("style")
attr.value = "color: red;"

p2.attributes.setNamedItem(attr)

script = document.createElement("script")

script.innerText = """
const runasync = 
	(func) => setTimeout(func, 0)

const a = 
	() => {
		runasync(() => window.alert("button clicked!"))
		
		const p = document.getElementById("p2")
		
		if (p.innerText == "cool")
			p.innerText = "wow"
		else
			p.innerText = "cool"
	}
"""

script.attributes.setNamedItem(
	document.createAttribute("defer")
)

document.head.append(
	script
)

if app.debug:
	print(document._stringify())

@app.route('/')
def index():
	return document._stringify()