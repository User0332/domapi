import domapi
from flask import Flask

app = Flask(__name__)

document = domapi.make_document_from_str(
	open(f"html/index.html", 'r').read()
)

document._exec_js_dom_func(
	open("js/index.js", 'r')
		.read()
			.rsplit("////", 1)[0]
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

document.querySelector("button[name='clickity']")
	.onclick = () => {
		runasync(() => window.alert("button clicked!"))
		
		const p = document.getElementById("p2")
		
		if (p.textContent == "cool")
			p.textContent = "wow"
		else
			p.textContent = "cool"
	}
"""

document.body.append(
	script
)

if app.debug:
	print(document._stringify())
	print(document.querySelectorAll('p.my-text-class#p2[style="color: red;"]'))

@app.route('/')
def index():
	return document._stringify()