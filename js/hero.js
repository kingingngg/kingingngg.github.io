/* 首页两个 Lottie：背景光波 + 头像的矢量遮罩，各自播一遍就停在末帧 */
(function () {
  'use strict';

  var heroAnim = document.getElementById('hero-anim');
  var avatar = document.getElementById('avatar');
  var avatarAnim = document.getElementById('avatar-lottie');

  if (!window.lottie || !heroAnim || !avatarAnim) {
    return;   // 没加载到播放器就保持静态头像
  }

  // 600×100 的光波；末帧所有图层 scale=0，播完那块就是干净的
  lottie.loadAnimation({
    container: heroAnim,
    renderer: 'svg',
    loop: false,
    autoplay: true,
    path: 'data/background.json'
  });

  // 100×100 的九角星遮罩，末帧是一个完整圆形；就绪后让下面的静态头像让位
  var mask = lottie.loadAnimation({
    container: avatarAnim,
    renderer: 'svg',
    loop: false,
    autoplay: true,
    path: 'data/avatar.json'
  });

  mask.addEventListener('DOMLoaded', function () {
    avatar.classList.add('is-live');
  });
})();
