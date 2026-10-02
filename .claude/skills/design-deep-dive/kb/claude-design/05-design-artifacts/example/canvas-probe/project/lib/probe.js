// Файл поддержки холста-пробы: показывает, что холст отдаёт файл скрипта и исполняет его из <head> артборда.
(function (root) {
  'use strict';
  root.CanvasProbe = {
    version: '1',
    // Волна на canvas 2D: w, h — размер рисунка, t — секунды от старта.
    wave: function (ctx, w, h, t) {
      ctx.clearRect(0, 0, w, h);
      ctx.strokeStyle = '#e0a458';
      ctx.lineWidth = 2;
      ctx.beginPath();
      for (var x = 0; x <= w; x += 4) {
        var y = h / 2 + Math.sin(x / 24 + t * 3) * (h * 0.3);
        if (x === 0) { ctx.moveTo(x, y); } else { ctx.lineTo(x, y); }
      }
      ctx.stroke();
    },
  };
})(typeof globalThis !== 'undefined' ? globalThis : window);
