// Ждём загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    // Находим поле файла
    var fileField = document.querySelector('input[type="file"][name="file"]');
    if (!fileField) return;
    
    // Находим родительский div с классом form-row
    var parentRow = fileField.closest('.form-row');
    if (!parentRow) return;
    
    // Находим существующий текст "Hozirda" и чекбокс
    var existingFile = parentRow.querySelector('p.file-upload');
    var clearCheckbox = parentRow.querySelector('input[type="checkbox"]');
    
    if (existingFile) {
        // Создаём новую структуру
        var newContainer = document.createElement('div');
        newContainer.style.cssText = 'display: flex; align-items: center; gap: 12px; flex-wrap: wrap; padding: 8px 0;';
        
        // Получаем информацию о текущем файле
        var fileLink = existingFile.querySelector('a');
        var fileName = fileLink ? fileLink.textContent : '';
        var fileUrl = fileLink ? fileLink.href : '';
        
        // Текущий файл
        var fileInfo = document.createElement('div');
        fileInfo.style.cssText = 'display: flex; align-items: center; gap: 6px;';
        fileInfo.innerHTML = '<span style="color: #666; font-size: 13px;">Hozirda:</span>' +
            '<a href="' + fileUrl + '" target="_blank" style="color: #417690; text-decoration: none; font-size: 13px; font-weight: 500;">📄 ' + fileName.replace('programs/', '') + '</a>';
        
        // Чекбокс "Aniq"
        var checkboxLabel = document.createElement('label');
        checkboxLabel.style.cssText = 'display: flex; align-items: center; gap: 4px; cursor: pointer; user-select: none; margin-left: 8px;';
        checkboxLabel.innerHTML = '<input type="checkbox" name="file-clear" id="file-clear_id" style="margin: 0;">' +
            '<span style="color: #dc3545; font-size: 12px;">Aniq</span>';
        
        // Кнопка
        var button = document.createElement('button');
        button.type = 'button';
        button.textContent = '📁 Faylni yangilash';
        button.style.cssText = 'background: #417690; color: white; border: none; padding: 5px 12px; border-radius: 3px; cursor: pointer; font-size: 12px; font-weight: 500; transition: all 0.2s; display: inline-flex; align-items: center; gap: 5px; white-space: nowrap;';
        button.onmouseover = function() { 
            this.style.background = '#325b70'; 
            this.style.transform = 'translateY(-1px)'; 
        };
        button.onmouseout = function() { 
            this.style.background = '#417690'; 
            this.style.transform = 'translateY(0)'; 
        };
        button.onclick = function() {
            fileField.click();
        };
        
        // Скрываем стандартный input file
        fileField.style.display = 'none';
        
        // Отображение выбранного файла
        var fileNameDisplay = document.createElement('div');
        fileNameDisplay.id = 'file-name-display';
        fileNameDisplay.style.cssText = 'width: 100%; margin-top: 8px; color: #666; font-size: 12px; font-style: italic; padding-left: 4px;';
        fileNameDisplay.textContent = 'Yangi fayl tanlanmagan';
        
        // Обработчик выбора файла
        fileField.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                fileNameDisplay.innerHTML = '<span style="color: #417690; font-weight: bold;">✓ Tanlangan:</span> ' + this.files[0].name;
            } else {
                fileNameDisplay.textContent = 'Yangi fayl tanlanmagan';
                fileNameDisplay.style.color = '#666';
            }
        });
        
        // Собираем всё вместе
        newContainer.appendChild(fileInfo);
        newContainer.appendChild(checkboxLabel);
        newContainer.appendChild(button);
        
        // Заменяем существующий контент
        existingFile.style.display = 'none';
        if (clearCheckbox && clearCheckbox.parentElement) {
            clearCheckbox.parentElement.style.display = 'none';
        }
        
        // Вставляем после скрытого input
        fileField.parentNode.insertBefore(newContainer, fileField.nextSibling);
        fileField.parentNode.insertBefore(fileNameDisplay, newContainer.nextSibling);
    }
});
