async function load(){

let r = await fetch("/api/data")
let data = await r.json()

let html=""

data.forEach(u=>{

html+=`
<div class="card p-3 mb-3">

<div class="d-flex align-items-center mb-2">

<img src="${u.avatar ? 'data:image/png;base64,' + u.avatar : '/static/avatars/default.png'}" class="avatar">

<h5 class="ms-2">${u.name}</h5>

</div>
`

if(u.tasks.length>0){

u.tasks.forEach(t=>{

html+=`
<div class="task diff${t.difficulty}">

<span>${t.text}</span>

<span>

${t.completed ? "✅" : ""}

${t.completed && !t.user_congrat ? 
`<button onclick="congrat(${t.id})" class="btn btn-primary btn-sm">🎉</button>` : ""}

${t.congrats > 0 ? `<small>${t.congrats}</small>` : ""}

</span>

</div>
`
})

}
else{
html+=`Сегодня отдыхает 😎`
}

html+=`</div>`
})

document.getElementById("cards").innerHTML=html
}

async function congrat(id){
await fetch("/congrat/"+id)
load()
}

setInterval(load,3000)
load()
