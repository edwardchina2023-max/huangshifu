// FDE黄师傅 · 站点交互
(function () {
  'use strict';

  // 移动端导航
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      nav.classList.toggle('open');
    });
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') nav.classList.remove('open');
    });
  }

  // 当前页高亮
  var here = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav a').forEach(function (a) {
    var href = a.getAttribute('href');
    if (href === here || (here === '' && href === 'index.html')) {
      a.classList.add('active');
    }
  });

  // 图片灯箱（视觉资产墙）
  var shots = document.querySelectorAll('.gallery .shot img');
  if (shots.length) {
    var lb = document.createElement('div');
    lb.style.cssText = 'position:fixed;inset:0;background:rgba(18,26,36,.92);display:none;' +
      'align-items:center;justify-content:center;z-index:999;padding:30px;cursor:zoom-out;';
    var lbImg = document.createElement('img');
    lbImg.style.cssText = 'max-width:96%;max-height:94%;object-fit:contain;border-radius:6px;' +
      'box-shadow:0 20px 60px rgba(0,0,0,.5);';
    lb.appendChild(lbImg);
    document.body.appendChild(lb);
    shots.forEach(function (img) {
      img.style.cursor = 'zoom-in';
      img.addEventListener('click', function () {
        lbImg.src = img.src;
        lb.style.display = 'flex';
      });
    });
    lb.addEventListener('click', function () { lb.style.display = 'none'; });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') lb.style.display = 'none';
    });
  }
})();
