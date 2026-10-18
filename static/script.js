const dropZone = document.getElementById('drop-zone');
let selectedFiles = []; // глобальный массив

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, unhighlight, false);
});

function highlight() {
    dropZone.classList.add('drag-over');
}

function unhighlight() {
    dropZone.classList.remove('drag-over');
}

dropZone.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = Array.from(dt.files); // превращаем в обычный массив

    // Добавляем новые файлы к уже выбранным
    selectedFiles.push(...files);

    // Обновляем отображение
    updateFileList();
}

function uploadFiles(files) {
    const formData = new FormData();

    for (let i = 0; i < files.length; i++) {
        formData.append('shared_file', files[i]);
    }

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.redirected) {
            // Очищаем список перед перезагрузкой
            selectedFiles = [];
            window.location.href = response.url;
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Ошибка при отправке файлов');
    });
}

dropZone.addEventListener('click', () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = '*/*';
    input.onchange = (e) => {
        const files = Array.from(input.files);
        selectedFiles.push(...files);
        updateFileList();
    };
    input.click();
});

function updateFileList() {
    const container = document.getElementById('file-list-container');
    const listElement = document.getElementById('file-list');

    if (selectedFiles.length === 0) {
        container.style.display = 'none';
        return;
    }

    container.style.display = 'block';
    listElement.innerHTML = '';

    selectedFiles.forEach((file, index) => {
        const li = document.createElement('li');

        // Форматируем размер
        let sizeText = '';
        if (file.size < 1024) {
            sizeText = `${file.size} B`;
        } else if (file.size < 1024 * 1024) {
            sizeText = `${(file.size / 1024).toFixed(1)} KB`;
        } else {
            sizeText = `${(file.size / (1024 * 1024)).toFixed(1)} MB`;
        }

        li.textContent = `${file.name} (${sizeText})`;

        // Кнопка удаления
        const removeBtn = document.createElement('button');
        removeBtn.textContent = '✖';
        removeBtn.style.marginLeft = '10px';
        removeBtn.style.cursor = 'pointer';
        removeBtn.onclick = () => {
            selectedFiles.splice(index, 1);
            updateFileList();
        };

        li.appendChild(removeBtn);
        listElement.appendChild(li);
    });
}
document.getElementById('send-files-btn').addEventListener('click', () => {
    if (selectedFiles.length === 0) {
        alert('Нет выбранных файлов');
        return;
    }

    uploadFiles(selectedFiles);
});

document.getElementById('clear-files-btn').addEventListener('click', () => {
    selectedFiles = [];
    updateFileList();
});