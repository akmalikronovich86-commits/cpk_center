document.addEventListener('DOMContentLoaded', function() {
    // Находим кнопку "Добавить" в списке объектов
    var btn = document.querySelector('.object-tools a.addlink');
    if (btn && btn.textContent.includes("qo'shish")) {
        btn.textContent = "Avtorizatsiyadan o'tish";
    }
    // Также меняем заголовок страницы, если он содержит "qo'shish"
    var h1 = document.querySelector('h1');
    if (h1 && h1.textContent.includes("qo'shish")) {
        h1.textContent = h1.textContent.replace("qo'shish", "").trim();
    }
});
