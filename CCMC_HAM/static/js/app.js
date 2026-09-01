// CCMC Hamilton 教会管理系统 - 通用脚本
document.addEventListener('DOMContentLoaded', function () {
    // 自动关闭提示
    document.querySelectorAll('.alert-dismissible').forEach(function (el) {
        setTimeout(function () {
            var btn = el.querySelector('.btn-close');
            if (btn) btn.click();
        }, 6000);
    });
});

