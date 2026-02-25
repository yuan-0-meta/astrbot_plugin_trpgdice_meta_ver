(function(){
  const $ = id => document.getElementById(id);
  const loadBtn = $('loadBtn');
  const userIdIn = $('userId');
  const charList = $('charList');
  const detailArea = $('detailArea');
  const detailTitle = $('detailTitle');
  const saveBtn = $('saveBtn');
  const setCurrentBtn = $('setCurrentBtn');
  const newBtn = $('newBtn');

  let currentUser = null;
  let currentChar = null;
  let fetchedChars = [];

  function renderList(){
    charList.innerHTML = '';
    fetchedChars.forEach(ch=>{
      const li = document.createElement('li');
      li.textContent = ch.name + (ch.is_current? ' (当前)':'');
      li.dataset.id = ch.id;
      li.onclick = ()=>loadCharDetail(ch.id);
      charList.appendChild(li);
    })
  }

  async function loadCharacters(){
    const uid = userIdIn.value.trim();
    if(!uid) return alert('请输入 user_id');
    currentUser = uid;
    const res = await fetch(`/api/characters/${encodeURIComponent(uid)}`);
    if(!res.ok) return alert('加载失败');
    const body = await res.json();
    fetchedChars = body.characters || [];
    renderList();
    detailArea.textContent = '请选择一个角色';
  }

  async function loadCharDetail(id){
    const res = await fetch(`/api/characters/${encodeURIComponent(currentUser)}/${encodeURIComponent(id)}`);
    if(!res.ok) return alert('读取角色失败');
    const data = await res.json();
    currentChar = data;
    detailTitle.textContent = data.name || '角色详情';

    // 格式化展示：可编辑的字段表单（name + attributes 列表）
    detailArea.innerHTML = '';

    const nameRow = document.createElement('div');
    const nameLabel = document.createElement('label');
    nameLabel.textContent = '名字：';
    const nameInput = document.createElement('input');
    nameInput.value = data.name || '';
    nameInput.style.marginLeft = '8px';
    nameRow.appendChild(nameLabel);
    nameRow.appendChild(nameInput);
    detailArea.appendChild(nameRow);

    const attrTitle = document.createElement('h3');
    attrTitle.textContent = '属性';
    detailArea.appendChild(attrTitle);

    const attrTable = document.createElement('div');
    attrTable.style.display = 'grid';
    attrTable.style.gridTemplateColumns = '1fr 1fr';
    attrTable.style.gap = '8px';

    const attrs = data.attributes || {};
    // Render existing attributes
    Object.keys(attrs).forEach(key=>{
      const kInput = document.createElement('input');
      kInput.value = key;
      const vInput = document.createElement('input');
      vInput.value = String(attrs[key]);
      kInput.dataset.role = 'attr-key';
      vInput.dataset.role = 'attr-val';
      attrTable.appendChild(kInput);
      attrTable.appendChild(vInput);
    });

    // Add one empty row for convenience
    const addK = document.createElement('input'); addK.placeholder='新属性名'; addK.dataset.role='attr-key';
    const addV = document.createElement('input'); addV.placeholder='值'; addV.dataset.role='attr-val';
    attrTable.appendChild(addK); attrTable.appendChild(addV);

    detailArea.appendChild(attrTable);

    // store references for save
    detailArea._nameInput = nameInput;
    detailArea._attrTable = attrTable;
  }

  async function saveCurrent(){
    if(!currentUser || !currentChar) return alert('未选中角色');
    const nameInput = detailArea._nameInput;
    const table = detailArea._attrTable;
    if(!nameInput || !table) return alert('无可保存内容');

    // 收集属性
    const inputs = Array.from(table.querySelectorAll('input'));
    const attrs = {};
    for(let i=0;i<inputs.length;i+=2){
      const k = inputs[i].value && inputs[i].value.trim();
      const v = inputs[i+1].value && inputs[i+1].value.trim();
      if(k){
        // 尝试把数值字符串转为 number，否则保留原字符串
        const num = Number(v);
        attrs[k] = (v!=='' && !isNaN(num)) ? num : v;
      }
    }

    const payload = Object.assign({}, currentChar, {name: nameInput.value || '角色', attributes: attrs});

    const res = await fetch(`/api/characters/${encodeURIComponent(currentUser)}/${encodeURIComponent(currentChar.id)}`,{
      method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)
    });
    if(!res.ok) return alert('保存失败');
    alert('保存成功');
    loadCharacters();
  }

  async function setCurrent(){
    if(!currentUser || !currentChar) return alert('未选中角色');
    const res = await fetch(`/api/characters/${encodeURIComponent(currentUser)}/current/${encodeURIComponent(currentChar.id)}`,{method:'POST'});
    if(!res.ok) return alert('设置失败');
    alert('已设为当前角色');
    loadCharacters();
  }

  async function createEmpty(){
    if(!currentUser) return alert('请先输入并加载 user_id');
    const template = {id: Date.now().toString(36), name:'新角色', attributes:{}};
    // 直接保存到文件：调用 PUT
    const res = await fetch(`/api/characters/${encodeURIComponent(currentUser)}/${encodeURIComponent(template.id)}`,{
      method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(template)
    });
    if(!res.ok) return alert('创建失败');
    alert('已创建新角色');
    loadCharacters();
  }

  loadBtn.onclick = loadCharacters;
  saveBtn.onclick = saveCurrent;
  setCurrentBtn.onclick = setCurrent;
  newBtn.onclick = createEmpty;

  // 如果页面脚本加载前页面写入了预填 user_id，则自动填充并触发加载
  window.addEventListener('DOMContentLoaded', ()=>{
    try{
      const pre = window._prefilled_user_id;
      if(pre){
        userIdIn.value = pre;
        // 延迟触发，确保一切就绪
        setTimeout(()=>{ loadCharacters(); }, 120);
      }
    }catch(e){}
  });
})();