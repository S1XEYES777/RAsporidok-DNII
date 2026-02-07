let dates = [];
let selectedIndex = 0;

function formatISO(d){
  return d.toISOString().split("T")[0];
}

function buildDates(){
  dates = [];
  const base = new Date();
  for(let i=0;i<7;i++){
    const d = new Date(base);
    d.setDate(base.getDate() + i);
    dates.push({
      iso: formatISO(d),
      label: i===0 ? "Сегодня" : (i===1 ? "Завтра" : `+${i} дней`)
    });
  }
}

function escapeHtml(s){
  return (s||"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;");
}

function avatarSrc(base64){
  return base64 ? ("data:image/png;base64," + base64) : "/static/avatars/default.png";
}

/* ---------- Конфетти ---------- */
function confettiBurst(){
  const canvas = document.createElement("canvas");
  canvas.style.position = "fixed";
  canvas.style.left = "0";
  canvas.style.top = "0";
  canvas.style.width = "100%";
  canvas.style.height = "100%";
  canvas.style.pointerEvents = "none";
  canvas.style.zIndex = "9999";
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

    if(t < 120) requestAnimationFrame(tick);
    else canvas.remove();
  }
  tick();
}

/* ---------- Рендер чипов дат ---------- */
function renderDateChips(){
  const chips = document.getElementById("dateChips");
  const label = document.getElementById("selectedLabel");
  if(!chips) return;

  chips.innerHTML = dates.map((d, idx)=>`
    <div class="date-chip ${idx===selectedIndex ? "active" : ""}" onclick="selectDate(${idx})">
      ${d.label}
      <span class="text-muted" style="font-weight:600; margin-left:6px;">${d.iso}</span>
    </div>
  `).join("");

  label.textContent = dates[selectedIndex].iso;
}

window.selectDate = function(idx){
  selectedIndex = Math.max(0, Math.min(dates.length-1, idx));
  renderDateChips();
  load();
}

/* ---------- Свайп (на телефоне) ---------- */
function enableSwipe(){
  const bar = document.getElementById("dateBar");
  if(!bar) return;

  let startX = 0;
  let startY = 0;
  let moving = false;

  bar.addEventListener("touchstart", (e)=>{
    const t = e.touches[0];
    startX = t.clientX;
    startY = t.clientY;
    moving = true;
  }, {passive:true});

  bar.addEventListener("touchmove", (e)=>{
    if(!moving) return;
    const t = e.touches[0];
    const dx = t.clientX - startX;
    const dy = t.clientY - startY;

    // если человек скроллит вниз — не мешаем
    if(Math.abs(dy) > Math.abs(dx)) return;
  }, {passive:true});

  bar.addEventListener("touchend", (e)=>{
    if(!moving) return;
    moving = false;

    const t = e.changedTouches[0];
    const dx = t.clientX - startX;

    const threshold = 45; // насколько надо свайпнуть
    if(dx <= -threshold){
      // влево -> следующий день
      if(selectedIndex < dates.length-1){
        selectedIndex++;
        renderDateChips();
        load();
      }
    } else if(dx >= threshold){
      // вправо -> предыдущий день
      if(selectedIndex > 0){
        selectedIndex--;
        renderDateChips();
        load();
      }
    }
  }, {passive:true});
}

/* ---------- Загрузка ---------- */
async function load(){
  try{
    const selected = dates[selectedIndex].iso;
    const res = await fetch(`/api/data?date=${encodeURIComponent(selected)}`);
    const data = await res.json();
    if(data.error) return;

    const cards = document.getElementById("cards");
    let html = "";

    data.users.forEach(u=>{
      html += `
        <div class="col-12 col-md-6 col-lg-4 mb-3">
          <div class="card p-3">
            <div class="d-flex align-items-center gap-2 mb-2">
              <img src="${avatarSrc(u.avatar)}" class="avatar" alt="av">
              <div>
                <div class="fw-semibold">${escapeHtml(u.name)}</div>
                <div class="small text-muted">Планы на ${dates[selectedIndex].iso}</div>
              </div>
            </div>
      `;

      if(u.tasks && u.tasks.length){
        u.tasks.forEach(t=>{
          const showCongratsBtn = (t.completed && data.me !== t.ownerId && !t.youCongrat);
          const congratsCount = (t.congrats && t.congrats>0) ? `<span class="small text-muted ms-2">🎉 ${t.congrats}</span>` : "";

          html += `
            <div class="task diff${t.difficulty}">
              <div class="me-2">
                <div class="fw-semibold">${escapeHtml(t.text)}</div>
                <div class="small text-muted">
                  ${t.completed ? "✅ Выполнено" : "⏳ В процессе"} ${congratsCount}
                </div>
              </div>

              <div class="d-flex align-items-center gap-2">
                ${showCongratsBtn ? `<button class="btn btn-primary btn-sm" onclick="congrat(${t.id})">🎉</button>` : ``}
              </div>
            </div>
          `;
        });
      } else {
        html += `<div class="text-muted">Нет задач 😎</div>`;
      }

      html += `</div></div>`;
    });

    cards.innerHTML = html;
  } catch (e){
    console.log("Load error:", e);
  }
}

/* ---------- Поздравление ---------- */
window.congrat = async function(taskId){
  try{
    const res = await fetch("/api/congrat", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({task_id: taskId})
    });
    const data = await res.json();
    if(data.ok){
      confettiBurst();
      await load();
    }
  } catch(e){
    console.log("Congrat error:", e);
  }
}

/* ---------- Старт ---------- */
buildDates();
renderDateChips();
enableSwipe();
load();
setInterval(load, 4000);
