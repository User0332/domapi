import domapi
import sys
from flask import Flask, render_template_string

DEBUG = (
	True if (len(sys.argv) > 1) and 
	(sys.argv[1] == "debug") else False
)

app = Flask(__name__)
app.debug = True

document = domapi.make_document_from_str(
	open(f"html/index.html", 'r').read()
)

document._exec_js_dom_func(
	open("js/index.js", 'r').read()
)

heading = document.getElementById("myheading")
divs = document.getElementsByTagName('div')

divs[0].children[0].innerText = f"'{heading.innerText}' - Copied over from heading!"
divs[0].children[1].innerText = "cool"
p1, p2, *_ = divs[0].children

p1.className+=" my-other-text-class"

attr = domapi.webapi_classes.Attr(
	"style",
	p2
)

attr.value = "color: red;"

p2.attributes.setNamedItem(attr)

script = document.createElement("script")

script.innerText = """
const a = () => {
	window.alert("button clicked!")
	
	const p=document.getElementById("p2")
	
	if (p.innerText == "cool")
		p.innerText = "wow"
	else
		p.innerText = "cool"
}"""

document.head.append(
	script
)

if DEBUG:
	print(
		document.children
	)
	print(document._stringify(True))
	exit(0)

@app.route('/')
def index():
	return document._minify(True)