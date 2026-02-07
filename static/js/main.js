function escapeHtml(s){
  return (s||"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;");
}

function randomNoTasks(name){
  const a = [
    "Сегодня отдыхает 😎",
    "Сегодня без задач 💤",
    "Сегодня режим лайт ✅",
    "Сегодня легенда чиллит 👑"
  ];
  return `${name}: ${a[Math.floor(Math.random()*a.length)]}`;
}

function confettiBurst(){
  // лёгкое конфетти без библиотек
  const canvas = document.createElement("canvas");
  canvas.style.position = "fixed";
  canvas.style.left = "0";
  canvas.style.top = "0";
  canvas.style.width = "100%";
  canvas.style.height = "100%";
  canvas.style.pointerEvents = "none";
  canvas.style.zIndex = "3000";
  document.body.appendChild(canvas);

  const ctx = canvas.getContext("2d");
  const w = canvas.width = window.innerWidth;
  const h = canvas.height = window.innerHeight;

  const colors = ["#ff6b6b","#ffd93d","#6bcBef","#6bff95","#b28dff"];
  const parts = [];
  for(let i=0;i<140;i++){
    parts.push({
      x: w*0.5,
      y: h*0.25,
      vx: (Math.random()-0.5)*10,
      vy: Math.random()*-8 - 4,
      g: 0.25 + Math.random()*0.2,
      s: 4 + Math.random()*5,
      c: colors[Math.floor(Math.random()*colors.length)],
      r: Math.random()*Math.PI
    });
  }

  let t = 0;
  function tick(){
    t++;
    ctx.clearRect(0,0,w,h);
    parts.forEach(p=>{
      p.vy += p.g;
      p.x += p.vx;
      p.y += p.vy;
      p.r += 0.2;

      ctx.save();
      ctx.translate(p.x,p.y);
      ctx.rotate(p.r);
      ctx.fillStyle = p.c;
      ctx.fillRect(-p.s/2,-p.s/2,p.s,p.s);
      ctx.restore();
    });

    if(t < 120){
      requestAnimationFrame(tick);
    } else {
      canvas.remove();
    }
  }
  tick();
}

async function loadToday(){
  const res = await fetch("/api/today");
  const data = await res.json();
  if(data.error) return;

  const todayLabel = document.getElementById("todayLabel");
  const cards = document.getElementById("cards");
  todayLabel.textContent = data.today;

  let html = "";
  data.users.forEach(u=>{
    html += `
      <div class="col-12 col-md-6 col-lg-4 mb-3">
        <div class="card p-3">
          <div class="d-flex align-items-center gap-2 mb-2">
            <img src="/static/avatars/${escapeHtml(u.avatar||"default.png")}" class="avatar" alt="av">
            <div>
              <div class="fw-semibold">${escapeHtml(u.name)}</div>
              <div class="small text-muted">Задачи на сегодня</div>
            </div>
          </div>
    `;

    if(u.tasks && u.tasks.length){
      u.tasks.forEach(t=>{
        const done = t.completed ? "✅" : "";
        const showCongratsBtn = (t.completed && data.me !== t.ownerId && !t.youCongrat);
        const congratsCount = (t.congrats && t.congrats>0) ? `<span class="small text-muted ms-2">🎉 ${t.congrats}</span>` : "";

        html += `
          <div class="task diff${t.difficulty}">
            <div class="me-2">
              <div class="fw-semibold">${escapeHtml(t.text)}</div>
              <div class="small text-muted">${done} ${congratsCount}</div>
            </div>

            <div class="d-flex align-items-center gap-2">
              ${t.completed ? `<span class="badge text-bg-success">Готово</span>` : ``}
              ${showCongratsBtn ? `<button class="btn btn-primary btn-sm" onclick="congrat(${t.id})">🎉</button>` : ``}
            </div>
          </div>
        `;
      });
    } else {
      html += `<div class="text-muted">${escapeHtml(randomNoTasks(u.name))}</div>`;
    }

    html += `</div></div>`;
  });

  cards.innerHTML = html;
}

async function congrat(taskId){
  const res = await fetch("/api/congrat", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({task_id: taskId})
  });
  const data = await res.json();
  if(data.ok){
    confettiBurst();
    await loadToday();
  }
}

loadToday();
setInterval(loadToday, 4000);
