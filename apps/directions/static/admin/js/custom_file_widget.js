console.log('✅ custom_file_widget.js загружен');

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWidget);
} else {
    setTimeout(initWidget, 500);
}

function initWidget() {
    console.log('🔍 Ищем поле файла...');
    
    var fileField = document.querySelector('input[type="file"][name="file"]');
    console.log(' fileField найден:', !!fileField);
    
    if (!fileField) {
        console.log('❌ Поле файла не найдено');
        return;
    }
    
    var parentRow = fileField.closest('.form-row');
    console.log('📋 parentRow найден:', !!parentRow);
    if (!parentRow) return;
    
    //  ВАЖНО: Скрываем ВСЕ стандартные элементы Django ДО создания нашей кнопки
    
    // 1. Находим и скрываем стандартный label (кнопка Django)
    var standardLabel = parentRow.querySelector('label[for="id_file"]');
    if (standardLabel) {
        standardLabel.remove();
        console.log('✅ Стандартный label удалён');
    }
    
    // 2. Скрываем стандартный input type="file"
    fileField.style.display = 'none';
    
    // 3. Находим и скрываем p.file-upload (стандартный блок Django)
    var existingFile = parentRow.querySelector('p.file-upload');
    if (existingFile) {
        // Сохраняем информацию о файле
        var fileLink = existingFile.querySelector('a');
        var fileName = fileLink ? fileLink.textContent : '';
        var fileUrl = fileLink ? fileLink.href : '';
        
        existingFile.remove();
        console.log('✅ Стандартный блок p.file-upload удалён');
        
        // 4. Скрываем чекбокс "Aniq" от Django
        var clearCheckbox = parentRow.querySelector('input[type="checkbox"]');
        if (clearCheckbox && clearCheckbox.parentElement) {
            clearCheckbox.parentElement.remove();
        }
        
        // 5. Создаём НАШ контейнер
        var newContainer = document.createElement('div');
        newContainer.style.cssText = 'display: flex !important; align-items: center !important; gap: 12px !important; flex-wrap: wrap !important; padding: 10px 0 !important;';
        
        // Информация о текущем файле
        var fileInfo = document.createElement('div');
        fileInfo.style.cssText = 'display: flex !important; align-items: center !important; gap: 6px !important;';
        if (fileUrl) {
            fileInfo.innerHTML = '<span style="color: #666; font-size: 13px;">Hozirda:</span>' +
                '<a href="' + fileUrl + '" target="_blank" style="color: #417690; text-decoration: none; font-size: 13px; font-weight: 500;">📄 ' + fileName.replace('programs/', '') + '</a>';
        } else {
            fileInfo.innerHTML = '<span style="color: #999; font-size: 13px;">Fayl yuklanmagan</span>';
        }
        
        // Чекбокс "Aniq"
        var checkboxLabel = document.createElement('label');
        checkboxLabel.style.cssText = 'display: flex !important; align-items: center !important; gap: 4px !important; cursor: pointer !important; user-select: none !important; margin-left: 8px !important;';
        checkboxLabel.innerHTML = '<input type="checkbox" name="file-clear" id="file-clear_id" style="margin: 0 !important;">' +
            '<span style="color: #dc3545; font-size: 12px;">Aniq</span>';
        
        // Кнопка
        var button = document.createElement('button');
        button.type = 'button';
        button.textContent = '📁 Faylni yangilash';
        button.style.cssText = 'background: #417690 !important; color: white !important; border: none !important; padding: 6px 14px !important; border-radius: 3px !important; cursor: pointer !important; font-size: 12px !important; font-weight: 500 !important; transition: all 0.2s !important; display: inline-flex !important; align-items: center !important; gap: 5px !important; white-space: nowrap !important; line-height: 1.2 !important; box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;';
        button.onmouseover = function() { 
            this.style.background = '#325b70'; 
            this.style.transform = 'translateY(-1px)'; 
            this.style.boxShadow = '0 2px 6px rgba(0,0,0,0.2)';
        };
        button.onmouseout = function() { 
            this.style.background = '#417690'; 
            this.style.transform = 'translateY(0)'; 
            this.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
        };
        button.onclick = function() {
            fileField.click();
        };
        
        // Текст "Yangi fayl tanlanmagan"
        var fileNameDisplay = document.createElement('span');
        fileNameDisplay.id = 'file-name-display';
        fileNameDisplay.style.cssText = 'color: #999 !important; font-size: 12px !important; font-style: italic !important; margin-left: 8px !important;';
        fileNameDisplay.textContent = 'Yangi fayl tanlanmagan';
        
        fileField.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                fileNameDisplay.innerHTML = '<span style="color: #417690; font-weight: bold;">✓</span> ' + this.files[0].name;
                fileNameDisplay.style.color = '#417690';
                fileNameDisplay.style.fontStyle = 'normal';
            } else {
                fileNameDisplay.textContent = 'Yangi fayl tanlanmagan';
                fileNameDisplay.style.color = '#999';
                fileNameDisplay.style.fontStyle = 'italic';
            }
        });
        
        // Собираем всё в одну строку
        newContainer.appendChild(fileInfo);
        newContainer.appendChild(checkboxLabel);
        newContainer.appendChild(button);
        newContainer.appendChild(fileNameDisplay);
        
        // Вставляем в родительский элемент
        var fieldDiv = parentRow.querySelector('.field-file > div');
        if (fieldDiv) {
            fieldDiv.appendChild(newContainer);
        } else {
            parentRow.querySelector('.field-file').appendChild(newContainer);
        }
        
        console.log('✅ Трансформация завершена!');
    }
}
