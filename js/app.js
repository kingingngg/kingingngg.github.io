/* ============ 窄屏抽屉式侧边栏 ============ */
(function () {
  const hamburger = document.getElementById('hamburger');
  const sidebar = document.getElementById('sidebar');
  const scrim = document.getElementById('scrim');

  // 打开抽屉时记录当前滚动位置，避免紧接着的 scroll 事件立刻把它收起
  let scrollStartY = 0;

  function openSidebar() {
    scrollStartY = window.scrollY;
    sidebar.classList.add('is-open');
    scrim.classList.add('is-visible');
    hamburger.classList.add('is-hidden');      // 隐藏汉堡按钮，只保留点空白关闭
    hamburger.setAttribute('aria-expanded', 'true');
  }

  function closeSidebar() {
    sidebar.classList.remove('is-open');
    scrim.classList.remove('is-visible');
    hamburger.classList.remove('is-hidden');
    hamburger.setAttribute('aria-expanded', 'false');
  }

  function isOpen() {
    return sidebar.classList.contains('is-open');
  }

  hamburger.addEventListener('click', openSidebar);
  scrim.addEventListener('click', closeSidebar);

  // Esc 关闭
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && isOpen()) {
      closeSidebar();
    }
  });

  // 向下滚动主体页面时收起侧边栏
  window.addEventListener('scroll', function () {
    if (!isOpen()) return;
    // 向下滚动（scrollY 增大）时收起
    if (window.scrollY > scrollStartY + 4) {
      closeSidebar();
    }
    scrollStartY = window.scrollY;
  }, { passive: true });

  // 视口变宽时自动收起抽屉，避免状态残留
  window.addEventListener('resize', function () {
    if (window.innerWidth > 720 && isOpen()) {
      closeSidebar();
    }
  });
})();
/* ============ 页面切换逻辑 ============ */
document.querySelectorAll('.nav-item').forEach(btn => {
  btn.addEventListener('click', function() {
    // 1. 获取要显示的页面 ID
    const targetId = this.getAttribute('data-target');
    
    // 2. 目标页面不存在（还没做这个页面）就保持当前页面不动
    const targetPage = document.getElementById('page-' + targetId);
    if (!targetPage) return;

    // 3. 切换显示：先全部隐藏，再打开目标页
    document.querySelectorAll('.page-section').forEach(page => {
      page.hidden = true;
    });
    targetPage.hidden = false;

    // 4. 切换按钮高亮状态
    document.querySelectorAll('.nav-item').forEach(nav => {
      nav.classList.remove('is-active');
      nav.removeAttribute('aria-current'); 
    });
    this.classList.add('is-active');
    this.setAttribute('aria-current', 'page'); 

    // 5. 窄屏下点击后自动关闭抽屉
    if (window.innerWidth <= 720) {
      document.getElementById('scrim').click(); 
    }
  });
});