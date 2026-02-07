// ---------- Конфетти ----------
function confettiBurst(){

const canvas = document.createElement("canvas")
canvas.style.position = "fixed"
canvas.style.left = "0"
canvas.style.top = "0"
canvas.style.width = "100%"
canvas.style.height = "100%"
canvas.style.pointerEvents = "none"
canvas.style.zIndex = "9999"

document.body.appendChild(canvas)

const ctx = canvas.getContext("2d")
canvas.width = window.innerWidth
canvas.height = window.innerHeight

const particles = []

const colors = ["#ff6b6b","#ffd93d","#6bcBef","#6bff95","#b28dff"]

for(let i=0;i<120;i++){

particles.push({
x:canvas.width/2,
y:canvas.height/4,
vx:(Math.random()-0.5)*10,
vy:Math.random()*-8,
gravity:0.25,
size:4+Math.random()*6,
color:colors[Math.floor(Math.random()*colors.length)],
rotation:Math.random()*360
})

}

let frame = 0

function draw(){

ctx.clearRect(0,0,canvas.width,canvas.height)

particles.forEach(p=>{

p.vy+=p.gravity
p.x+=p.vx
p.y+=p.vy
p.rotation+=2

ctx.save()
ctx.translate(p.x,p.y)
ctx.rotate(p.rotation*Math.PI/180)
ctx.fillStyle=p.color
ctx.fillRect(-p.size/2,-p.size/2,p.size,p.size)
ctx.restore()

})

frame++

if(frame<120){
requestAnimationFrame(draw)
}else{
canvas.remove()
}

}

draw()

}



// ---------- Экранирование текста ----------
function escapeHtml(text){

return text
.replaceAll("&","&amp;")
.replaceAll("<","&lt;")
.replaceAll(">","&gt;")

}



// ---------- Загрузка данных ----------
async function load(){

try{

let r = await fetch("/api/data")
let data = await r.json()

let html=""

data.forEach(u=>{

html+=`
<div class="col-md-4 col-12 mb-3">
<div class="card p-3 user-card">

<div class="d-flex align-items-center mb-2">

<img src="${u.avatar ? 'data:image/png;base64,' + u.avatar : '/static/avatars/default.png'}" class="avatar">

<h5 class="ms-2">${escapeHtml(u.name)}</h5>

</div>
`


// ---------- Задачи ----------
if(u.tasks.length>0){

u.tasks.forEach(t=>{

html+=`
<div class="task diff${t.difficulty}">

<span>${escapeHtml(t.text)}</span>

<span class="task-actions">

${t.completed ? '<span class="done-icon">✅</span>' : ""}

${t.completed && !t.user_congrat ? 
`<button onclick="congrat(${t.id})" class="btn btn-primary btn-sm congrats-btn">🎉</button>` : ""}

${t.congrats > 0 ? `<small class="ms-1">🎉 ${t.congrats}</small>` : ""}

</span>

</div>
`
})

}
else{
html+=`<div class="text-muted">Сегодня отдыхает 😎</div>`
}

html+=`</div></div>`

})


document.getElementById("cards").innerHTML = html

}
catch(e){
console.log("Ошибка загрузки:", e)
}

}



// ---------- Поздравление ----------
async function congrat(id){

try{

await fetch("/congrat/"+id)

confettiBurst()

load()

}
catch(e){
console.log("Ошибка поздравления:", e)
}

}



// ---------- Авто обновление ----------
setInterval(load, 3000)


// ---------- Первый запуск ----------
load()
